"""
Authentication endpoints for Z2 API.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import PasswordSecurity, UserCredentials, auth_service
from app.database.session import get_db
from app.models.user import User
from app.schemas import (
    BaseResponse,
    TokenResponse,
    UserLogin,
    UserProfile,
    UserRegister,
)

router = APIRouter()
security = HTTPBearer()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[dict]:
    """Get user by username from database."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type,
            "is_active": user.is_active,
            "password_hash": user.hashed_password,
            "permissions": []  # TODO: implement permissions
        }
    return None


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[dict]:
    """Get user by ID from database."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type,
            "is_active": user.is_active,
            "password_hash": user.hashed_password,
            "permissions": []  # TODO: implement permissions
        }
    return None


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user and return access token."""
    # Check if user already exists
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength
    password_validation = PasswordSecurity.validate_password_strength(user_data.password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
        )

    # Hash password
    hashed_password = PasswordSecurity.get_password_hash(user_data.password)

    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        user_type=user_data.user_type,
        is_active=True,
        is_superuser=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create and return token
    from app.core.security import jwt_manager
    token = jwt_manager.create_token_pair(
        user_id=str(new_user.id),
        username=new_user.username,
        user_type=new_user.user_type,
        permissions=[]
    )

    return TokenResponse(
        access_token=token.access_token,
        token_type=token.token_type,
        expires_in=token.expires_in
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return access token."""
    user_creds = UserCredentials(
        username=credentials.username,
        password=credentials.password,
        remember_me=False
    )

    # Authenticate user
    token = await auth_service.authenticate_user(
        credentials=user_creds,
        get_user_func=lambda username: get_user_by_username(db, username),
        request=request
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

    return TokenResponse(
        access_token=token.access_token,
        token_type=token.token_type,
        expires_in=token.expires_in
    )


@router.post("/logout", response_model=BaseResponse)
async def logout(
    db: AsyncSession = Depends(get_db),
):
    """Logout user and invalidate token."""
    # TODO: Implement token blacklisting/invalidation
    return BaseResponse(message="Logged out successfully")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token."""
    # TODO: Implement token refresh logic with refresh tokens
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials = Depends(security)
):
    """Get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user = await auth_service.get_current_user(
        credentials=credentials,
        get_user_func=lambda username: get_user_by_username(db, username)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return UserProfile(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        user_type=user["user_type"],
        is_active=user["is_active"],
        created_at=user.get("created_at"),
        last_login=user.get("last_login")
    )
