"""
User model for Z2 platform.
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base

if TYPE_CHECKING:
    from app.models.role import Role, RefreshToken


class User(Base):
    """User model representing both developers and operators."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))

    # User type and permissions
    user_type: Mapped[str] = mapped_column(
        String(20),
        default="operator",  # "developer" or "operator"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Profile information
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships (defined after the role module is imported)
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, type={self.user_type})>"
