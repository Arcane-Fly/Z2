"""
Authentication endpoints for Z2 API.
"""

from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import PasswordSecurity, UserCredentials, auth_service, jwt_manager
from app.core.auth_dependencies import get_current_user, get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.models.role import Role, RefreshToken
from app.schemas import (
    BaseResponse,
    TokenResponse,
    UserLogin,
    UserProfile,
    UserRegister,
)

router = APIRouter()
security = HTTPBearer()


async def get_user_by_username_with_roles(db: AsyncSession, username: str) -> Optional[dict]:
    """Get user by username from database with roles and permissions."""
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.username == username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # Get user permissions from roles
        permissions = set()
        for role in user.roles:
            if role.is_active:
                for permission in role.permissions:
                    permissions.add(permission.name)

        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "password_hash": user.hashed_password,
            "permissions": list(permissions),
            "roles": [{"id": str(role.id), "name": role.name} for role in user.roles if role.is_active]
        }
    return None


async def get_user_by_id_with_roles(db: AsyncSession, user_id: str) -> Optional[dict]:
    """Get user by ID from database with roles and permissions."""
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # Get user permissions from roles
        permissions = set()
        for role in user.roles:
            if role.is_active:
                for permission in role.permissions:
                    permissions.add(permission.name)

        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "password_hash": user.hashed_password,
            "permissions": list(permissions),
            "roles": [{"id": str(role.id), "name": role.name} for role in user.roles if role.is_active]
        }
    return None


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user and return access token."""
    # Check if user already exists
    existing_user = await get_user_by_username_with_roles(db, user_data.username)
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

    # Assign default role based on user type
    from app.models.role import Role
    stmt = select(Role).where(Role.name == user_data.user_type, Role.is_active == True)
    result = await db.execute(stmt)
    default_role = result.scalar_one_or_none()
    
    if default_role:
        new_user.roles.append(default_role)
        await db.commit()

    # Get user with roles for token creation
    user_with_roles = await get_user_by_username_with_roles(db, new_user.username)

    # Create and return token
    token = jwt_manager.create_token_pair(
        user_id=str(new_user.id),
        username=new_user.username,
        user_type=new_user.user_type,
        permissions=user_with_roles["permissions"] if user_with_roles else []
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
        remember_me=getattr(credentials, 'remember_me', False)
    )

    # Authenticate user
    token = await auth_service.authenticate_user(
        credentials=user_creds,
        get_user_func=lambda username: get_user_by_username_with_roles(db, username),
        request=request
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

    # Store refresh token if provided
    if token.refresh_token:
        expires_at = datetime.now(UTC) + timedelta(days=jwt_manager.refresh_token_expire_days)
        await jwt_manager.store_refresh_token(
            db=db,
            refresh_token=token.refresh_token,
            user_id=token.user_id if hasattr(token, 'user_id') else user_creds.username,
            session_id=token.session_id if hasattr(token, 'session_id') else "",
            expires_at=expires_at
        )

    # Update last login timestamp
    user_data = await get_user_by_username_with_roles(db, user_creds.username)
    if user_data:
        stmt = select(User).where(User.id == user_data["id"])
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.last_login = datetime.now(UTC)
            await db.commit()

    return TokenResponse(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        token_type=token.token_type,
        expires_in=token.expires_in
    )


@router.post("/logout", response_model=BaseResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Logout user and invalidate refresh tokens."""
    # Get refresh token from request body if provided
    refresh_token = None
    if request.headers.get("content-type") == "application/json":
        try:
            body = await request.json()
            refresh_token = body.get("refresh_token")
        except:
            pass

    if refresh_token:
        # Revoke specific refresh token
        await jwt_manager.revoke_refresh_token(db, refresh_token)
    else:
        # Revoke all user's refresh tokens
        await jwt_manager.revoke_user_tokens(db, str(current_user.id))

    return BaseResponse(message="Logged out successfully")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )

        # Verify refresh token
        token_data = await jwt_manager.verify_refresh_token(db, refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Get user with current roles and permissions
        user_data = await get_user_by_id_with_roles(db, token_data.user_id)
        if not user_data or not user_data["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new token pair
        new_token = jwt_manager.create_token_pair(
            user_id=user_data["id"],
            username=user_data["username"],
            user_type=user_data["user_type"],
            permissions=user_data["permissions"],
            remember_me=True  # Keep refresh token active
        )

        # Store new refresh token
        if new_token.refresh_token:
            expires_at = datetime.now(UTC) + timedelta(days=jwt_manager.refresh_token_expire_days)
            await jwt_manager.store_refresh_token(
                db=db,
                refresh_token=new_token.refresh_token,
                user_id=user_data["id"],
                session_id=token_data.session_id,
                expires_at=expires_at
            )

        # Optionally revoke old refresh token
        await jwt_manager.revoke_refresh_token(db, refresh_token)

        return TokenResponse(
            access_token=new_token.access_token,
            refresh_token=new_token.refresh_token,
            token_type=new_token.token_type,
            expires_in=new_token.expires_in
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current authenticated user profile."""
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        user_type=current_user.user_type,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )
