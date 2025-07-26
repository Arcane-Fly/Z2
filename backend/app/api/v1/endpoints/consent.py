"""
Consent and Access Control for Z2 MCP Server.

This module implements user consent workflows and access control
for tools and resources as required for production MCP servers.
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.consent import ConsentRequest as ConsentRequestModel
from app.services.consent_service import ConsentService

router = APIRouter()


# Pydantic Models for API
class ConsentRequest(BaseModel):
    """Request for user consent to access a resource or tool."""

    user_id: str
    resource_type: str  # "tool" or "resource"
    resource_name: str
    description: str
    permissions: list[str]
    expires_in_hours: Optional[int] = 24


class ConsentResponse(BaseModel):
    """Response to consent request."""

    consent_id: str
    status: str  # "pending", "granted", "denied", "expired"
    granted_at: Optional[str] = None
    expires_at: Optional[str] = None
    permissions: list[str]


class AccessPolicy(BaseModel):
    """Access control policy for resources/tools."""

    resource_type: str
    resource_name: str
    required_permissions: list[str]
    auto_approve: bool = False
    max_usage_per_hour: Optional[int] = None
    max_usage_per_day: Optional[int] = None
    description: Optional[str] = None


class AuditLog(BaseModel):
    """Audit log entry for resource/tool access."""

    log_id: str
    timestamp: str
    user_id: str
    action: str  # "request", "grant", "deny", "access", "error"
    resource_type: str
    resource_name: str
    details: Optional[dict] = None


class AccessCheckRequest(BaseModel):
    """Request to check access to a resource or tool."""

    user_id: str
    resource_type: str
    resource_name: str
    permissions: list[str]


def get_consent_service(db: AsyncSession = Depends(get_db)) -> ConsentService:
    """Get consent service instance."""
    return ConsentService(db)


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.post("/consent/request")
async def request_consent(
    request: ConsentRequest,
    http_request: Request,
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Request user consent for accessing a resource or tool."""
    ip_address, user_agent = get_client_info(http_request)
    
    # Check if there's an auto-approval policy
    policy = await consent_service.get_access_policy(
        request.resource_type, request.resource_name
    )
    
    consent_request = await consent_service.create_consent_request(
        user_id=request.user_id,
        resource_type=request.resource_type,
        resource_name=request.resource_name,
        description=request.description,
        permissions=request.permissions,
        expires_in_hours=request.expires_in_hours,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Auto-approve if policy allows
    if policy and policy.auto_approve:
        grant = await consent_service.grant_consent(
            consent_id=consent_request.id,
            granted_by="system",  # Auto-approved by system
            expires_in_hours=request.expires_in_hours,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        if grant:
            await db.commit()
            return ConsentResponse(
                consent_id=str(consent_request.id),
                status="granted",
                granted_at=grant.granted_at.isoformat(),
                expires_at=grant.expires_at.isoformat(),
                permissions=request.permissions,
            )
    
    await db.commit()
    return ConsentResponse(
        consent_id=str(consent_request.id),
        status="pending",
        permissions=request.permissions,
    )


@router.post("/consent/{consent_id}/grant")
async def grant_consent(
    consent_id: str,
    user_id: str,
    http_request: Request,
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Grant consent for a pending request."""
    ip_address, user_agent = get_client_info(http_request)
    
    try:
        consent_uuid = UUID(consent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid consent ID format",
        )
    
    # Get the original request
    consent_request = await consent_service.get_consent_request(consent_uuid)
    if not consent_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consent request not found: {consent_id}",
        )
    
    # Check if user is authorized to grant consent
    if consent_request.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to grant this consent",
        )
    
    grant = await consent_service.grant_consent(
        consent_id=consent_uuid,
        granted_by=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    if not grant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot grant consent for this request",
        )
    
    await db.commit()
    
    return ConsentResponse(
        consent_id=consent_id,
        status="granted",
        granted_at=grant.granted_at.isoformat(),
        expires_at=grant.expires_at.isoformat(),
        permissions=consent_request.permissions,
    )


@router.post("/consent/{consent_id}/deny")
async def deny_consent(
    consent_id: str,
    user_id: str,
    reason: Optional[str] = None,
    http_request: Request = None,
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Deny consent for a pending request."""
    ip_address, user_agent = get_client_info(http_request)
    
    try:
        consent_uuid = UUID(consent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid consent ID format",
        )
    
    # Get the original request
    consent_request = await consent_service.get_consent_request(consent_uuid)
    if not consent_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consent request not found: {consent_id}",
        )
    
    success = await consent_service.deny_consent(
        consent_id=consent_uuid,
        denied_by=user_id,
        reason=reason,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deny consent for this request",
        )
    
    await db.commit()
    
    return ConsentResponse(
        consent_id=consent_id,
        status="denied",
        permissions=consent_request.permissions,
    )


@router.get("/consent/{consent_id}")
async def get_consent_status(
    consent_id: str,
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Get the status of a consent request."""
    try:
        consent_uuid = UUID(consent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid consent ID format",
        )
    
    consent_request = await consent_service.get_consent_request(consent_uuid)
    if not consent_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consent not found: {consent_id}",
        )
    
    # Check if consent has expired
    if (
        consent_request.status == "granted" 
        and consent_request.expires_at 
        and datetime.now() > consent_request.expires_at.replace(tzinfo=None)
    ):
        consent_request.status = "expired"
        await db.commit()
    
    response = ConsentResponse(
        consent_id=consent_id,
        status=consent_request.status,
        permissions=consent_request.permissions,
    )
    
    if consent_request.granted_at:
        response.granted_at = consent_request.granted_at.isoformat()
    if consent_request.expires_at:
        response.expires_at = consent_request.expires_at.isoformat()
    
    return response


@router.post("/access/check")
async def check_access(
    request: AccessCheckRequest,
    http_request: Request,
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Check if user has access to a resource or tool."""
    ip_address, user_agent = get_client_info(http_request)
    
    result = await consent_service.check_access(
        user_id=request.user_id,
        resource_type=request.resource_type,
        resource_name=request.resource_name,
        permissions=request.permissions,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    await db.commit()  # Commit any audit log entries
    return result


@router.get("/policies")
async def list_access_policies(
    consent_service: ConsentService = Depends(get_consent_service),
) -> dict[str, list[dict]]:
    """List all access control policies."""
    policies = await consent_service.list_access_policies()
    
    return {
        "policies": [
            {
                "resource_type": p.resource_type,
                "resource_name": p.resource_name,
                "required_permissions": p.required_permissions,
                "auto_approve": p.auto_approve,
                "max_usage_per_hour": p.max_usage_per_hour,
                "max_usage_per_day": p.max_usage_per_day,
                "description": p.description,
            }
            for p in policies
        ]
    }


@router.put("/policies/{resource_type}/{resource_name}")
async def update_access_policy(
    resource_type: str,
    resource_name: str,
    policy: AccessPolicy,
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Update an access control policy."""
    await consent_service.create_or_update_access_policy(
        resource_type=resource_type,
        resource_name=resource_name,
        required_permissions=policy.required_permissions,
        auto_approve=policy.auto_approve,
        max_usage_per_hour=policy.max_usage_per_hour,
        max_usage_per_day=policy.max_usage_per_day,
        description=policy.description,
    )
    
    await db.commit()
    return {"message": "Policy updated successfully"}


@router.get("/audit")
async def get_audit_logs(
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    consent_service: ConsentService = Depends(get_consent_service),
) -> dict[str, list[dict]]:
    """Get audit logs with optional filtering."""
    logs = await consent_service.get_audit_logs(
        user_id=user_id,
        resource_type=resource_type,
        action=action,
        limit=limit,
        offset=offset,
    )
    
    return {
        "logs": [
            {
                "log_id": str(log.id),
                "timestamp": log.timestamp.isoformat(),
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_name": log.resource_name,
                "details": log.details,
            }
            for log in logs
        ]
    }


@router.get("/sessions/{user_id}")
async def get_user_sessions(
    user_id: str,
    consent_service: ConsentService = Depends(get_consent_service),
) -> dict[str, Any]:
    """Get active consent sessions for a user."""
    grants = await consent_service.get_user_active_consents(user_id)
    
    active_consents = []
    for grant in grants:
        active_consents.append({
            "consent_id": str(grant.request_id),
            "grant_id": str(grant.id),
            "granted_at": grant.granted_at.isoformat(),
            "expires_at": grant.expires_at.isoformat(),
            "permissions": grant.granted_permissions,
            "usage_count": grant.usage_count,
            "last_used_at": grant.last_used_at.isoformat() if grant.last_used_at else None,
            "request": {
                "resource_type": grant.request.resource_type,
                "resource_name": grant.request.resource_name,
                "description": grant.request.description,
            },
        })
    
    return {"user_id": user_id, "active_consents": active_consents}


@router.post("/setup-default-policies")
async def setup_default_policies(
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Set up default access policies for MCP resources and tools."""
    
    # Default policies for MCP tools and resources
    default_policies = [
        {
            "resource_type": "tool",
            "resource_name": "execute_agent",
            "required_permissions": ["agent:execute"],
            "auto_approve": False,
            "max_usage_per_hour": 10,
            "description": "Execute agent for task processing",
        },
        {
            "resource_type": "tool",
            "resource_name": "create_workflow",
            "required_permissions": ["workflow:create"],
            "auto_approve": False,
            "max_usage_per_hour": 5,
            "description": "Create new multi-agent workflows",
        },
        {
            "resource_type": "resource",
            "resource_name": "agent",
            "required_permissions": ["agent:read"],
            "auto_approve": True,
            "max_usage_per_hour": 50,
            "description": "Access agent information and status",
        },
        {
            "resource_type": "resource", 
            "resource_name": "workflow",
            "required_permissions": ["workflow:read"],
            "auto_approve": True,
            "max_usage_per_hour": 50,
            "description": "Access workflow templates and definitions",
        },
    ]
    
    for policy_data in default_policies:
        await consent_service.create_or_update_access_policy(**policy_data)
    
    await db.commit()
    return {"message": f"Set up {len(default_policies)} default policies"}


@router.post("/cleanup-expired")
async def cleanup_expired_consents(
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Clean up expired consent requests and grants."""
    count = await consent_service.cleanup_expired_consents()
    await db.commit()
    return {"expired_consents_cleaned": count}
