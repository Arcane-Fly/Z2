"""
Z2 Backend Main Application Module

This is the entry point for the Z2 FastAPI application. It sets up the FastAPI
instance, configures middleware, includes routers, and handles application lifecycle.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.database.session import init_db


logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting Z2 Backend API", version=settings.app_version)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
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

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure trusted hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

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
            agent_json_path = Path(__file__).parent.parent.parent / ".well-known" / "agent.json"
            
            if not agent_json_path.exists():
                return {
                    "error": "Agent configuration not found",
                    "status": "unavailable"
                }
            
            with open(agent_json_path, 'r') as f:
                agent_config = json.load(f)
            
            # Replace environment variables in the config
            agent_str = json.dumps(agent_config)
            # Replace Railway environment variables
            railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000")
            agent_str = agent_str.replace("${RAILWAY_PUBLIC_DOMAIN:-http://localhost:8000}", railway_public_domain)
            
            node_env = os.getenv("NODE_ENV", "development")
            agent_str = agent_str.replace("${NODE_ENV:-development}", node_env)
            
            return json.loads(agent_str)
            
        except Exception as e:
            logger.error("Failed to load agent configuration", error=str(e))
            return {
                "error": "Failed to load agent configuration",
                "status": "error",
                "details": str(e)
            }

    @app.get("/health")
    async def health_check():
        """Enhanced health check endpoint for Railway."""
        try:
            # Basic health indicators
            health_status = {
                "status": "healthy",
                "app": settings.app_name,
                "version": settings.app_version,
                "timestamp": datetime.utcnow().isoformat(),
                "environment": "production" if settings.is_production else "development",
                "checks": {
                    "api": "ok",
                    "database": "unknown",  # TODO: Add database health check
                    "redis": "unknown",     # TODO: Add redis health check
                    "llm_providers": "unknown"  # TODO: Add LLM provider health checks
                }
            }
            
            return health_status
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy", 
                "app": settings.app_name,
                "version": settings.app_version,
                "error": str(e)
            }

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Z2 AI Workforce Platform API",
            "version": settings.app_version,
            "docs": "/docs" if settings.debug else "API documentation disabled in production",
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