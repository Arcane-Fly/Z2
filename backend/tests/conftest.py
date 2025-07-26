"""
Test configuration and fixtures for Z2 backend tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import create_application


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    app = create_application()
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    mock = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.close = AsyncMock()
    mock.flush = AsyncMock()
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
