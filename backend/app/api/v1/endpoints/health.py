"""
Health Check API Endpoints

Enhanced health monitoring endpoints for detailed service status reporting.
"""

from fastapi import APIRouter
from datetime import UTC, datetime
import structlog

from app.utils.monitoring import health_checker, metrics_collector

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/detailed")
async def detailed_health():
    """
    Detailed health check with comprehensive service monitoring.
    
    Returns detailed status of all services including:
    - Database connectivity
    - Redis connectivity  
    - LLM provider status
    - System resources
    - Application metrics
    """
    try:
        health_status = await health_checker.comprehensive_health_check()
        
        # Add application metrics
        health_status["metrics"] = {
            "requests_count": metrics_collector.get_metrics().get("total_requests", 0),
            "error_rate": metrics_collector.get_metrics().get("error_rate", 0),
            "average_response_time": metrics_collector.get_metrics().get("avg_response_time", 0)
        }
        
        return health_status
        
    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "error": str(e)
        }


@router.get("/services")
async def services_health():
    """
    Service-specific health checks.
    
    Returns the status of individual services for monitoring dashboards.
    """
    try:
        # Get individual service checks
        health_status = await health_checker.comprehensive_health_check()
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "services": health_status.get("checks", {})
        }
        
    except Exception as e:
        logger.error("Services health check failed", error=str(e))
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "error": str(e),
            "services": {}
        }


@router.get("/providers")
async def llm_providers_health():
    """
    LLM provider specific health check.
    
    Returns detailed status of all configured LLM providers.
    """
    try:
        provider_status = await health_checker.check_llm_providers()
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "llm_providers": provider_status
        }
        
    except Exception as e:
        logger.error("LLM providers health check failed", error=str(e))
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "error": str(e),
            "llm_providers": {
                "status": "error",
                "error": str(e)
            }
        }