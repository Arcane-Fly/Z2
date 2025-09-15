"""
Monitoring and Observability Module for Z2

Provides Sentry integration, health checks, and monitoring utilities
for production observability and error tracking.
"""

import asyncio
import os
import time
from datetime import UTC, datetime
from typing import Any, Optional

import psutil
import sentry_sdk
import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings

logger = structlog.get_logger(__name__)


class SentryConfig:
    """Sentry configuration and initialization."""

    def __init__(self):
        self.dsn = os.getenv("SENTRY_DSN")
        self.environment = "production" if settings.is_production else "development"
        self.release = f"z2@{settings.app_version}"
        self.sample_rate = 1.0 if not settings.is_production else 0.1
        self.traces_sample_rate = 1.0 if not settings.is_production else 0.1

    def initialize(self):
        """Initialize Sentry SDK with Z2-specific configuration."""
        if not self.dsn:
            logger.warning("Sentry DSN not configured, error tracking disabled")
            return

        try:
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                release=self.release,
                sample_rate=self.sample_rate,
                traces_sample_rate=self.traces_sample_rate,
                integrations=[
                    FastApiIntegration(auto_enabling_integrations=True),
                    RedisIntegration(),
                    SqlalchemyIntegration(),
                    AsyncioIntegration(),
                ],
                # Custom tags for Z2
                default_integrations=True,
                debug=not settings.is_production,
                attach_stacktrace=True,
                send_default_pii=False,  # Don't send PII for privacy
                max_breadcrumbs=50,
                before_send=self._before_send_filter,
            )

            # Set user context
            sentry_sdk.set_tag("service", "z2-backend")
            sentry_sdk.set_tag("version", settings.app_version)

            logger.info("Sentry initialized successfully",
                       environment=self.environment,
                       release=self.release)

        except Exception as e:
            logger.error("Failed to initialize Sentry", error=str(e))

    def _before_send_filter(self, event: dict[str, Any], hint: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Filter and modify events before sending to Sentry."""
        # Don't send health check errors
        if event.get('transaction') == '/health':
            return None

        # Filter out sensitive data
        if 'request' in event:
            headers = event['request'].get('headers', {})
            # Remove authorization headers
            headers.pop('authorization', None)
            headers.pop('cookie', None)

        return event


class HealthChecker:
    """Comprehensive health checking for Z2 services."""

    def __init__(self):
        self.start_time = time.time()

    async def check_database(self) -> dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            from app.database.session import SessionLocal
            from sqlalchemy import text

            start_time = time.time()
            async with SessionLocal() as session:
                # Simple query to test connectivity
                result = await session.execute(text("SELECT 1 as test"))
                result.fetchone()  # Remove await here since fetchone() is not async

            duration = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "connection": "ok"
            }

        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection": "failed"
            }

    async def check_redis(self) -> dict[str, Any]:
        """Check Redis connectivity and performance."""
        try:
            import redis.asyncio as redis

            redis_client = redis.from_url(settings.redis_url)

            start_time = time.time()
            await redis_client.ping()
            duration = time.time() - start_time

            # Get some basic info
            info = await redis_client.info()
            await redis_client.close()

            return {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "version": info.get("redis_version", "unknown"),
                "memory_usage": info.get("used_memory_human", "unknown")
            }

        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def check_llm_providers(self) -> dict[str, Any]:
        """Check LLM provider API availability."""
        providers = {}
        any_providers_configured = False

        # Check OpenAI
        if settings.openai_api_key:
            any_providers_configured = True
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

                start_time = time.time()
                models = await client.models.list()
                duration = time.time() - start_time

                providers["openai"] = {
                    "status": "healthy",
                    "response_time_ms": round(duration * 1000, 2),
                    "models_count": len(models.data)
                }
            except Exception as e:
                providers["openai"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        else:
            providers["openai"] = {
                "status": "not_configured",
                "error": "API key not configured"
            }

        # Check Anthropic
        if settings.anthropic_api_key:
            any_providers_configured = True
            try:
                import anthropic
                client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

                start_time = time.time()
                # Simple message to test connectivity with minimal tokens
                await client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1,
                    messages=[{"role": "user", "content": "test"}]
                )
                duration = time.time() - start_time

                providers["anthropic"] = {
                    "status": "healthy",
                    "response_time_ms": round(duration * 1000, 2)
                }
            except Exception as e:
                providers["anthropic"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        else:
            providers["anthropic"] = {
                "status": "not_configured",
                "error": "API key not configured"
            }

        # Check Groq
        if settings.groq_api_key:
            any_providers_configured = True
            try:
                import groq
                client = groq.AsyncGroq(api_key=settings.groq_api_key)

                start_time = time.time()
                models = await client.models.list()
                duration = time.time() - start_time

                providers["groq"] = {
                    "status": "healthy",
                    "response_time_ms": round(duration * 1000, 2),
                    "models_count": len(models.data)
                }
            except Exception as e:
                providers["groq"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        else:
            providers["groq"] = {
                "status": "not_configured",
                "error": "API key not configured"
            }

        # Overall status for LLM providers
        if not any_providers_configured:
            return {
                "status": "degraded",
                "message": "No LLM providers configured",
                "providers": providers
            }

        # If any provider is healthy, consider the service operational but potentially degraded
        healthy_count = sum(1 for p in providers.values() if p.get("status") == "healthy")
        total_configured = sum(1 for p in providers.values() if p.get("status") != "not_configured")
        
        if healthy_count > 0:
            status = "healthy" if healthy_count == total_configured else "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "healthy_providers": healthy_count,
            "total_configured": total_configured,
            "providers": providers
        }

    def check_system_resources(self) -> dict[str, Any]:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage('/')

            # Load average (Unix only)
            load_avg = None
            try:
                load_avg = os.getloadavg()
            except (OSError, AttributeError):
                pass  # Windows doesn't have getloadavg

            return {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "used": disk.used,
                    "percent": round((disk.used / disk.total) * 100, 1)
                },
                "load_average": load_avg
            }

        except Exception as e:
            logger.error("System resource check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def comprehensive_health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check of all services."""
        uptime = time.time() - self.start_time

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "app": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": "production" if settings.is_production else "development",
                "uptime_seconds": round(uptime, 2)
            },
            "checks": {}
        }

        # Run all health checks concurrently
        try:
            database_check, redis_check, system_check = await asyncio.gather(
                self.check_database(),
                self.check_redis(),
                asyncio.to_thread(self.check_system_resources),
                return_exceptions=True
            )

            # LLM providers check (can be slow, so timeout)
            try:
                llm_check = await asyncio.wait_for(
                    self.check_llm_providers(),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                llm_check = {"status": "timeout", "error": "Health check timed out"}

            health_status["checks"] = {
                "database": database_check if not isinstance(database_check, Exception) else {
                    "status": "error", "error": str(database_check)
                },
                "redis": redis_check if not isinstance(redis_check, Exception) else {
                    "status": "error", "error": str(redis_check)
                },
                "system": system_check if not isinstance(system_check, Exception) else {
                    "status": "error", "error": str(system_check)
                },
                "llm_providers": llm_check
            }

            # Determine overall health status
            unhealthy_checks = [
                name for name, check in health_status["checks"].items()
                if check.get("status") == "unhealthy"
            ]

            degraded_checks = [
                name for name, check in health_status["checks"].items()
                if check.get("status") == "degraded"
            ]

            if unhealthy_checks:
                # Critical services failing (database, redis) should mark as unhealthy
                critical_unhealthy = [name for name in unhealthy_checks if name in ["database", "redis"]]
                if critical_unhealthy:
                    health_status["status"] = "unhealthy"
                    health_status["unhealthy_services"] = unhealthy_checks
                else:
                    # Non-critical services (like LLM providers) only cause degraded status
                    health_status["status"] = "degraded"
                    health_status["unhealthy_services"] = unhealthy_checks
            elif degraded_checks:
                health_status["status"] = "degraded" 
                health_status["degraded_services"] = degraded_checks

        except Exception as e:
            logger.error("Health check failed", error=str(e))
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status


class MetricsCollector:
    """Collect and expose metrics for monitoring."""

    def __init__(self):
        # Legacy collections for JSON endpoint
        self.request_counts = {}
        self.response_times = {}
        self.error_counts = {}
        
        # Prometheus metrics
        self.http_requests_total = Counter(
            'z2_http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'z2_http_request_duration_seconds',
            'HTTP request latency',
            ['method', 'endpoint']
        )
        
        self.http_requests_in_progress = Gauge(
            'z2_http_requests_in_progress',
            'Number of HTTP requests currently being processed'
        )
        
        self.model_requests_total = Counter(
            'z2_model_requests_total',
            'Total number of LLM model requests',
            ['provider', 'model', 'status']
        )
        
        self.model_request_duration = Histogram(
            'z2_model_request_duration_seconds',
            'Model request latency',
            ['provider', 'model']
        )
        
        self.active_agents = Gauge(
            'z2_active_agents',
            'Number of currently active agents'
        )
        
        self.workflow_executions_total = Counter(
            'z2_workflow_executions_total',
            'Total number of workflow executions',
            ['status']
        )
        
        self.database_connections = Gauge(
            'z2_database_connections',
            'Number of active database connections'
        )
        
        self.redis_operations_total = Counter(
            'z2_redis_operations_total',
            'Total Redis operations',
            ['operation', 'status']
        )

    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record request metrics."""
        # Legacy metrics
        key = f"{method}_{endpoint}"

        # Count requests
        if key not in self.request_counts:
            self.request_counts[key] = 0
        self.request_counts[key] += 1

        # Track response times
        if key not in self.response_times:
            self.response_times[key] = []
        self.response_times[key].append(duration)

        # Count errors
        if status_code >= 400:
            if key not in self.error_counts:
                self.error_counts[key] = 0
            self.error_counts[key] += 1
        
        # Prometheus metrics
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def record_model_request(self, provider: str, model: str, status: str, duration: float):
        """Record LLM model request metrics."""
        self.model_requests_total.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        if status == "success":
            self.model_request_duration.labels(
                provider=provider,
                model=model
            ).observe(duration)

    def set_active_agents(self, count: int):
        """Set the number of active agents."""
        self.active_agents.set(count)

    def record_workflow_execution(self, status: str):
        """Record workflow execution."""
        self.workflow_executions_total.labels(status=status).inc()

    def set_database_connections(self, count: int):
        """Set database connection count."""
        self.database_connections.set(count)

    def record_redis_operation(self, operation: str, status: str):
        """Record Redis operation."""
        self.redis_operations_total.labels(
            operation=operation,
            status=status
        ).inc()

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        return {
            "request_counts": self.request_counts.copy(),
            "response_times": {
                endpoint: {
                    "count": len(times),
                    "avg": sum(times) / len(times) if times else 0,
                    "min": min(times) if times else 0,
                    "max": max(times) if times else 0
                }
                for endpoint, times in self.response_times.items()
            },
            "error_counts": self.error_counts.copy()
        }
    
    def get_prometheus_metrics(self) -> bytes:
        """Get metrics in Prometheus format."""
        return generate_latest()


class PerformanceMetrics:
    """Simple performance metrics tracking."""
    
    def __init__(self):
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
        self.response_times = []
        self.memory_usage = []
        
    def add_request(self, response_time: float, is_error: bool = False):
        """Add a request to the metrics."""
        self.request_count += 1
        self.total_response_time += response_time
        self.response_times.append(response_time)
        
        if is_error:
            self.error_count += 1
            
    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
        
    @property 
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100


def format_performance_summary(metrics: PerformanceMetrics) -> str:
    """Format performance metrics into a summary string."""
    return f"""Performance Summary:
- Requests: {metrics.request_count}
- Average Response Time: {metrics.average_response_time:.3f}s
- Error Rate: {metrics.error_rate:.2f}%
- Total Errors: {metrics.error_count}"""


def get_system_metrics() -> dict:
    """Get current system metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available_gb": psutil.virtual_memory().available / (1024**3),
        "disk_percent": psutil.disk_usage('/').percent,
        "disk_free_gb": psutil.disk_usage('/').free / (1024**3),
    }


# Global instances
sentry_config = SentryConfig()
health_checker = HealthChecker()
metrics_collector = MetricsCollector()


def initialize_monitoring():
    """Initialize all monitoring and observability features."""
    sentry_config.initialize()
    logger.info("Monitoring initialized",
                sentry_enabled=bool(sentry_config.dsn),
                environment=sentry_config.environment)
