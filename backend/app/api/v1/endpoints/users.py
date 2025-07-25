"""
User management endpoints for Z2 API.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db


router = APIRouter()


@router.get("/")
async def list_users(
    db: AsyncSession = Depends(get_db),
):
    """List all users."""
    # TODO: Implement user listing
    return {"message": "List users endpoint - TODO: Implement user listing"}


@router.post("/")
async def create_user(
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    # TODO: Implement user creation
    return {"message": "Create user endpoint - TODO: Implement user creation"}


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID."""
    # TODO: Implement user retrieval
    return {"message": f"Get user {user_id} endpoint - TODO: Implement user retrieval"}


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Update user by ID."""
    # TODO: Implement user update
    return {"message": f"Update user {user_id} endpoint - TODO: Implement user update"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete user by ID."""
    # TODO: Implement user deletion
    return {"message": f"Delete user {user_id} endpoint - TODO: Implement user deletion"}