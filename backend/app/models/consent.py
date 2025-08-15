"""
Consent and Access Control Database Models

This module defines the database models for consent requests, grants,
audit logs, and access policies as required for MCP server compliance.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base


class ConsentRequest(Base):
    """Database model for consent requests."""

    __tablename__ = "consent_requests"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )

    # Request details
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    resource_type: Mapped[str] = mapped_column(String(50))  # "tool" or "resource"
    resource_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    permissions: Mapped[list[str]] = mapped_column(JSON)
    expires_in_hours: Mapped[int | None] = mapped_column(Integer, default=24)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # "pending", "granted", "denied", "expired"

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    consent_grant: Mapped[Optional["ConsentGrant"]] = relationship(
        "ConsentGrant", back_populates="request", uselist=False
    )
    audit_logs: Mapped[list["ConsentAuditLog"]] = relationship(
        "ConsentAuditLog", back_populates="request"
    )

    def __repr__(self) -> str:
        return f"<ConsentRequest(id={self.id}, user_id={self.user_id}, status={self.status})>"


class ConsentGrant(Base):
    """Database model for consent grants."""

    __tablename__ = "consent_grants"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )

    # Link to request
    request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("consent_requests.id"), index=True
    )

    # Grant details
    granted_by: Mapped[str] = mapped_column(String(255))  # User ID who granted
    granted_permissions: Mapped[list[str]] = mapped_column(JSON)

    # Timestamps
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    request: Mapped["ConsentRequest"] = relationship(
        "ConsentRequest", back_populates="consent_grant"
    )

    def __repr__(self) -> str:
        return f"<ConsentGrant(id={self.id}, request_id={self.request_id})>"


class AccessPolicy(Base):
    """Database model for access control policies."""

    __tablename__ = "access_policies"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )

    # Policy identification
    resource_type: Mapped[str] = mapped_column(String(50))
    resource_name: Mapped[str] = mapped_column(String(255))
    policy_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Policy rules
    required_permissions: Mapped[list[str]] = mapped_column(JSON)
    auto_approve: Mapped[bool] = mapped_column(Boolean, default=False)
    max_usage_per_hour: Mapped[int | None] = mapped_column(Integer)
    max_usage_per_day: Mapped[int | None] = mapped_column(Integer)

    # Policy metadata
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<AccessPolicy(id={self.id}, policy_key={self.policy_key})>"


class ConsentAuditLog(Base):
    """Database model for consent audit logs."""

    __tablename__ = "consent_audit_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )

    # Log details
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    action: Mapped[str] = mapped_column(String(50))  # "request", "grant", "deny", "access", "error"
    resource_type: Mapped[str] = mapped_column(String(50))
    resource_name: Mapped[str] = mapped_column(String(255))

    # Context
    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("consent_requests.id"), index=True
    )
    details: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    request: Mapped[Optional["ConsentRequest"]] = relationship(
        "ConsentRequest", back_populates="audit_logs"
    )

    def __repr__(self) -> str:
        return f"<ConsentAuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
