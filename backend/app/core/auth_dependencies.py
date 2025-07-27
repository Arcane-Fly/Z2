"""
Authorization dependencies for FastAPI route protection.
"""

from typing import List, Optional, Set
from functools import wraps
import inspect

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import jwt_manager
from app.database.session import get_db
from app.models.user import User
from app.models.role import Role, Permission


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


def check_user_permissions(user: User, required_permissions: List[str]) -> bool:
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


def get_user_permissions(user: User) -> Set[str]:
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