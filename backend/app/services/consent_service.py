"""
Consent Service

Database service layer for consent and access control operations.
Handles consent requests, grants, audit logging, and access policies.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.consent import (
    AccessPolicy,
    ConsentAuditLog,
    ConsentGrant,
    ConsentRequest,
)


class ConsentService:
    """Service class for consent and access control operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_consent_request(
        self,
        user_id: str,
        resource_type: str,
        resource_name: str,
        description: str,
        permissions: list[str],
        expires_in_hours: int | None = 24,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentRequest:
        """Create a new consent request."""

        request = ConsentRequest(
            user_id=user_id,
            resource_type=resource_type,
            resource_name=resource_name,
            description=description,
            permissions=permissions,
            expires_in_hours=expires_in_hours,
        )

        self.db.add(request)
        await self.db.flush()  # Get the ID

        # Create audit log
        await self.create_audit_log(
            user_id=user_id,
            action="request",
            resource_type=resource_type,
            resource_name=resource_name,
            request_id=request.id,
            details={"consent_id": str(request.id), "permissions": permissions},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return request

    async def get_consent_request(self, consent_id: UUID) -> ConsentRequest | None:
        """Get a consent request by ID."""
        result = await self.db.execute(
            select(ConsentRequest)
            .options(selectinload(ConsentRequest.consent_grant))
            .where(ConsentRequest.id == consent_id)
        )
        return result.scalar_one_or_none()

    async def grant_consent(
        self,
        consent_id: UUID,
        granted_by: str,
        expires_in_hours: int | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentGrant | None:
        """Grant consent for a request."""

        request = await self.get_consent_request(consent_id)
        if not request:
            return None

        if request.status != "pending":
            return None

        # Calculate expiration
        expires_at = datetime.now(UTC) + timedelta(
            hours=expires_in_hours or request.expires_in_hours or 24
        )

        # Update request status
        request.status = "granted"
        request.granted_at = datetime.now(UTC)
        request.expires_at = expires_at

        # Create grant record
        grant = ConsentGrant(
            request_id=consent_id,
            granted_by=granted_by,
            granted_permissions=request.permissions,
            expires_at=expires_at,
        )

        self.db.add(grant)

        # Create audit log
        await self.create_audit_log(
            user_id=request.user_id,
            action="grant",
            resource_type=request.resource_type,
            resource_name=request.resource_name,
            request_id=consent_id,
            details={"consent_id": str(consent_id), "granted_by": granted_by},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return grant

    async def deny_consent(
        self,
        consent_id: UUID,
        denied_by: str,
        reason: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> bool:
        """Deny consent for a request."""

        request = await self.get_consent_request(consent_id)
        if not request:
            return False

        if request.status != "pending":
            return False

        # Update request status
        request.status = "denied"

        # Create audit log
        await self.create_audit_log(
            user_id=request.user_id,
            action="deny",
            resource_type=request.resource_type,
            resource_name=request.resource_name,
            request_id=consent_id,
            details={"consent_id": str(consent_id), "reason": reason, "denied_by": denied_by},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return True

    async def check_access(
        self,
        user_id: str,
        resource_type: str,
        resource_name: str,
        permissions: list[str],
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        """Check if user has access to a resource."""

        # Get access policy
        policy = await self.get_access_policy(resource_type, resource_name)
        if not policy:
            await self.create_audit_log(
                user_id=user_id,
                action="error",
                resource_type=resource_type,
                resource_name=resource_name,
                details={"error": "No access policy found"},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            return {"allowed": False, "reason": "No access policy defined"}

        # Check required permissions
        missing_permissions = set(policy.required_permissions) - set(permissions)
        if missing_permissions:
            return {
                "allowed": False,
                "reason": f"Missing permissions: {list(missing_permissions)}",
            }

        # Check for valid consent
        now = datetime.now(UTC)

        # Query for valid grants
        grant_query = (
            select(ConsentGrant)
            .join(ConsentRequest)
            .where(
                and_(
                    ConsentRequest.user_id == user_id,
                    ConsentRequest.resource_type == resource_type,
                    ConsentRequest.resource_name == resource_name,
                    ConsentRequest.status == "granted",
                    ConsentGrant.expires_at > now,
                    ConsentGrant.revoked_at.is_(None),
                )
            )
        )

        result = await self.db.execute(grant_query)
        grant = result.scalar_one_or_none()

        if not grant:
            return {"allowed": False, "reason": "No valid consent found"}

        # Update usage tracking
        grant.usage_count += 1
        grant.last_used_at = now

        # Create access audit log
        await self.create_audit_log(
            user_id=user_id,
            action="access",
            resource_type=resource_type,
            resource_name=resource_name,
            request_id=grant.request_id,
            details={"permissions": permissions, "grant_id": str(grant.id)},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return {"allowed": True, "reason": "Access granted", "grant_id": str(grant.id)}

    async def get_access_policy(
        self, resource_type: str, resource_name: str
    ) -> AccessPolicy | None:
        """Get access policy for a resource."""
        policy_key = f"{resource_type}:{resource_name}"

        result = await self.db.execute(
            select(AccessPolicy).where(
                and_(
                    AccessPolicy.policy_key == policy_key,
                    AccessPolicy.is_active is True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_or_update_access_policy(
        self,
        resource_type: str,
        resource_name: str,
        required_permissions: list[str],
        auto_approve: bool = False,
        max_usage_per_hour: int | None = None,
        max_usage_per_day: int | None = None,
        description: str | None = None,
    ) -> AccessPolicy:
        """Create or update an access policy."""
        policy_key = f"{resource_type}:{resource_name}"

        # Check if policy exists
        existing = await self.get_access_policy(resource_type, resource_name)

        if existing:
            # Update existing policy
            existing.required_permissions = required_permissions
            existing.auto_approve = auto_approve
            existing.max_usage_per_hour = max_usage_per_hour
            existing.max_usage_per_day = max_usage_per_day
            existing.description = description
            return existing
        else:
            # Create new policy
            policy = AccessPolicy(
                resource_type=resource_type,
                resource_name=resource_name,
                policy_key=policy_key,
                required_permissions=required_permissions,
                auto_approve=auto_approve,
                max_usage_per_hour=max_usage_per_hour,
                max_usage_per_day=max_usage_per_day,
                description=description,
            )
            self.db.add(policy)
            return policy

    async def list_access_policies(
        self, active_only: bool = True
    ) -> list[AccessPolicy]:
        """List all access policies."""
        query = select(AccessPolicy)
        if active_only:
            query = query.where(AccessPolicy.is_active is True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_audit_log(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_name: str,
        request_id: UUID | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentAuditLog:
        """Create an audit log entry."""
        log_entry = ConsentAuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_name=resource_name,
            request_id=request_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log_entry)
        return log_entry

    async def get_audit_logs(
        self,
        user_id: str | None = None,
        resource_type: str | None = None,
        action: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConsentAuditLog]:
        """Get audit logs with optional filtering."""
        query = select(ConsentAuditLog).order_by(ConsentAuditLog.timestamp.desc())

        conditions = []
        if user_id:
            conditions.append(ConsentAuditLog.user_id == user_id)
        if resource_type:
            conditions.append(ConsentAuditLog.resource_type == resource_type)
        if action:
            conditions.append(ConsentAuditLog.action == action)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_active_consents(self, user_id: str) -> list[ConsentGrant]:
        """Get active consent grants for a user."""
        now = datetime.now(UTC)

        query = (
            select(ConsentGrant)
            .join(ConsentRequest)
            .options(selectinload(ConsentGrant.request))
            .where(
                and_(
                    ConsentRequest.user_id == user_id,
                    ConsentRequest.status == "granted",
                    ConsentGrant.expires_at > now,
                    ConsentGrant.revoked_at.is_(None),
                )
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def revoke_consent(
        self, grant_id: UUID, revoked_by: str, reason: str | None = None
    ) -> bool:
        """Revoke a consent grant."""
        result = await self.db.execute(
            select(ConsentGrant)
            .options(selectinload(ConsentGrant.request))
            .where(ConsentGrant.id == grant_id)
        )
        grant = result.scalar_one_or_none()

        if not grant:
            return False

        grant.revoked_at = datetime.now(UTC)
        grant.request.status = "revoked"

        # Create audit log
        await self.create_audit_log(
            user_id=grant.request.user_id,
            action="revoke",
            resource_type=grant.request.resource_type,
            resource_name=grant.request.resource_name,
            request_id=grant.request_id,
            details={
                "grant_id": str(grant_id),
                "revoked_by": revoked_by,
                "reason": reason,
            },
        )

        return True

    async def cleanup_expired_consents(self) -> int:
        """Clean up expired consent requests and grants."""
        now = datetime.now(UTC)

        # Update expired requests
        expired_requests = await self.db.execute(
            select(ConsentRequest).where(
                and_(
                    ConsentRequest.status == "granted",
                    ConsentRequest.expires_at <= now,
                )
            )
        )

        count = 0
        for request in expired_requests.scalars():
            request.status = "expired"
            count += 1

        return count
