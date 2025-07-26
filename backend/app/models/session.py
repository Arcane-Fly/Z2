"""
Session Management Database Models

This module defines the database models for MCP and A2A session management
to support persistent session tracking and recovery.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.session import Base


class MCPSession(Base):
    """Database model for MCP protocol sessions."""

    __tablename__ = "mcp_sessions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Session identification
    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Client information
    client_name: Mapped[Optional[str]] = mapped_column(String(255))
    client_version: Mapped[Optional[str]] = mapped_column(String(50))
    client_info: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Protocol details
    protocol_version: Mapped[str] = mapped_column(String(20))
    client_capabilities: Mapped[Optional[dict]] = mapped_column(JSON)
    server_capabilities: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Session state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Connection details
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<MCPSession(id={self.id}, session_id={self.session_id}, active={self.is_active})>"


class A2ASession(Base):
    """Database model for A2A protocol sessions."""

    __tablename__ = "a2a_sessions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Session identification
    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Agent information
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    agent_name: Mapped[str] = mapped_column(String(255))
    agent_capabilities: Mapped[list[str]] = mapped_column(JSON)
    
    # Protocol details
    protocol_version: Mapped[str] = mapped_column(String(20))
    public_key: Mapped[Optional[str]] = mapped_column(Text)
    
    # Session state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    has_websocket: Mapped[bool] = mapped_column(Boolean, default=False)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Connection details
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<A2ASession(id={self.id}, session_id={self.session_id}, agent_id={self.agent_id})>"


class A2ANegotiation(Base):
    """Database model for A2A skill negotiations."""

    __tablename__ = "a2a_negotiations"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Negotiation identification
    negotiation_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    
    # Negotiation details
    requested_skills: Mapped[list[str]] = mapped_column(JSON)
    available_skills: Mapped[list[str]] = mapped_column(JSON)
    task_description: Mapped[str] = mapped_column(Text)
    task_parameters: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Negotiation results
    accepted: Mapped[bool] = mapped_column(Boolean)
    proposed_workflow: Mapped[Optional[dict]] = mapped_column(JSON)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer)
    cost_estimate: Mapped[Optional[float]] = mapped_column(String(20))  # Using string for decimal precision
    
    # Priority and timeouts
    priority: Mapped[int] = mapped_column(Integer, default=5)
    timeout_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # "pending", "accepted", "rejected", "completed", "failed"
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<A2ANegotiation(id={self.id}, negotiation_id={self.negotiation_id}, status={self.status})>"


class TaskExecution(Base):
    """Database model for tracking long-running task executions."""

    __tablename__ = "task_executions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Task identification
    task_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    negotiation_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    
    # Task details
    task_type: Mapped[str] = mapped_column(String(50))  # "mcp_tool", "a2a_task", "workflow"
    task_name: Mapped[str] = mapped_column(String(255))
    task_parameters: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Execution state
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # "pending", "running", "completed", "failed", "cancelled"
    progress: Mapped[float] = mapped_column(String(5), default="0.0")  # 0.0 to 1.0
    
    # Results and errors
    result: Mapped[Optional[dict]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Cancellation support
    can_cancel: Mapped[bool] = mapped_column(Boolean, default=True)
    cancelled_by: Mapped[Optional[str]] = mapped_column(String(255))
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<TaskExecution(id={self.id}, task_id={self.task_id}, status={self.status})>"