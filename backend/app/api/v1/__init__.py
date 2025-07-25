"""
API Router Configuration for Z2 Backend

This module sets up the main API router and includes all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, agents, workflows, models


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(models.router, prefix="/models", tags=["models"])