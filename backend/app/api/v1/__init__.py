"""
API Router Configuration for Z2 Backend

This module sets up the main API router and includes all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    a2a,
    agents,
    auth,
    consent,
    debug,
    mcp,
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
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(consent.router, prefix="/consent", tags=["consent"])
api_router.include_router(a2a.router, prefix="/a2a", tags=["a2a"])
api_router.include_router(quantum.router, prefix="/multi-agent-system/quantum", tags=["quantum"])

# Include debug endpoints only in development or when explicitly enabled
if settings.debug or settings.log_level.lower() == "debug":
    api_router.include_router(debug.router, prefix="/debug", tags=["debug"])
