"""
Workflow model for Z2 platform.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.session import Base
from app.database.types import UniversalJSON


class Workflow(Base):
    """Workflow model representing multi-agent orchestration workflows."""

    __tablename__ = "workflows"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Workflow configuration
    goal: Mapped[str] = mapped_column(Text)  # High-level objective
    agent_team: Mapped[dict] = mapped_column(UniversalJSON, default=dict)  # Agent IDs and roles
    workflow_graph: Mapped[dict] = mapped_column(UniversalJSON, default=dict)  # Execution graph
    execution_policy: Mapped[dict] = mapped_column(
        UniversalJSON, default=dict
    )  # Routing and execution rules

    # Input/Output configuration
    input_schema: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    output_schema: Mapped[dict] = mapped_column(UniversalJSON, default=dict)

    # Execution state
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",  # "draft", "running", "paused", "completed", "failed"
    )
    current_step: Mapped[Optional[str]] = mapped_column(String(100))
    execution_context: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    intermediate_results: Mapped[dict] = mapped_column(UniversalJSON, default=dict)

    # Execution metadata
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    execution_duration_seconds: Mapped[Optional[int]] = mapped_column()

    # Performance metrics
    total_tokens_used: Mapped[int] = mapped_column(default=0)
    total_cost_usd: Mapped[float] = mapped_column(default=0.0)
    success_rate: Mapped[Optional[float]] = mapped_column()

    # Template and versioning
    is_template: Mapped[bool] = mapped_column(default=False)
    template_category: Mapped[Optional[str]] = mapped_column(String(50))
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")

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

    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name={self.name}, status={self.status})>"


class WorkflowExecution(Base):
    """Individual workflow execution instances for tracking and auditing."""

    __tablename__ = "workflow_executions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workflows.id"), index=True
    )

    # Execution details
    input_data: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    output_data: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    execution_log: Mapped[dict] = mapped_column(UniversalJSON, default=dict)

    # Status and timing
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[Optional[int]] = mapped_column()

    # Resource usage
    tokens_used: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)

    # Relationships
    executed_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )

    def __repr__(self) -> str:
        return f"<WorkflowExecution(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"
