"""
API Router Configuration for Z2 Backend

This module sets up the main API router and includes all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    a2a,
    activity,
    agents,
    api_keys,
    auth,
    consent,
    debug,
    health,
    heavy_analysis,
    mcp,
    memory_graph,
    models,
    quantum,
    users,
    workflows,
)
from app.core.config import settings

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(memory_graph.router, prefix="/memory-graph", tags=["memory-graph"])
api_router.include_router(health.router, tags=["health", "monitoring"])
api_router.include_router(heavy_analysis.router, tags=["heavy-analysis"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(consent.router, prefix="/consent", tags=["consent"])
api_router.include_router(a2a.router, prefix="/a2a", tags=["a2a"])
api_router.include_router(activity.router, prefix="/activity", tags=["activity", "monitoring"])
api_router.include_router(quantum.router, prefix="/multi-agent-system/quantum", tags=["quantum"])

# Include debug endpoints only in development or when explicitly enabled
if settings.debug or settings.log_level.lower() == "debug":
    api_router.include_router(debug.router, prefix="/debug", tags=["debug"])
