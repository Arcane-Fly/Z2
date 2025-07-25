"""
Consent and Access Control for Z2 MCP Server.

This module implements user consent workflows and access control
for tools and resources as required for production MCP servers.
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

router = APIRouter()


# Consent and Access Control Models
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


class AuditLog(BaseModel):
    """Audit log entry for resource/tool access."""

    log_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
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


# In-memory storage (TODO: Move to Redis/Database)
consent_requests: dict[str, ConsentRequest] = {}
consent_responses: dict[str, ConsentResponse] = {}
access_policies: dict[str, AccessPolicy] = {}
audit_logs: list[AuditLog] = []
user_sessions: dict[str, set[str]] = {}  # user_id -> set of granted consent_ids


# Default access policies
DEFAULT_POLICIES = {
    "tool:execute_agent": AccessPolicy(
        resource_type="tool",
        resource_name="execute_agent",
        required_permissions=["agent:execute"],
        auto_approve=False,
        max_usage_per_hour=10,
    ),
    "tool:create_workflow": AccessPolicy(
        resource_type="tool",
        resource_name="create_workflow",
        required_permissions=["workflow:create"],
        auto_approve=False,
        max_usage_per_hour=5,
    ),
    "resource:agent": AccessPolicy(
        resource_type="resource",
        resource_name="agent",
        required_permissions=["agent:read"],
        auto_approve=True,
        max_usage_per_hour=50,
    ),
    "resource:workflow": AccessPolicy(
        resource_type="resource",
        resource_name="workflow",
        required_permissions=["workflow:read"],
        auto_approve=True,
        max_usage_per_hour=50,
    ),
}

# Initialize default policies
access_policies.update(DEFAULT_POLICIES)


def create_audit_log(
    user_id: str,
    action: str,
    resource_type: str,
    resource_name: str,
    details: Optional[dict] = None,
) -> None:
    """Create an audit log entry."""
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_name=resource_name,
        details=details,
    )
    audit_logs.append(log_entry)


@router.post("/consent/request")
async def request_consent(
    request: ConsentRequest,
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Request user consent for accessing a resource or tool."""
    consent_id = str(uuid4())

    # Check if there's an access policy
    policy_key = f"{request.resource_type}:{request.resource_name}"
    policy = access_policies.get(policy_key)

    # Create audit log
    create_audit_log(
        user_id=request.user_id,
        action="request",
        resource_type=request.resource_type,
        resource_name=request.resource_name,
        details={"consent_id": consent_id, "permissions": request.permissions},
    )

    # Store the request
    consent_requests[consent_id] = request

    # Auto-approve if policy allows
    if policy and policy.auto_approve:
        expires_at = datetime.utcnow() + timedelta(hours=request.expires_in_hours or 24)
        response = ConsentResponse(
            consent_id=consent_id,
            status="granted",
            granted_at=datetime.utcnow().isoformat(),
            expires_at=expires_at.isoformat(),
            permissions=request.permissions,
        )

        # Track user session
        if request.user_id not in user_sessions:
            user_sessions[request.user_id] = set()
        user_sessions[request.user_id].add(consent_id)

        create_audit_log(
            user_id=request.user_id,
            action="grant",
            resource_type=request.resource_type,
            resource_name=request.resource_name,
            details={"consent_id": consent_id, "auto_approved": True},
        )
    else:
        response = ConsentResponse(
            consent_id=consent_id, status="pending", permissions=request.permissions
        )

    consent_responses[consent_id] = response
    return response


@router.post("/consent/{consent_id}/grant")
async def grant_consent(
    consent_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Grant consent for a pending request."""
    if consent_id not in consent_requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consent request not found: {consent_id}",
        )

    request = consent_requests[consent_id]

    # Check if user is authorized to grant consent (simplified)
    if request.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to grant this consent",
        )

    expires_at = datetime.utcnow() + timedelta(hours=request.expires_in_hours or 24)
    response = ConsentResponse(
        consent_id=consent_id,
        status="granted",
        granted_at=datetime.utcnow().isoformat(),
        expires_at=expires_at.isoformat(),
        permissions=request.permissions,
    )

    consent_responses[consent_id] = response

    # Track user session
    if user_id not in user_sessions:
        user_sessions[user_id] = set()
    user_sessions[user_id].add(consent_id)

    create_audit_log(
        user_id=user_id,
        action="grant",
        resource_type=request.resource_type,
        resource_name=request.resource_name,
        details={"consent_id": consent_id},
    )

    return response


@router.post("/consent/{consent_id}/deny")
async def deny_consent(
    consent_id: str,
    user_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Deny consent for a pending request."""
    if consent_id not in consent_requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consent request not found: {consent_id}",
        )

    request = consent_requests[consent_id]

    response = ConsentResponse(
        consent_id=consent_id, status="denied", permissions=request.permissions
    )

    consent_responses[consent_id] = response

    create_audit_log(
        user_id=user_id,
        action="deny",
        resource_type=request.resource_type,
        resource_name=request.resource_name,
        details={"consent_id": consent_id, "reason": reason},
    )

    return response


