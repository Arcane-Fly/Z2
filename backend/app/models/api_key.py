"""
API Key model for programmatic access to Z2 platform.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.database.types import UniversalJSON


class APIKey(Base):
    """API Key model for programmatic access."""

    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Key identification
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    key_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)  # Store hash, not actual key
    key_prefix: Mapped[str] = mapped_column(String(10), index=True)  # First few chars for identification
    
    # Ownership
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    
    # Access control
    permissions: Mapped[list] = mapped_column(UniversalJSON, default=list)  # List of allowed operations
    allowed_endpoints: Mapped[list] = mapped_column(UniversalJSON, default=list)  # Specific endpoints allowed
    rate_limit_per_hour: Mapped[Optional[int]] = mapped_column(default=1000)  # Requests per hour
    
    # Key metadata
    is_active: Mapped[bool] = mapped_column(default=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    usage_count: Mapped[int] = mapped_column(default=0)
    
    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relationship
    user = relationship("User", back_populates="api_keys")

    @classmethod
    def generate_key(cls) -> tuple[str, str]:
        """Generate a new API key and return (key, hash)."""
        # Generate secure random key
        key = f"z2_{secrets.token_urlsafe(32)}"
        
        # Create hash for storage
        import hashlib
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        return key, key_hash
    
    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash an API key for verification."""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()
    
    def is_expired(self) -> bool:
        """Check if the API key is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the API key is valid for use."""
        return self.is_active and not self.is_expired()
    
    def has_permission(self, permission: str) -> bool:
        """Check if the API key has a specific permission."""
        if not self.permissions:
            return False
        return permission in self.permissions or "admin" in self.permissions
    
    def can_access_endpoint(self, endpoint: str) -> bool:
        """Check if the API key can access a specific endpoint."""
        if not self.allowed_endpoints:
            return True  # No restrictions
        
        # Check for exact match or wildcard patterns
        for allowed in self.allowed_endpoints:
            if allowed == endpoint or allowed.endswith("*") and endpoint.startswith(allowed[:-1]):
                return True
        
        return False


class APIKeyUsage(Base):
    """Track API key usage for monitoring and rate limiting."""

    __tablename__ = "api_key_usage"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Key reference
    api_key_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("api_keys.id"), index=True
    )
    
    # Request details
    endpoint: Mapped[str] = mapped_column(String(200), index=True)
    method: Mapped[str] = mapped_column(String(10))
    status_code: Mapped[int] = mapped_column(index=True)
    response_time_ms: Mapped[int] = mapped_column(default=0)
    
    # Request metadata
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 compatible
    request_size_bytes: Mapped[Optional[int]] = mapped_column(default=0)
    response_size_bytes: Mapped[Optional[int]] = mapped_column(default=0)
    
    # Error tracking
    error_type: Mapped[Optional[str]] = mapped_column(String(100))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    
    # Relationship
    api_key = relationship("APIKey")