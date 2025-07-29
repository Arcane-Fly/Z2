"""
Quantum computing models for Z2 platform.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base


class CollapseStrategy(str, Enum):
    """Strategies for collapsing quantum task results."""
    FIRST_SUCCESS = "first_success"
    BEST_SCORE = "best_score"
    CONSENSUS = "consensus"
    COMBINED = "combined"
    WEIGHTED = "weighted"


class TaskStatus(str, Enum):
    """Status of quantum tasks."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ThreadStatus(str, Enum):
    """Status of quantum execution threads."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QuantumTask(Base):
    """Quantum task model representing parallel agent execution tasks."""

    __tablename__ = "quantum_tasks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Task configuration
    task_description: Mapped[str] = mapped_column(Text)
    collapse_strategy: Mapped[CollapseStrategy] = mapped_column(
        String(20), default=CollapseStrategy.BEST_SCORE
    )
    metrics_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    max_parallel_executions: Mapped[int] = mapped_column(Integer, default=5)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300)
    
    # Task state
    status: Mapped[TaskStatus] = mapped_column(
        String(20), default=TaskStatus.PENDING, index=True
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Results
    collapsed_result: Mapped[Optional[dict]] = mapped_column(JSONB)
    final_metrics: Mapped[Optional[dict]] = mapped_column(JSONB)
    execution_summary: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Metadata
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_execution_time: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationships
    user_id: Mapped[UUID] = mapped_column(
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
        return f"<QuantumTask(id={self.id}, name={self.name}, status={self.status})>"


class Variation(Base):
    """Variation model representing different execution configurations."""

    __tablename__ = "quantum_variations"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Variation configuration
    agent_type: Mapped[str] = mapped_column(String(50))  # Agent type to use
    provider: Mapped[Optional[str]] = mapped_column(String(50))  # LLM provider
    model: Mapped[Optional[str]] = mapped_column(String(100))  # Specific model
    prompt_modifications: Mapped[dict] = mapped_column(JSONB, default=dict)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    weight: Mapped[float] = mapped_column(Float, default=1.0)  # For weighted strategies
    
    # Relationships
    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("quantum_tasks.id"), index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Variation(id={self.id}, name={self.name}, agent_type={self.agent_type})>"


class QuantumThreadResult(Base):
    """Result model for individual quantum execution threads."""

    __tablename__ = "quantum_thread_results"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Execution details
    thread_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[ThreadStatus] = mapped_column(
        String(20), default=ThreadStatus.PENDING, index=True
    )
    
    # Results
    result: Mapped[Optional[dict]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metrics
    execution_time: Mapped[Optional[float]] = mapped_column(Float)
    success_rate: Mapped[Optional[float]] = mapped_column(Float)
    completeness: Mapped[Optional[float]] = mapped_column(Float)
    accuracy: Mapped[Optional[float]] = mapped_column(Float)
    total_score: Mapped[Optional[float]] = mapped_column(Float)
    detailed_metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Execution metadata
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    cost: Mapped[Optional[float]] = mapped_column(Float)
    provider_used: Mapped[Optional[str]] = mapped_column(String(50))
    model_used: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("quantum_tasks.id"), index=True
    )
    variation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("quantum_variations.id"), index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<QuantumThreadResult(id={self.id}, status={self.status}, score={self.total_score})>"