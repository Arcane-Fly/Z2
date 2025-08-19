"""
Test utilities for Z2 backend tests.
"""

from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.main import create_application
from app.models.user import User


def create_mock_user(
    user_id: str = "test-user-id",
    email: str = "test@example.com",
    full_name: str = "Test User",
    user_type: str = "operator",
    is_active: bool = True
) -> User:
    """Create a mock user for testing."""
    user = User(
        id=user_id,
        email=email,
        full_name=full_name,
        user_type=user_type,
        is_active=is_active,
        hashed_password="$2b$12$test.hash"
    )
    return user


def create_test_client_with_auth(test_db: AsyncSession, user: User | None = None) -> TestClient:
    """Create a test client with authenticated user."""
    app = create_application()

    # Override database dependency
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Mock authentication if user provided
    if user:
        from app.api.auth import get_current_user

        async def override_get_current_user():
            return user

        app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app)


def create_sample_agent_data() -> dict[str, Any]:
    """Create sample agent data for testing."""
    return {
        "name": "Test Agent",
        "description": "A test agent for unit testing",
        "role": "assistant",
        "system_prompt": "You are a helpful test assistant.",
        "model_preferences": {
            "preferred_models": ["gpt-4"],
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "is_active": True
    }


def create_sample_workflow_data() -> dict[str, Any]:
    """Create sample workflow data for testing."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow for unit testing",
        "steps": [
            {
                "name": "Step 1",
                "agent_id": "test-agent-id",
                "prompt": "Perform step 1",
                "dependencies": []
            },
            {
                "name": "Step 2",
                "agent_id": "test-agent-id-2",
                "prompt": "Perform step 2",
                "dependencies": ["Step 1"]
            }
        ],
        "is_active": True
    }


def create_mock_mcp_session() -> MagicMock:
    """Create a mock MCP session for testing."""
    mock_session = MagicMock()
    mock_session.session_id = "test-session-id"
    mock_session.status = "active"
    mock_session.capabilities = {
        "supports_resources": True,
        "supports_tools": True,
        "supports_prompts": True
    }
    return mock_session


def create_mock_ai_response(content: str = "Test AI response") -> dict[str, Any]:
    """Create a mock AI model response."""
    return {
        "content": content,
        "model": "test-model",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        },
        "finish_reason": "stop"
    }


class MockRedisClient:
    """Mock Redis client for testing."""

    def __init__(self):
        self.data = {}

    async def get(self, key: str) -> str | None:
        return self.data.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.data[key] = value
        return True

    async def delete(self, key: str) -> int:
        if key in self.data:
            del self.data[key]
            return 1
        return 0

    async def exists(self, key: str) -> int:
        return 1 if key in self.data else 0


@pytest.fixture
def mock_redis():
    """Provide a mock Redis client for testing."""
    return MockRedisClient()


@pytest.fixture
def sample_user():
    """Provide a sample user for testing."""
    return create_mock_user()


@pytest.fixture
def authenticated_client(test_db, sample_user):
    """Provide an authenticated test client."""
    return create_test_client_with_auth(test_db, sample_user)


@pytest.fixture
def unauthenticated_client(test_db):
    """Provide an unauthenticated test client."""
    return create_test_client_with_auth(test_db, None)
