"""
Agent model for Z2 platform.
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base


class Agent(Base):
    """Agent model representing individual AI agents with specific roles."""

    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Agent configuration
    role: Mapped[str] = mapped_column(String(50))  # e.g., "researcher", "writer", "coder"
    system_prompt: Mapped[str] = mapped_column(Text)
    model_preferences: Mapped[Dict] = mapped_column(JSONB, default=dict)
    tools: Mapped[Dict] = mapped_column(JSONB, default=dict)
    skills: Mapped[Dict] = mapped_column(JSONB, default=dict)
    
    # Performance and behavior settings
    temperature: Mapped[float] = mapped_column(default=0.7)
    max_tokens: Mapped[int] = mapped_column(default=4096)
    timeout_seconds: Mapped[int] = mapped_column(default=300)
    max_iterations: Mapped[int] = mapped_column(default=10)
    
    # Agent state and metrics
    status: Mapped[str] = mapped_column(
        String(20), default="idle"  # "idle", "busy", "error", "disabled"
    )
    total_executions: Mapped[int] = mapped_column(default=0)
    total_tokens_used: Mapped[int] = mapped_column(default=0)
    average_response_time: Mapped[Optional[float]] = mapped_column()
    
    # Relationships
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name={self.name}, role={self.role})>"