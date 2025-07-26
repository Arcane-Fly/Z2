"""
User management endpoints for Z2 API.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas import BaseResponse, PaginatedResponse, UserProfile

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by username, email, or full name"),
    user_type: Optional[str] = Query(None, description="Filter by user type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
):
    """List all users with filtering and pagination."""

    # Build query
    query = select(User)

    # Apply filters
    conditions = []
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        )

    if user_type:
        conditions.append(User.user_type == user_type)

    if is_active is not None:
        conditions.append(User.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count(User.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    query = query.order_by(User.created_at.desc())

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Convert to response format
    user_profiles = []
    for user in users:
        user_profiles.append(UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            user_type=user.user_type,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        ))

    pages = (total + limit - 1) // limit

    return PaginatedResponse(
        success=True,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        data=user_profiles
    )


@router.post("/", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def create_user(
    # This endpoint is handled by /auth/register
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Use /auth/register endpoint to create new users"
    )


@router.get("/{user_id}", response_model=UserProfile)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        user_type=user.user_type,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.put("/{user_id}", response_model=UserProfile)
async def update_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Update user by ID."""
    # TODO: Implement user update with validation and authorization
    # For now, return not implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User update not yet implemented"
    )


@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete user by ID."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete by deactivating the user
    user.is_active = False
    await db.commit()

    return BaseResponse(
        success=True,
        message=f"User {user.username} has been deactivated"
    )