@router.get("/consent/{consent_id}")
async def get_consent_status(
    consent_id: str,
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Get the status of a consent request."""
    if consent_id not in consent_responses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consent not found: {consent_id}",
        )

    response = consent_responses[consent_id]

    # Check if consent has expired
    if response.status == "granted" and response.expires_at:
        expires_at = datetime.fromisoformat(response.expires_at)
        if datetime.utcnow() > expires_at:
            response.status = "expired"
            consent_responses[consent_id] = response

    return response


@router.post("/access/check")
async def check_access(
    request: AccessCheckRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Check if user has access to a resource or tool."""
    # Check access policy
    policy_key = f"{request.resource_type}:{request.resource_name}"
    policy = access_policies.get(policy_key)

    if not policy:
        create_audit_log(
            user_id=request.user_id,
            action="error",
            resource_type=request.resource_type,
            resource_name=request.resource_name,
            details={"error": "No access policy found"},
        )
        return {"allowed": False, "reason": "No access policy defined"}

    # Check required permissions
    missing_permissions = set(policy.required_permissions) - set(request.permissions)
    if missing_permissions:
        return {
            "allowed": False,
            "reason": f"Missing permissions: {list(missing_permissions)}",
        }

    # Check user consents
    user_consents = user_sessions.get(request.user_id, set())
    valid_consent = False

    for consent_id in user_consents:
        if consent_id in consent_responses:
            consent = consent_responses[consent_id]
            if consent.status == "granted" and consent.expires_at:
                expires_at = datetime.fromisoformat(consent.expires_at)
                if datetime.utcnow() <= expires_at:
                    # Check if this consent covers the requested resource
                    request_data = consent_requests.get(consent_id)
                    if (
                        request_data
                        and request_data.resource_type == request.resource_type
                        and request_data.resource_name == request.resource_name
                    ):
                        valid_consent = True
                        break

    if not valid_consent:
        return {"allowed": False, "reason": "No valid consent found"}

    # TODO: Check rate limits
    if policy.max_usage_per_hour:
        # Simple rate limiting check would go here
        pass

    create_audit_log(
        user_id=request.user_id,
        action="access",
        resource_type=request.resource_type,
        resource_name=request.resource_name,
        details={"permissions": request.permissions},
    )

    return {"allowed": True, "reason": "Access granted"}


@router.get("/policies")
async def list_access_policies(
    db: AsyncSession = Depends(get_db),
) -> dict[str, list[AccessPolicy]]:
    """List all access control policies."""
    return {"policies": [policy.model_dump() for policy in access_policies.values()]}


@router.put("/policies/{policy_key}")
async def update_access_policy(
    policy_key: str,
    policy: AccessPolicy,
    db: AsyncSession = Depends(get_db),
) -> AccessPolicy:
    """Update an access control policy."""
    access_policies[policy_key] = policy
    return policy


@router.get("/audit")
async def get_audit_logs(
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> dict[str, list[AuditLog]]:
    """Get audit logs with optional filtering."""
    filtered_logs = audit_logs

    if user_id:
        filtered_logs = [log for log in filtered_logs if log.user_id == user_id]

    if resource_type:
        filtered_logs = [
            log for log in filtered_logs if log.resource_type == resource_type
        ]

    # Return most recent logs first
    filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)

    return {"logs": [log.model_dump() for log in filtered_logs[:limit]]}


@router.get("/sessions/{user_id}")
async def get_user_sessions(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get active consent sessions for a user."""
    user_consents = user_sessions.get(user_id, set())
    active_consents = []

    for consent_id in user_consents:
        if consent_id in consent_responses:
            consent = consent_responses[consent_id]
            if consent.status == "granted" and consent.expires_at:
                expires_at = datetime.fromisoformat(consent.expires_at)
                if datetime.utcnow() <= expires_at:
                    active_consents.append(
                        {
                            "consent_id": consent_id,
                            "granted_at": consent.granted_at,
                            "expires_at": consent.expires_at,
                            "permissions": consent.permissions,
                            "request": consent_requests.get(consent_id, {}),
                        }
                    )

    return {"user_id": user_id, "active_consents": active_consents}
