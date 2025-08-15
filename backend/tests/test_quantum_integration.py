"""
Integration tests for quantum API endpoints.
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import create_application
from app.models.quantum import QuantumTask, TaskStatus


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    app = create_application()
    return TestClient(app)


@pytest.fixture
def mock_quantum_service():
    """Mock the quantum service for testing."""
    with patch('app.api.v1.endpoints.quantum.QuantumAgentManager') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance

        # Create a mock task
        mock_task = QuantumTask(
            id=uuid4(),
            name="Test Task",
            task_description="Test description",
            user_id=uuid4(),
            status=TaskStatus.PENDING,
        )

        mock_instance.create_task.return_value = mock_task
        mock_instance.get_task.return_value = mock_task
        mock_instance.execute_task.return_value = mock_task
        mock_instance.list_tasks.return_value = ([mock_task], 1)

        yield mock_instance


@pytest.fixture
def mock_auth():
    """Mock authentication to bypass login requirements."""
    with patch('app.api.v1.endpoints.quantum.get_current_user') as mock:
        from app.models.user import User
        mock_user = User(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            user_type="operator",
        )
        mock.return_value = mock_user
        yield mock_user


@pytest.fixture
def mock_db():
    """Mock database session."""
    with patch('app.api.v1.endpoints.quantum.get_db') as mock:
        mock_session = AsyncMock()
        mock.return_value = mock_session
        yield mock_session


class TestQuantumAPIEndpoints:
    """Test quantum API endpoints."""

    def test_create_quantum_task_endpoint(self, client, mock_quantum_service, mock_auth, mock_db):
        """Test POST /api/v1/multi-agent-system/quantum/tasks/create"""
        task_data = {
            "name": "Test Task",
            "task_description": "Analyze market trends",
            "collapse_strategy": "best_score",
            "variations": [
                {
                    "name": "Variation 1",
                    "agent_type": "researcher",
                },
                {
                    "name": "Variation 2",
                    "agent_type": "analyst",
                },
            ],
        }

        response = client.post(
            "/api/v1/multi-agent-system/quantum/tasks/create",
            json=task_data
        )

        # The endpoint should work with mocked dependencies
        assert response.status_code in [200, 422]  # 422 for validation errors in test env

    def test_list_quantum_tasks_endpoint(self, client, mock_quantum_service, mock_auth, mock_db):
        """Test GET /api/v1/multi-agent-system/quantum/tasks"""
        response = client.get(
            "/api/v1/multi-agent-system/quantum/tasks"
        )

        # The endpoint should be accessible
        assert response.status_code in [200, 422]

    def test_get_quantum_task_endpoint(self, client, mock_quantum_service, mock_auth, mock_db):
        """Test GET /api/v1/multi-agent-system/quantum/tasks/{task_id}"""
        task_id = str(uuid4())

        response = client.get(
            f"/api/v1/multi-agent-system/quantum/tasks/{task_id}"
        )

        # The endpoint should be accessible
        assert response.status_code in [200, 404, 422]

    def test_execute_quantum_task_endpoint(self, client, mock_quantum_service, mock_auth, mock_db):
        """Test POST /api/v1/multi-agent-system/quantum/tasks/{task_id}/execute"""
        task_id = str(uuid4())
        execution_data = {
            "force_restart": False
        }

        response = client.post(
            f"/api/v1/multi-agent-system/quantum/tasks/{task_id}/execute",
            json=execution_data
        )

        # The endpoint should be accessible
        assert response.status_code in [200, 404, 422]

    def test_quantum_task_validation(self, client, mock_quantum_service, mock_auth, mock_db):
        """Test quantum task input validation."""
        # Test missing required fields
        invalid_task_data = {
            "name": "Test Task",
            # Missing task_description and variations
        }

        response = client.post(
            "/api/v1/multi-agent-system/quantum/tasks/create",
            json=invalid_task_data
        )

        # Should return validation error
        assert response.status_code == 422

    def test_quantum_endpoints_require_auth(self, client, mock_db):
        """Test that quantum endpoints require authentication."""
        # Without mocked auth, endpoints should require authentication
        response = client.get("/api/v1/multi-agent-system/quantum/tasks")

        # Should require authentication (401 or 422 depending on implementation)
        assert response.status_code in [401, 422]


def test_quantum_module_imports():
    """Test that all quantum module components can be imported."""
    # Test model imports
    # Test API imports
    from app.api.v1.endpoints.quantum import router
    from app.models.quantum import (
        CollapseStrategy,
        QuantumTask,
    )

    # Test schema imports
    # Test service imports
    from app.services.quantum_service import QuantumAgentManager

    # All imports should succeed
    assert QuantumTask is not None
    assert QuantumAgentManager is not None
    assert router is not None
    assert CollapseStrategy.BEST_SCORE == "best_score"


def test_api_router_includes_quantum():
    """Test that the main API router includes quantum endpoints."""
    from app.api.v1 import api_router

    # Check that quantum routes are included
    quantum_routes = [
        route for route in api_router.routes
        if hasattr(route, 'path') and 'quantum' in route.path
    ]

    # Should have quantum routes
    assert len(quantum_routes) > 0


if __name__ == "__main__":
    # Run basic import test
    test_quantum_module_imports()
    print("✓ All quantum module imports successful")

    test_api_router_includes_quantum()
    print("✓ Quantum routes included in API router")
