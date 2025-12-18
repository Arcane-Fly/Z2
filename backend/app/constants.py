"""
Centralized constants for the Z2 backend API.

This module provides a single source of truth for configuration values,
status codes, and other constants used throughout the backend application.
"""

from enum import Enum
from typing import Final

# API Configuration
API_V1_PREFIX: Final[str] = "/api/v1"

# HTTP Status Codes
class HTTPStatus:
    """HTTP status codes used throughout the API."""
    
    OK: Final[int] = 200
    CREATED: Final[int] = 201
    ACCEPTED: Final[int] = 202
    NO_CONTENT: Final[int] = 204
    BAD_REQUEST: Final[int] = 400
    UNAUTHORIZED: Final[int] = 401
    FORBIDDEN: Final[int] = 403
    NOT_FOUND: Final[int] = 404
    CONFLICT: Final[int] = 409
    UNPROCESSABLE_ENTITY: Final[int] = 422
    TOO_MANY_REQUESTS: Final[int] = 429
    INTERNAL_SERVER_ERROR: Final[int] = 500
    SERVICE_UNAVAILABLE: Final[int] = 503


# Agent Status
class AgentStatus(str, Enum):
    """Agent execution status."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


# Workflow Status
class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


# Model Provider Types
class ModelProvider(str, Enum):
    """LLM provider types."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GOOGLE = "google"
    PERPLEXITY = "perplexity"
    XAI = "xai"
    MOONSHOT = "moonshot"
    QWEN = "qwen"


# Model Types
class ModelType(str, Enum):
    """LLM model types by capability."""
    
    DEFAULT = "default"
    REASONING = "reasoning"
    ADVANCED = "advanced"
    FAST = "fast"
    MULTIMODAL = "multimodal"
    EMBEDDING = "embedding"
    SEARCH = "search"
    COST_EFFICIENT = "cost_efficient"


# Vector Database Types
class VectorDBType(str, Enum):
    """Vector database types."""
    
    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"


# Storage Types
class StorageType(str, Enum):
    """Storage backend types."""
    
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"


# User Roles
class UserRole(str, Enum):
    """User role types."""
    
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    DEVELOPER = "developer"
    OPERATOR = "operator"


# MCP Protocol
class MCPProtocol:
    """MCP protocol constants."""
    
    # Version uses date format as per MCP specification: https://modelcontextprotocol.io/
    # This is the official MCP protocol version identifier format
    VERSION: Final[str] = "2025-03-26"
    SERVER_NAME: Final[str] = "Z2 AI Workforce Platform"
    SERVER_VERSION: Final[str] = "1.0.0"


# A2A Protocol
class A2AProtocol:
    """A2A protocol constants."""
    
    VERSION: Final[str] = "1.0.0"
    HANDSHAKE_TIMEOUT: Final[int] = 30  # seconds
    NEGOTIATION_TIMEOUT: Final[int] = 60  # seconds


# Pagination
class Pagination:
    """Pagination defaults."""
    
    DEFAULT_PAGE_SIZE: Final[int] = 20
    MAX_PAGE_SIZE: Final[int] = 100
    DEFAULT_PAGE: Final[int] = 1


# Rate Limiting
class RateLimit:
    """Rate limiting configurations."""
    
    DEFAULT_REQUESTS_PER_MINUTE: Final[int] = 60
    AUTH_REQUESTS_PER_MINUTE: Final[int] = 10
    WORKFLOW_REQUESTS_PER_MINUTE: Final[int] = 30


# Timeouts
class Timeouts:
    """Timeout configurations (in seconds)."""
    
    DEFAULT_REQUEST: Final[int] = 30
    AGENT_EXECUTION: Final[int] = 300  # 5 minutes
    WORKFLOW_EXECUTION: Final[int] = 86400  # 24 hours
    DATABASE_QUERY: Final[int] = 10
    EXTERNAL_API: Final[int] = 30


# Cache TTL
class CacheTTL:
    """Cache time-to-live configurations (in seconds)."""
    
    SHORT: Final[int] = 60  # 1 minute
    MEDIUM: Final[int] = 300  # 5 minutes
    LONG: Final[int] = 3600  # 1 hour
    VERY_LONG: Final[int] = 86400  # 24 hours


# Error Messages
class ErrorMessages:
    """Standard error messages."""
    
    GENERIC: Final[str] = "An unexpected error occurred. Please try again."
    UNAUTHORIZED: Final[str] = "You are not authorized to perform this action."
    NOT_FOUND: Final[str] = "The requested resource was not found."
    BAD_REQUEST: Final[str] = "Invalid request data."
    INTERNAL_ERROR: Final[str] = "Internal server error. Please try again later."
    RATE_LIMIT: Final[str] = "Too many requests. Please try again later."
    VALIDATION_ERROR: Final[str] = "Validation error. Please check your input."


# Validation Rules
class ValidationRules:
    """Validation constraints."""
    
    MIN_PASSWORD_LENGTH: Final[int] = 8
    MAX_PASSWORD_LENGTH: Final[int] = 128
    MIN_USERNAME_LENGTH: Final[int] = 3
    MAX_USERNAME_LENGTH: Final[int] = 50
    MAX_AGENT_NAME_LENGTH: Final[int] = 100
    MAX_WORKFLOW_NAME_LENGTH: Final[int] = 100
    MAX_DESCRIPTION_LENGTH: Final[int] = 1000
    MAX_FILE_SIZE_MB: Final[int] = 10


# Token Configuration
class TokenConfig:
    """JWT token configurations."""
    
    ALGORITHM: Final[str] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30
    REFRESH_TOKEN_EXPIRE_DAYS: Final[int] = 7


# Log Levels
class LogLevel(str, Enum):
    """Logging levels."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Health Check
class HealthStatus(str, Enum):
    """Health check statuses."""
    
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


# Export all constants for convenience
__all__ = [
    "API_V1_PREFIX",
    "HTTPStatus",
    "AgentStatus",
    "WorkflowStatus",
    "ModelProvider",
    "ModelType",
    "VectorDBType",
    "StorageType",
    "UserRole",
    "MCPProtocol",
    "A2AProtocol",
    "Pagination",
    "RateLimit",
    "Timeouts",
    "CacheTTL",
    "ErrorMessages",
    "ValidationRules",
    "TokenConfig",
    "LogLevel",
    "HealthStatus",
]
