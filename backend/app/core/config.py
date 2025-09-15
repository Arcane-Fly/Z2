"""
Z2 Backend API Configuration Module

This module contains all configuration settings for the Z2 backend API,
including environment variables, database settings, and service configurations.
"""

import json
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Custom env parsing for complex types
        env_parse_none_str="None",
    )

    # Application Settings
    app_name: str = "Z2 AI Workforce Platform"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    port: int = Field(default=8000, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")

    # API Settings
    api_v1_prefix: str = "/api/v1"
    allowed_hosts: list[str] = Field(default=["*"], description="Allowed hosts")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="CORS allowed origins (comma-separated or JSON array)",
    )

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, value: str) -> list[str]:
        """Parse CORS origins from string to list.

        Handles multiple input formats:
        - JSON array format: '["http://localhost:3000","https://app.com"]'
        - Comma-separated string: 'http://localhost:3000,https://app.com'
        - Comma-separated with spaces: 'http://localhost:3000, https://app.com'
        """
        if isinstance(value, list):
            # Already processed - check if empty and return defaults if so
            return value if value else ["http://localhost:3000", "http://localhost:5173"]

        if not isinstance(value, str) or not value.strip():
            return ["http://localhost:3000", "http://localhost:5173"]

        # Try to parse as JSON first
        if value.strip().startswith("[") and value.strip().endswith("]"):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    result = [str(origin).strip() for origin in parsed if origin]
                    return result if result else ["http://localhost:3000", "http://localhost:5173"]
            except (json.JSONDecodeError, ValueError):
                pass

        # Handle comma-separated string format
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        return origins if origins else ["http://localhost:3000", "http://localhost:5173"]

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return self.parse_cors_origins(self.cors_origins)

    # Database Settings
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/z2",
        description="Database connection URL",
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # Redis Settings
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # Authentication Settings
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production",
        description="JWT secret key",
        alias="JWT_SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm",
        alias="JWT_ALGORITHM"
    )

    # LLM Provider API Keys
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(
        default=None, description="Anthropic API key"
    )
    groq_api_key: str | None = Field(default=None, description="Groq API key")
    google_api_key: str | None = Field(default=None, description="Google API key")
    perplexity_api_key: str | None = Field(
        default=None, description="Perplexity API key"
    )
    xai_api_key: str | None = Field(default=None, description="xAI API key")
    moonshot_api_key: str | None = Field(
        default=None, description="Moonshot AI API key"
    )
    qwen_api_key: str | None = Field(default=None, description="Qwen API key")

    # LLM Configuration
    default_model: str = Field(
        default="groq/llama-3.3-70b-versatile", description="Default LLM model"
    )
    reasoning_model: str = Field(
        default="openai/o4-mini",
        description="Default reasoning model for complex tasks",
    )
    advanced_model: str = Field(
        default="anthropic/claude-sonnet-4-20250514",
        description="Advanced model for complex analysis",
    )
    fast_model: str = Field(
        default="groq/llama-3.1-8b-instant", description="Fast model for quick responses"
    )
    multimodal_model: str = Field(
        default="google/gemini-2.5-flash",
        description="Multimodal model for vision/audio tasks",
    )
    embedding_model: str = Field(
        default="openai/text-embedding-3-small",
        description="Embedding model for vector operations",
    )
    search_model: str = Field(
        default="perplexity/llama-3.1-sonar-large-128k-online",
        description="Model with real-time search capabilities",
    )
    cost_efficient_model: str = Field(
        default="qwen/qwen2.5-7b-instruct",
        description="Most cost-efficient model for basic tasks",
    )
    max_tokens: int = Field(default=4096, description="Maximum tokens per request")
    temperature: float = Field(default=0.7, description="Default temperature")

    # Agent Configuration
    max_agents_per_workflow: int = Field(
        default=10, description="Maximum agents per workflow"
    )
    agent_timeout_seconds: int = Field(
        default=300, description="Agent execution timeout"
    )
    max_workflow_duration_hours: int = Field(
        default=24, description="Maximum workflow duration"
    )

    # Vector Database Configuration
    vector_db_type: str = Field(default="chroma", description="Vector database type")
    chroma_host: str = Field(default="localhost", description="Chroma host")
    chroma_port: int = Field(default=8000, description="Chroma port")

    # Monitoring and Observability
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=8001, description="Metrics server port")
    enable_tracing: bool = Field(default=True, description="Enable request tracing")

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=60, description="Rate limit per minute"
    )

    # File Storage
    storage_type: str = Field(default="local", description="Storage type")
    storage_path: str = Field(default="/opt/app/storage", description="Local storage path")
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")

    # MCP Protocol Configuration
    mcp_server_name: str = Field(
        default="Z2 AI Workforce Platform", description="MCP server name"
    )
    mcp_server_version: str = Field(default="1.0.0", description="MCP server version")
    mcp_protocol_version: str = Field(
        default="2025-03-26", description="MCP protocol version"
    )
    enable_mcp_sessions: bool = Field(
        default=True, description="Enable MCP session management"
    )
    session_timeout_minutes: int = Field(
        default=30, description="Session timeout in minutes"
    )
    max_concurrent_sessions: int = Field(
        default=100, description="Maximum concurrent sessions"
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return not self.debug

    @property
    def database_url_async(self) -> str:
        """Get async database URL with asyncpg driver."""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for migrations."""
        return self.database_url_async.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
