"""
Test configuration and fixtures for Z2 backend tests.
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import create_application
from app.database.base import Base
from app.database.session import get_db


# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "sqlite+aiosqlite:///./test.db"
)

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

# Create test session factory
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture
async def test_db():
    """Create test database and clean up after tests."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(test_db):
    """Create a test client for the FastAPI application."""
    app = create_application()
    
    # Override the dependency to use test database
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    mock = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.close = AsyncMock()
    mock.flush = AsyncMock()
    mock.add = AsyncMock()
    mock.delete = AsyncMock()
    mock.refresh = AsyncMock()
    return mock


@pytest.fixture
def sample_mcp_initialize_request():
    """Sample MCP initialize request for testing."""
    return {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "resources": {"subscribe": True},
            "tools": {"listChanged": True},
            "prompts": {"listChanged": True}
        },
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }


@pytest.fixture
def sample_consent_request():
    """Sample consent request for testing."""
    return {
        "user_id": "test-user-123",
        "resource_type": "tool",
        "resource_name": "execute_agent",
        "description": "Execute agent for testing",
        "permissions": ["agent:execute"],
        "expires_in_hours": 24
    }


@pytest.fixture
def sample_a2a_handshake_request():
    """Sample A2A handshake request for testing."""
    return {
        "agent_id": "test-agent-123",
        "agent_name": "Test Agent",
        "capabilities": ["reasoning", "analysis"],
        "protocol_version": "1.0.0"
    }


@pytest.fixture
def mock_session_service():
    """Mock session service for testing."""
    mock = AsyncMock()
    
    # Mock MCP session methods
    mock.create_mcp_session = AsyncMock()
    mock.get_mcp_session = AsyncMock()
    mock.update_mcp_session_activity = AsyncMock()
    mock.close_mcp_session = AsyncMock()
    mock.list_active_mcp_sessions = AsyncMock(return_value=[])
    
    # Mock A2A session methods
    mock.create_a2a_session = AsyncMock()
    mock.get_a2a_session = AsyncMock()
    mock.update_a2a_session_activity = AsyncMock()
    mock.close_a2a_session = AsyncMock()
    mock.list_active_a2a_sessions = AsyncMock(return_value=[])
    
    # Mock task execution methods
    mock.create_task_execution = AsyncMock()
    mock.get_task_execution = AsyncMock()
    mock.update_task_progress = AsyncMock()
    mock.complete_task = AsyncMock()
    mock.cancel_task = AsyncMock()
    mock.list_running_tasks = AsyncMock(return_value=[])
    
    # Mock statistics
    mock.get_session_statistics = AsyncMock(return_value={
        "active_mcp_sessions": 0,
        "active_a2a_sessions": 0,
        "active_websocket_connections": 0,
        "running_tasks": 0,
    })
    
    return mock


@pytest.fixture
def mock_consent_service():
    """Mock consent service for testing."""
    mock = AsyncMock()
    
    # Mock consent methods
    mock.create_consent_request = AsyncMock()
    mock.get_consent_request = AsyncMock()
    mock.grant_consent = AsyncMock()
    mock.deny_consent = AsyncMock()
    mock.check_access = AsyncMock()
    mock.get_access_policy = AsyncMock()
    mock.create_or_update_access_policy = AsyncMock()
    mock.list_access_policies = AsyncMock(return_value=[])
    mock.get_audit_logs = AsyncMock(return_value=[])
    mock.get_user_active_consents = AsyncMock(return_value=[])
    mock.cleanup_expired_consents = AsyncMock(return_value=0)
    
    return mock


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "role": "operator",
        "is_active": True
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "name": "Test Agent",
        "description": "A test agent for unit testing",
        "capabilities": ["reasoning", "analysis"],
        "model_provider": "openai",
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2048
    }


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow for unit testing",
        "steps": [
            {
                "name": "Step 1",
                "agent_id": "test-agent-1",
                "input_schema": {"type": "string"},
                "output_schema": {"type": "string"}
            }
        ],
        "input_schema": {"type": "object"},
        "output_schema": {"type": "object"}
    }


# Security test fixtures
@pytest.fixture
def security_headers():
    """Expected security headers for testing."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    }


@pytest.fixture
def malicious_payloads():
    """Common malicious payloads for security testing."""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "admin'/*",
        ],
        "xss": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "'\"><script>alert('xss')</script>",
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
        ],
        "command_injection": [
            "; cat /etc/passwd",
            "| cat /etc/passwd",
            "& cat /etc/passwd",
            "`cat /etc/passwd`",
        ]
    }
