"""
Test configuration and fixtures for Z2 backend tests.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_application


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    app = create_application()
    return TestClient(app)


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
