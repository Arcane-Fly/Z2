"""
Quantum computing schemas for Z2 platform API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.quantum import CollapseStrategy, TaskStatus, ThreadStatus


# Base schemas for quantum models
class VariationBase(BaseModel):
    """Base schema for quantum execution variations."""
    name: str = Field(..., description="Name of the variation")
    description: str | None = Field(None, description="Description of the variation")
    agent_type: str = Field(..., description="Type of agent to use")
    provider: str | None = Field(None, description="LLM provider to use")
    model: str | None = Field(None, description="Specific model to use")
    prompt_modifications: dict = Field(default_factory=dict, description="Modifications to apply to prompts")
    parameters: dict = Field(default_factory=dict, description="Additional parameters")
    weight: float = Field(1.0, ge=0.0, description="Weight for weighted collapse strategies")


class VariationCreate(VariationBase):
    """Schema for creating a new variation."""
    pass


class VariationResponse(VariationBase):
    """Schema for variation responses."""
    id: UUID
    task_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Quantum task schemas
class QuantumTaskBase(BaseModel):
    """Base schema for quantum tasks."""
    name: str = Field(..., description="Name of the quantum task")
    description: str | None = Field(None, description="Description of the task")
    task_description: str = Field(..., description="The task to be executed")
    collapse_strategy: CollapseStrategy = Field(
        CollapseStrategy.BEST_SCORE, description="Strategy for collapsing results"
    )
    metrics_config: dict = Field(
        default_factory=dict, description="Configuration for metrics evaluation"
    )
    max_parallel_executions: int = Field(
        5, ge=1, le=20, description="Maximum number of parallel executions"
    )
    timeout_seconds: int = Field(
        300, ge=30, le=3600, description="Timeout for task execution in seconds"
    )


class QuantumTaskCreate(QuantumTaskBase):
    """Schema for creating a new quantum task."""
    variations: list[VariationCreate] = Field(
        ..., min_items=1, max_items=20, description="List of execution variations"
    )


class QuantumTaskUpdate(BaseModel):
    """Schema for updating a quantum task."""
    name: str | None = Field(None, description="Name of the quantum task")
    description: str | None = Field(None, description="Description of the task")
    status: TaskStatus | None = Field(None, description="Task status")


class QuantumTaskResponse(QuantumTaskBase):
    """Schema for quantum task responses."""
    id: UUID
    status: TaskStatus
    progress: float
    collapsed_result: dict | None
    final_metrics: dict | None
    execution_summary: dict | None
    started_at: datetime | None
    completed_at: datetime | None
    total_execution_time: float | None
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Thread result schemas
class QuantumThreadResultResponse(BaseModel):
    """Schema for quantum thread result responses."""
    id: UUID
    thread_name: str
    status: ThreadStatus
    result: dict | None
    error_message: str | None
    execution_time: float | None
    success_rate: float | None
    completeness: float | None
    accuracy: float | None
    total_score: float | None
    detailed_metrics: dict
    tokens_used: int | None
    cost: float | None
    provider_used: str | None
    model_used: str | None
    started_at: datetime | None
    completed_at: datetime | None
    task_id: UUID
    variation_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Execution request schema
class QuantumTaskExecutionRequest(BaseModel):
    """Schema for executing a quantum task."""
    force_restart: bool = Field(
        False, description="Force restart if task is already running"
    )
    custom_metrics: dict | None = Field(
        None, description="Custom metrics configuration for this execution"
    )


# Task list response
class QuantumTaskListResponse(BaseModel):
    """Schema for quantum task list responses."""
    tasks: list[QuantumTaskResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


# Detailed task response with related data
class QuantumTaskDetailResponse(QuantumTaskResponse):
    """Schema for detailed quantum task responses with related data."""
    variations: list[VariationResponse] = Field(
        default_factory=list, description="Task variations"
    )
    thread_results: list[QuantumThreadResultResponse] = Field(
        default_factory=list, description="Thread execution results"
    )


# Metrics schemas
class MetricsConfiguration(BaseModel):
    """Schema for metrics configuration."""
    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "execution_time": 0.2,
            "success_rate": 0.3,
            "completeness": 0.3,
            "accuracy": 0.2
        },
        description="Weights for different metrics"
    )
    normalization: dict[str, dict] = Field(
        default_factory=dict,
        description="Normalization parameters for metrics"
    )
    custom_metrics: dict[str, dict] = Field(
        default_factory=dict,
        description="Custom metric definitions"
    )


# Error response schemas
class QuantumError(BaseModel):
    """Schema for quantum operation errors."""
    error_type: str
    message: str
    details: dict | None = None
    task_id: UUID | None = None
    thread_id: UUID | None = None
