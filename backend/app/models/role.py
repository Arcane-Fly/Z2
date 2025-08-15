"""
Role and Permission models for Z2 platform.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base

if TYPE_CHECKING:
    from app.models.user import User


# Association table for role-permission many-to-many relationship
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", PG_UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", PG_UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True),
)

# Association table for user-role many-to-many relationship
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role_id", PG_UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
)


class Permission(Base):
    """Permission model for fine-grained access control."""

    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    resource: Mapped[str] = mapped_column(String(50), index=True)  # e.g., "users", "agents", "workflows"
    action: Mapped[str] = mapped_column(String(50), index=True)    # e.g., "read", "write", "delete", "execute"

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name}, resource={self.resource}, action={self.action})>"


class Role(Base):
    """Role model for role-based access control."""

    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False)  # For built-in roles
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    permissions: Mapped[list[Permission]] = relationship(
        Permission,
        secondary=role_permissions,
        back_populates="roles"
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name}, is_system_role={self.is_system_role})>"


class RefreshToken(Base):
    """Refresh token model for JWT token management."""

    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # Hashed token
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_used: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"
