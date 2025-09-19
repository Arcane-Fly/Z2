"""
Z2 Backend Main Application Module

This is the entry point for the Z2 FastAPI application. It sets up the FastAPI
instance, configures middleware, includes routers, and handles application lifecycle.
"""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import Response

from app.api.v1 import api_router
from app.core.config import settings
from app.core.security import SecurityHeaders
from app.database.session import init_db
from app.utils.monitoring import (
    health_checker,
    initialize_monitoring,
    metrics_collector,
    CONTENT_TYPE_LATEST,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting Z2 Backend API", version=settings.app_version)

    # Initialize monitoring and observability
    initialize_monitoring()

    # Verify database connection (migrations handled by Alembic in startup command)
    try:
        from app.database.session import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        # In production, we want the app to start even if DB is temporarily unavailable
        # The health check will catch this

    yield

    logger.info("Shutting down Z2 Backend API")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Z2 AI Workforce Platform - Dynamic Multi-Agent Orchestration",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Configure CORS with enhanced security
    if settings.debug:
        # Development - more permissive
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # Production - restrictive CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,  # Should be specific domains in production
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=[
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "X-CSRFToken"
            ],
            expose_headers=["X-Total-Count", "X-Page-Count"],
            max_age=600,  # Cache preflight requests for 10 minutes
        )

    # Configure trusted hosts with environment-specific settings
    if settings.is_production:
        # Production - strict host validation
        allowed_hosts = [host for host in settings.allowed_hosts if host != "*"]
        if allowed_hosts:
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=allowed_hosts,
            )
    else:
        # Development - allow all hosts
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )

    # Add security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)

        # Add security headers
        security_headers = SecurityHeaders.get_security_headers()
        for header, value in security_headers.items():
            response.headers[header] = value

        # Add HSTS only in production with HTTPS
        if settings.is_production and request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response

    # Add metrics collection middleware
    @app.middleware("http")
    async def collect_metrics(request, call_next):
        start_time = time.time()

        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record metrics
        metrics_collector.record_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration=duration
        )

        # Add response time header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        return response

    # Include API router
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/.well-known/agent.json")
    async def agent_discovery():
        """A2A protocol agent discovery endpoint."""
        import json
        import os
        from pathlib import Path

        try:
            # Load agent.json from .well-known directory
            agent_json_path = (
                Path(__file__).parent.parent.parent / ".well-known" / "agent.json"
            )

            if not agent_json_path.exists():
                return {
                    "error": "Agent configuration not found",
                    "status": "unavailable",
                }

            with open(agent_json_path) as f:
                agent_config = json.load(f)

            # Replace environment variables in the config
            agent_str = json.dumps(agent_config)
            # Replace Railway environment variables
            railway_public_domain = os.getenv(
                "RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000"
            )
            agent_str = agent_str.replace(
                "${RAILWAY_PUBLIC_DOMAIN:-http://localhost:8000}", railway_public_domain
            )

            node_env = os.getenv("NODE_ENV", "development")
            agent_str = agent_str.replace("${NODE_ENV:-development}", node_env)

            return json.loads(agent_str)

        except Exception as e:
            logger.error("Failed to load agent configuration", error=str(e))
            return {
                "error": "Failed to load agent configuration",
                "status": "error",
                "details": str(e),
            }

    @app.get("/health")
    async def health_check():
        """Enhanced health check endpoint for Railway and monitoring."""
        try:
            # Use comprehensive health checker
            health_status = await health_checker.comprehensive_health_check()

            # Return appropriate HTTP status based on health
            status_code = 200
            if health_status["status"] == "degraded":
                status_code = 200  # Still accept traffic but log warning
                logger.warning("Service degraded", unhealthy_services=health_status.get("unhealthy_services"))
            elif health_status["status"] == "unhealthy":
                status_code = 503  # Service unavailable
                logger.error("Service unhealthy", error=health_status.get("error"))

            return health_status

        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "app": settings.app_name,
                "version": settings.app_version,
                "timestamp": datetime.now(UTC).isoformat(),
                "error": str(e),
            }

    @app.get("/health/live")
    async def liveness_probe():
        """Kubernetes liveness probe - checks if the application is running."""
        try:
            # Simple check that the application is responsive
            # Don't check external dependencies for liveness
            return {
                "status": "alive",
                "timestamp": datetime.now(UTC).isoformat(),
                "app": settings.app_name,
                "version": settings.app_version,
                "uptime_seconds": round(time.time() - health_checker.start_time, 2)
            }
        except Exception as e:
            logger.error("Liveness probe failed", error=str(e))
            return Response(status_code=503, content="Service not alive")

    @app.get("/health/ready")
    async def readiness_probe():
        """Kubernetes readiness probe - checks if the application is ready to serve traffic."""
        try:
            # Check essential dependencies for readiness
            health_status = await health_checker.comprehensive_health_check()
            
            # For readiness, we're more strict about dependencies
            if health_status["status"] == "unhealthy":
                return Response(status_code=503, content="Service not ready")
            
            return {
                "status": "ready",
                "timestamp": datetime.now(UTC).isoformat(),
                "app": settings.app_name,
                "version": settings.app_version,
                "checks": health_status.get("checks", {})
            }
        except Exception as e:
            logger.error("Readiness probe failed", error=str(e))
            return Response(status_code=503, content="Service not ready")

    @app.get("/metrics")
    async def get_prometheus_metrics():
        """Get Prometheus metrics."""
        try:
            metrics_data = metrics_collector.get_prometheus_metrics()
            return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
        except Exception as e:
            logger.error("Prometheus metrics collection failed", error=str(e))
            return Response(content=b"", media_type=CONTENT_TYPE_LATEST, status_code=500)

    @app.get("/metrics/json")
    async def get_json_metrics():
        """Get application metrics in JSON format for monitoring."""
        try:
            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "app": settings.app_name,
                "version": settings.app_version,
                "metrics": metrics_collector.get_metrics()
            }
        except Exception as e:
            logger.error("JSON metrics collection failed", error=str(e))
            return {"error": str(e)}

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Z2 AI Workforce Platform API",
            "version": settings.app_version,
            "docs": "/docs"
            if settings.debug
            else "API documentation disabled in production",
        }

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
