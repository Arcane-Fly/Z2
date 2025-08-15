"""
Authorization dependencies for FastAPI route protection.
"""

import inspect
from functools import wraps

import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import jwt_manager
from app.database.session import get_db
from app.models.api_key import APIKey
from app.models.role import Role
from app.models.user import User

logger = structlog.get_logger(__name__)


security = HTTPBearer()


class AuthorizationError(HTTPException):
    """Custom authorization error."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify JWT token
    token_data = jwt_manager.verify_token(credentials.credentials)

    # Get user with roles and permissions
    stmt = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        .where(User.id == token_data.user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (alias for clarity)."""
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user, ensuring they are a superuser."""
    if not current_user.is_superuser:
        raise AuthorizationError("Superuser access required")
    return current_user


def check_user_permissions(user: User, required_permissions: list[str]) -> bool:
    """Check if user has all required permissions."""
    if user.is_superuser:
        return True

    # Get all user permissions from roles
    user_permissions = set()
    for role in user.roles:
        if role.is_active:
            for permission in role.permissions:
                user_permissions.add(permission.name)

    # Check if user has all required permissions
    required_set = set(required_permissions)
    return required_set.issubset(user_permissions)


def get_user_permissions(user: User) -> set[str]:
    """Get all permissions for a user."""
    if user.is_superuser:
        return {"system:admin"}  # Superuser has all permissions

    permissions = set()
    for role in user.roles:
        if role.is_active:
            for permission in role.permissions:
                permissions.add(permission.name)

    return permissions


def require_permissions(*required_permissions: str):
    """
    Decorator to require specific permissions for an endpoint.

    Usage:
        @require_permissions("users:read", "users:write")
        async def update_user(...):
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the current user from the function arguments
            current_user = None

            # Look for current_user in kwargs first
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            else:
                # If not found in kwargs, look in args based on function signature
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())

                for i, param_name in enumerate(param_names):
                    param = sig.parameters[param_name]
                    if param.annotation == User and i < len(args):
                        current_user = args[i]
                        break

            if not current_user:
                raise AuthorizationError("Authentication required")

            # Check permissions
            if not check_user_permissions(current_user, list(required_permissions)):
                missing_perms = set(required_permissions) - get_user_permissions(current_user)
                raise AuthorizationError(
                    f"Missing required permissions: {', '.join(missing_perms)}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def RequirePermissions(*required_permissions: str):
    """
    FastAPI dependency to require specific permissions.

    Usage:
        @app.get("/users", dependencies=[Depends(RequirePermissions("users:read"))])
        async def list_users():
            pass
    """
    async def check_permissions(current_user: User = Depends(get_current_user)):
        if not check_user_permissions(current_user, list(required_permissions)):
            missing_perms = set(required_permissions) - get_user_permissions(current_user)
            raise AuthorizationError(
                f"Missing required permissions: {', '.join(missing_perms)}"
            )
        return current_user

    return check_permissions


def RequireAnyPermission(*permissions: str):
    """
    FastAPI dependency that requires ANY of the specified permissions.

    Usage:
        @app.get("/data", dependencies=[Depends(RequireAnyPermission("admin:read", "user:read"))])
        async def get_data():
            pass
    """
    async def check_any_permission(current_user: User = Depends(get_current_user)):
        if current_user.is_superuser:
            return current_user

        user_permissions = get_user_permissions(current_user)
        if not any(perm in user_permissions for perm in permissions):
            raise AuthorizationError(
                f"Requires one of: {', '.join(permissions)}"
            )
        return current_user

    return check_any_permission


def RequireRole(*required_roles: str):
    """
    FastAPI dependency to require specific roles.

    Usage:
        @app.get("/admin", dependencies=[Depends(RequireRole("admin", "manager"))])
        async def admin_endpoint():
            pass
    """
    async def check_roles(current_user: User = Depends(get_current_user)):
        if current_user.is_superuser:
            return current_user

        user_roles = {role.name for role in current_user.roles if role.is_active}
        required_set = set(required_roles)

        if not required_set.intersection(user_roles):
            raise AuthorizationError(
                f"Requires one of these roles: {', '.join(required_roles)}"
            )
        return current_user

    return check_roles


# Convenience dependencies for common permission patterns
RequireUserRead = RequirePermissions("users:read")
RequireUserWrite = RequirePermissions("users:write")
RequireUserDelete = RequirePermissions("users:delete")

RequireAgentRead = RequirePermissions("agents:read")
RequireAgentWrite = RequirePermissions("agents:write")
RequireAgentDelete = RequirePermissions("agents:delete")
RequireAgentExecute = RequirePermissions("agents:execute")

RequireWorkflowRead = RequirePermissions("workflows:read")
RequireWorkflowWrite = RequirePermissions("workflows:write")
RequireWorkflowDelete = RequirePermissions("workflows:delete")
RequireWorkflowExecute = RequirePermissions("workflows:execute")

RequireSystemAdmin = RequirePermissions("system:admin")
RequireSystemManage = RequirePermissions("system:manage")

# Role-based dependencies
RequireAdminRole = RequireRole("admin")
RequireManagerRole = RequireRole("manager", "admin")
RequireDeveloperRole = RequireRole("developer", "manager", "admin")
RequireOperatorRole = RequireRole("operator", "developer", "manager", "admin")


# API Key Authentication Support
async def authenticate_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """Authenticate using API key instead of JWT token."""

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )

    # Check if it looks like an API key
    if not credentials.credentials.startswith("z2_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )

    # Import here to avoid circular imports
    from app.services.api_key import APIKeyService

    service = APIKeyService(db)
    api_key = await service.validate_api_key(credentials.credentials)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )

    # Check rate limits
    rate_limit_info = await service.check_rate_limit(api_key)
    if not rate_limit_info["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Limit: {rate_limit_info['limit']}/hour, "
                   f"Usage: {rate_limit_info['usage']}, "
                   f"Remaining: {rate_limit_info['remaining']}"
        )

    # Check endpoint permissions
    endpoint = request.url.path
    if not api_key.can_access_endpoint(endpoint):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key does not have access to endpoint: {endpoint}"
        )

    return api_key


async def get_current_user_from_api_key(
    api_key: APIKey = Depends(authenticate_api_key),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the user associated with an API key."""

    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == api_key.user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account associated with API key is inactive"
        )

    return user


async def get_current_user_or_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate using either JWT token or API key.
    This allows endpoints to accept both authentication methods.
    """

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    token = credentials.credentials

    # Check if it's an API key
    if token.startswith("z2_"):
        try:
            api_key = await authenticate_api_key(request, credentials, db)
            return await get_current_user_from_api_key(api_key, db)
        except HTTPException:
            raise
    else:
        # Try JWT authentication
        try:
            return await get_current_user(credentials, db)
        except HTTPException:
            raise

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials"
    )


# API Key Permission Checks
def require_api_key_permissions(*required_permissions: str):
    """
    Dependency that requires API key to have specific permissions.

    Usage:
        @router.get("/data", dependencies=[Depends(require_api_key_permissions("data:read"))])
        async def get_data(api_key: APIKey = Depends(authenticate_api_key)):
            pass
    """
    def check_permissions(api_key: APIKey = Depends(authenticate_api_key)):
        for permission in required_permissions:
            if not api_key.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"API key missing required permission: {permission}"
                )
        return api_key

    return check_permissions
