"""
API Key management endpoints for Z2 platform.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.services.api_key import APIKeyService

logger = structlog.get_logger(__name__)

router = APIRouter()


# Pydantic models for request/response
class APIKeyCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    allowed_endpoints: Optional[List[str]] = None
    rate_limit_per_hour: int = 1000
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    key_prefix: str
    permissions: List[str]
    allowed_endpoints: List[str]
    rate_limit_per_hour: Optional[int]
    is_active: bool
    last_used_at: Optional[datetime]
    usage_count: int
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class APIKeyCreateResponse(BaseModel):
    api_key: APIKeyResponse
    key: str  # Only returned once during creation
    warning: str = "Store this key securely - it will not be shown again"


class APIKeyUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    allowed_endpoints: Optional[List[str]] = None
    rate_limit_per_hour: Optional[int] = None
    is_active: Optional[bool] = None


class APIKeyUsageStatsResponse(BaseModel):
    api_key_id: str
    period_days: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_response_time_ms: float
    total_request_bytes: int
    total_response_bytes: int
    endpoint_breakdown: List[dict]
    rate_limit_info: dict


@router.post("/", response_model=APIKeyCreateResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new API key for the current user."""
    service = APIKeyService(db)
    
    try:
        api_key, key_string = await service.create_api_key(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            permissions=request.permissions,
            allowed_endpoints=request.allowed_endpoints,
            rate_limit_per_hour=request.rate_limit_per_hour,
            expires_in_days=request.expires_in_days,
        )
        
        return APIKeyCreateResponse(
            api_key=APIKeyResponse(
                id=str(api_key.id),
                name=api_key.name,
                description=api_key.description,
                key_prefix=api_key.key_prefix,
                permissions=api_key.permissions,
                allowed_endpoints=api_key.allowed_endpoints,
                rate_limit_per_hour=api_key.rate_limit_per_hour,
                is_active=api_key.is_active,
                last_used_at=api_key.last_used_at,
                usage_count=api_key.usage_count,
                expires_at=api_key.expires_at,
                created_at=api_key.created_at,
                updated_at=api_key.updated_at,
            ),
            key=key_string,
        )
        
    except Exception as e:
        logger.error("Failed to create API key", error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all API keys for the current user."""
    service = APIKeyService(db)
    
    api_keys = await service.list_user_api_keys(current_user.id)
    
    return [
        APIKeyResponse(
            id=str(key.id),
            name=key.name,
            description=key.description,
            key_prefix=key.key_prefix,
            permissions=key.permissions,
            allowed_endpoints=key.allowed_endpoints,
            rate_limit_per_hour=key.rate_limit_per_hour,
            is_active=key.is_active,
            last_used_at=key.last_used_at,
            usage_count=key.usage_count,
            expires_at=key.expires_at,
            created_at=key.created_at,
            updated_at=key.updated_at,
        )
        for key in api_keys
    ]


@router.get("/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get details of a specific API key."""
    service = APIKeyService(db)
    
    api_key = await service.get_api_key(api_key_id, current_user.id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return APIKeyResponse(
        id=str(api_key.id),
        name=api_key.name,
        description=api_key.description,
        key_prefix=api_key.key_prefix,
        permissions=api_key.permissions,
        allowed_endpoints=api_key.allowed_endpoints,
        rate_limit_per_hour=api_key.rate_limit_per_hour,
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at,
        usage_count=api_key.usage_count,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
    )


@router.put("/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: UUID,
    request: APIKeyUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an API key."""
    service = APIKeyService(db)
    
    # Filter out None values
    updates = {k: v for k, v in request.dict().items() if v is not None}
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid updates provided"
        )
    
    api_key = await service.update_api_key(api_key_id, current_user.id, **updates)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return APIKeyResponse(
        id=str(api_key.id),
        name=api_key.name,
        description=api_key.description,
        key_prefix=api_key.key_prefix,
        permissions=api_key.permissions,
        allowed_endpoints=api_key.allowed_endpoints,
        rate_limit_per_hour=api_key.rate_limit_per_hour,
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at,
        usage_count=api_key.usage_count,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
    )


@router.delete("/{api_key_id}")
async def revoke_api_key(
    api_key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Revoke (deactivate) an API key."""
    service = APIKeyService(db)
    
    success = await service.revoke_api_key(api_key_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {"message": "API key revoked successfully", "revoked_at": datetime.utcnow()}


@router.get("/{api_key_id}/usage", response_model=APIKeyUsageStatsResponse)
async def get_api_key_usage_stats(
    api_key_id: UUID,
    days_back: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get usage statistics for an API key."""
    service = APIKeyService(db)
    
    stats = await service.get_api_key_usage_stats(
        api_key_id, current_user.id, days_back
    )
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return APIKeyUsageStatsResponse(**stats)


@router.post("/cleanup-expired")
async def cleanup_expired_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Clean up expired API keys (admin only)."""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = APIKeyService(db)
    count = await service.cleanup_expired_keys()
    
    return {
        "message": f"Cleaned up {count} expired API keys",
        "deactivated_count": count,
        "cleanup_time": datetime.utcnow(),
    }