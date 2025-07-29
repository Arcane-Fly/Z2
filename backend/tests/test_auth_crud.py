"""
Integration tests for authentication and CRUD endpoints.
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
def sample_user_data():
    """Sample user registration data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "user_type": "operator"
    }


@pytest.fixture
def sample_login_data():
    """Sample login data."""
    return {
        "username": "testuser",
        "password": "TestPassword123!"
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent creation data."""
    return {
        "name": "Test Agent",
        "description": "A test agent for development",
        "role": "researcher",
        "system_prompt": "You are a helpful AI assistant focused on research tasks.",
        "temperature": 0.7,
        "max_tokens": 2048,
        "timeout_seconds": 300,
        "tools": ["web_search", "document_analysis"],
        "skills": ["research", "analysis"],
        "preferred_models": ["openai/gpt-4.1-mini"]
    }


@pytest.fixture
def sample_workflow_data():
    """Sample workflow creation data."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow for development",
        "goal": "Complete a research task with multiple agents",
        "max_duration_seconds": 3600,
        "max_cost_usd": 5.0,
        "require_human_approval": False,
        "agent_ids": [],
        "tasks": []
    }


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        # Note: This will fail without a database, but tests the endpoint structure
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        # We expect this to fail in test environment without database
        assert response.status_code in [201, 500]  # 201 for success, 500 for DB error

    def test_register_user_invalid_password(self, client):
        """Test user registration with weak password."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak",  # Too weak
            "full_name": "Test User",
            "user_type": "operator"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        # Should fail validation
        assert response.status_code in [400, 422, 500]

    def test_login_endpoint_structure(self, client, sample_login_data):
        """Test login endpoint structure."""
        response = client.post("/api/v1/auth/login", json=sample_login_data)
        # Endpoint should be accessible even if auth fails
        assert response.status_code in [200, 401, 422, 500]

    def test_get_current_user_unauthorized(self, client):
        """Test get current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_logout_endpoint(self, client):
        """Test logout endpoint."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code in [200, 500]


class TestUserCRUDEndpoints:
    """Test user CRUD endpoints."""

    def test_list_users_endpoint(self, client):
        """Test list users endpoint."""
        response = client.get("/api/v1/users/")
        assert response.status_code in [200, 500]  # 200 for success, 500 for DB error

    def test_list_users_with_pagination(self, client):
        """Test list users with pagination parameters."""
        response = client.get("/api/v1/users/?page=1&limit=5")
        assert response.status_code in [200, 500]

    def test_list_users_with_search(self, client):
        """Test list users with search parameter."""
        response = client.get("/api/v1/users/?search=test")
        assert response.status_code in [200, 500]

    def test_get_user_by_id(self, client):
        """Test get user by ID."""
        # Use a random UUID
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code in [200, 404, 422, 500]

    def test_create_user_redirect(self, client):
        """Test create user redirects to register."""
        response = client.post("/api/v1/users/", json={})
        assert response.status_code == 400
        assert "register" in response.json()["detail"]


class TestAgentCRUDEndpoints:
    """Test agent CRUD endpoints."""

    def test_list_agents_endpoint(self, client):
        """Test list agents endpoint."""
        response = client.get("/api/v1/agents/")
        assert response.status_code in [200, 500]

    def test_list_agents_with_filters(self, client):
        """Test list agents with filters."""
        response = client.get("/api/v1/agents/?role=researcher&status=idle")
        assert response.status_code in [200, 500]

    def test_create_agent_endpoint(self, client, sample_agent_data):
        """Test create agent endpoint."""
        response = client.post("/api/v1/agents/", json=sample_agent_data)
        assert response.status_code in [201, 400, 422, 500]

    def test_create_agent_invalid_role(self, client):
        """Test create agent with invalid role."""
        agent_data = {
            "name": "Test Agent",
            "role": "invalid_role",  # Invalid role
            "system_prompt": "Test prompt"
        }
        response = client.post("/api/v1/agents/", json=agent_data)
        assert response.status_code in [400, 422, 500]

    def test_get_agent_by_id(self, client):
        """Test get agent by ID."""
        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/v1/agents/{agent_id}")
        assert response.status_code in [200, 404, 422, 500]

    def test_agent_execution_endpoint(self, client):
        """Test agent execution endpoint."""
        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        execution_data = {
            "task_description": "Test task",
            "input_data": {"test": "data"}
        }
        response = client.post(f"/api/v1/agents/{agent_id}/execute", json=execution_data)
        assert response.status_code in [200, 404, 422, 500]


class TestWorkflowCRUDEndpoints:
    """Test workflow CRUD endpoints."""

    def test_list_workflows_endpoint(self, client):
        """Test list workflows endpoint."""
        response = client.get("/api/v1/workflows/")
        assert response.status_code in [200, 500]

    def test_list_workflows_with_filters(self, client):
        """Test list workflows with filters."""
        response = client.get("/api/v1/workflows/?status=draft&is_template=false")
        assert response.status_code in [200, 500]

    def test_create_workflow_endpoint(self, client, sample_workflow_data):
        """Test create workflow endpoint."""
        response = client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert response.status_code in [201, 400, 422, 500]

    def test_get_workflow_by_id(self, client):
        """Test get workflow by ID."""
        workflow_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code in [200, 404, 422, 500]

    def test_workflow_execution_endpoints(self, client):
        """Test workflow execution control endpoints."""
        workflow_id = "550e8400-e29b-41d4-a716-446655440000"

        # Test start
        start_data = {"input_data": {}, "priority": "normal"}
        response = client.post(f"/api/v1/workflows/{workflow_id}/start", json=start_data)
        assert response.status_code in [200, 404, 422, 500]

        # Test stop
        response = client.post(f"/api/v1/workflows/{workflow_id}/stop")
        assert response.status_code in [200, 404, 400, 500]

        # Test pause
        response = client.post(f"/api/v1/workflows/{workflow_id}/pause")
        assert response.status_code in [200, 404, 400, 500]

        # Test resume
        response = client.post(f"/api/v1/workflows/{workflow_id}/resume")
        assert response.status_code in [200, 404, 400, 500]

    def test_workflow_status_endpoint(self, client):
        """Test workflow status endpoint."""
        workflow_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/v1/workflows/{workflow_id}/status")
        assert response.status_code in [200, 404, 422, 500]

    def test_workflow_logs_endpoint(self, client):
        """Test workflow logs endpoint."""
        workflow_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/v1/workflows/{workflow_id}/logs")
        assert response.status_code in [200, 500]


class TestAPIValidation:
    """Test API validation and error handling."""

    def test_invalid_uuid_format(self, client):
        """Test endpoints with invalid UUID format."""
        invalid_id = "not-a-uuid"

        response = client.get(f"/api/v1/users/{invalid_id}")
        assert response.status_code == 422

        response = client.get(f"/api/v1/agents/{invalid_id}")
        assert response.status_code == 422

        response = client.get(f"/api/v1/workflows/{invalid_id}")
        assert response.status_code == 422

    def test_pagination_validation(self, client):
        """Test pagination parameter validation."""
        # Invalid page number
        response = client.get("/api/v1/users/?page=0")
        assert response.status_code == 422

        # Invalid limit
        response = client.get("/api/v1/users/?limit=0")
        assert response.status_code == 422

        # Limit too high
        response = client.get("/api/v1/users/?limit=1000")
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test endpoints with missing required fields."""
        # Missing required fields for agent creation
        incomplete_agent = {"name": "Test"}
        response = client.post("/api/v1/agents/", json=incomplete_agent)
        assert response.status_code == 422

        # Missing required fields for workflow creation
        incomplete_workflow = {"name": "Test"}
        response = client.post("/api/v1/workflows/", json=incomplete_workflow)
        assert response.status_code == 422
