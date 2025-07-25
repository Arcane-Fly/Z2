"""
Z2 Backend API Configuration Module

This module contains all configuration settings for the Z2 backend API,
including environment variables, database settings, and service configurations.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = "Z2 AI Workforce Platform"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API Settings
    api_v1_prefix: str = "/api/v1"
    allowed_hosts: list[str] = Field(default=["*"], description="Allowed hosts")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="CORS allowed origins",
    )

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
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")

    # LLM Provider API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key"
    )
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    perplexity_api_key: Optional[str] = Field(
        default=None, description="Perplexity API key"
    )

    # LLM Configuration
    default_model: str = Field(
        default="openai/gpt-4.1-mini", description="Default LLM model"
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
    storage_path: str = Field(default="./storage", description="Local storage path")
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return not self.debug

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for migrations."""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()