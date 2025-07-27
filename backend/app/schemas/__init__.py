"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Base schemas
class BaseResponse(BaseModel):
    """Base response schema."""

    success: bool = True
    message: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


class PaginatedResponse(BaseResponse):
    """Paginated response schema."""

    total: int
    page: int
    limit: int
    pages: int
    data: list[Any]


# Authentication schemas
class UserLogin(BaseModel):
    """User login request."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    remember_me: bool = Field(default=False)


class UserRegister(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=255)
    user_type: str = Field(default="operator", pattern="^(developer|operator)$")


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    
    refresh_token: str


class UserProfile(BaseModel):
    """User profile response."""

    id: UUID
    username: str
    email: str
    full_name: Optional[str]
    user_type: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# Agent schemas
class AgentCreate(BaseModel):
    """Agent creation request."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    role: str = Field(
        ...,
        pattern="^(researcher|analyst|writer|coder|reviewer|planner|executor|coordinator|validator)$",
    )
    system_prompt: str = Field(..., min_length=10)

    # Configuration
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=32000)
    timeout_seconds: int = Field(default=300, ge=30, le=3600)

    # Capabilities
    tools: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    preferred_models: list[str] = Field(default_factory=list)


class AgentUpdate(BaseModel):
    """Agent update request."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    system_prompt: Optional[str] = Field(None, min_length=10)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=32000)
    timeout_seconds: Optional[int] = Field(None, ge=30, le=3600)


class AgentResponse(BaseModel):
    """Agent response."""

    id: UUID
    name: str
    description: Optional[str]
    role: str
    system_prompt: str
    status: str

    # Configuration
    temperature: float
    max_tokens: int
    timeout_seconds: int

    # Metrics
    total_executions: int
    total_tokens_used: int
    average_response_time: Optional[float]

    # Metadata
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime]

    class Config:
        from_attributes = True


class AgentExecutionRequest(BaseModel):
    """Agent task execution request."""

    task_description: str = Field(..., min_length=10)
    input_data: dict[str, Any] = Field(default_factory=dict)
    expected_output_format: str = Field(default="json")
    max_tokens: Optional[int] = Field(None, ge=1, le=32000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)


class AgentExecutionResponse(BaseModel):
    """Agent task execution response."""

    task_id: UUID
    status: str
    output: dict[str, Any]
    tokens_used: int
    cost_usd: float
    execution_time_ms: float
    model_used: str


# Workflow schemas
class TaskCreate(BaseModel):
    """Task creation request."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10)
    assigned_agent: Optional[UUID] = None
    dependencies: list[UUID] = Field(default_factory=list)
    input_data: dict[str, Any] = Field(default_factory=dict)
    expected_output: dict[str, Any] = Field(default_factory=dict)
    success_criteria: list[str] = Field(default_factory=list)


class WorkflowCreate(BaseModel):
    """Workflow creation request."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    goal: str = Field(..., min_length=10)

    # Configuration
    max_duration_seconds: int = Field(default=3600, ge=60, le=86400)
    max_cost_usd: float = Field(default=10.0, ge=0.1, le=1000.0)
    require_human_approval: bool = Field(default=False)

    # Agent team (optional - can be auto-assigned)
    agent_ids: list[UUID] = Field(default_factory=list)

    # Tasks (optional - can be auto-generated)
    tasks: list[TaskCreate] = Field(default_factory=list)


class WorkflowUpdate(BaseModel):
    """Workflow update request."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    goal: Optional[str] = Field(None, min_length=10)
    max_duration_seconds: Optional[int] = Field(None, ge=60, le=86400)
    max_cost_usd: Optional[float] = Field(None, ge=0.1, le=1000.0)


class WorkflowResponse(BaseModel):
    """Workflow response."""

    id: UUID
    name: str
    description: Optional[str]
    goal: str
    status: str

    # Configuration
    max_duration_seconds: int
    max_cost_usd: float
    require_human_approval: bool

    # Execution state
    current_step: Optional[str]
    progress_percentage: float = 0.0

    # Metrics
    total_tokens_used: int
    total_cost_usd: float

    # Timing
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    # Relationships
    created_by: UUID
    agent_count: int
    task_count: int

    class Config:
        from_attributes = True


class WorkflowExecutionRequest(BaseModel):
    """Workflow execution request."""

    input_data: dict[str, Any] = Field(default_factory=dict)
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")
    notify_on_completion: bool = Field(default=True)


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response."""

    execution_id: UUID
    workflow_id: UUID
    status: str
    started_at: datetime
    estimated_completion: Optional[datetime]
    progress: dict[str, Any]


# Model Integration schemas
class ModelInfo(BaseModel):
    """Model information."""

    id: str
    provider: str
    name: str
    description: str
    capabilities: list[str]
    context_window: int
    input_cost_per_million_tokens: float
    output_cost_per_million_tokens: float
    avg_latency_ms: Optional[float]
    quality_score: Optional[float]


class ModelTestRequest(BaseModel):
    """Model test request."""

    model_id: str
    prompt: str = Field(..., min_length=10)
    max_tokens: int = Field(default=1000, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ModelTestResponse(BaseModel):
    """Model test response."""

    model_used: str
    provider: str
    response: str
    tokens_used: int
    cost_usd: float
    latency_ms: float


class RoutingPolicyUpdate(BaseModel):
    """Routing policy update request."""

    cost_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    latency_weight: float = Field(default=0.4, ge=0.0, le=1.0)
    quality_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    prefer_provider: Optional[str] = None
    max_cost_per_request: Optional[float] = Field(None, ge=0.001)
    max_latency_ms: Optional[float] = Field(None, ge=100)


class ModelMetricsResponse(BaseModel):
    """Model usage metrics."""

    model_id: str
    provider: str
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    avg_latency_ms: float
    success_rate: float
    last_used: Optional[datetime]


# System schemas
class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str
    app: str
    version: str
    timestamp: datetime
    services: dict[str, str]


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
