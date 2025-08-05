"""
Model Routing Policy model for persistent storage of model routing configurations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.session import Base
from app.database.types import UniversalJSON


class ModelRoutingPolicy(Base):
    """Model for storing dynamic model routing policies."""

    __tablename__ = "model_routing_policies"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Policy configuration
    task_type: Mapped[str] = mapped_column(String(50), index=True)  # e.g., "reasoning", "code_generation"
    model_id: Mapped[str] = mapped_column(String(100))  # The preferred model for this task type
    fallback_models: Mapped[list] = mapped_column(UniversalJSON, default=list)  # Fallback model IDs
    
    # Policy constraints
    max_cost_per_request: Mapped[Optional[float]] = mapped_column(default=None)
    max_latency_ms: Mapped[Optional[int]] = mapped_column(default=None)
    required_capabilities: Mapped[list] = mapped_column(UniversalJSON, default=list)
    
    # Policy metadata
    is_active: Mapped[bool] = mapped_column(default=True)
    priority: Mapped[int] = mapped_column(default=100)  # Lower number = higher priority
    created_by: Mapped[Optional[str]] = mapped_column(String(100))  # User who created policy
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ModelUsageTracking(Base):
    """Model for tracking model usage statistics."""

    __tablename__ = "model_usage_tracking"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Request identification
    model_id: Mapped[str] = mapped_column(String(100), index=True)
    provider: Mapped[str] = mapped_column(String(50), index=True)
    task_type: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Usage metrics
    input_tokens: Mapped[int] = mapped_column(default=0)
    output_tokens: Mapped[int] = mapped_column(default=0)
    total_tokens: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)
    latency_ms: Mapped[int] = mapped_column(default=0)
    
    # Request details
    was_cached: Mapped[bool] = mapped_column(default=False)
    success: Mapped[bool] = mapped_column(default=True)
    error_type: Mapped[Optional[str]] = mapped_column(String(100))
    request_metadata: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )