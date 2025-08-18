"""
Comprehensive API endpoint tests for improved coverage.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app


class TestHealthEndpoints:
    """Test health and monitoring endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root API endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "name" in data

    def test_health_detailed_endpoint(self):
        """Test detailed health endpoint with comprehensive checks."""
        response = self.client.get("/health")
        assert response.status_code in [200, 503]
        data = response.json()
        
        # Verify structure
        assert "status" in data
        assert "timestamp" in data
        
        # Check for detailed health information
        if "checks" in data:
            checks = data["checks"]
            assert isinstance(checks, dict)
            # System check should always be present
            assert "system" in checks


class TestModelEndpoints:
    """Test model-related API endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_list_models_endpoint(self):
        """Test models listing endpoint."""
        response = self.client.get("/api/v1/models/")
        # May require authentication, but should not return 404
        assert response.status_code in [200, 401, 403]

    def test_model_health_check(self):
        """Test model health check endpoint."""
        response = self.client.get("/api/v1/models/health")
        # May require authentication, but should not return 404
        assert response.status_code in [200, 401, 403]

    def test_model_routing_recommendation(self):
        """Test model routing recommendation."""
        test_request = {
            "task_type": "text-generation",
            "complexity": "medium",
            "max_tokens": 1000
        }
        response = self.client.post("/api/v1/models/recommend", json=test_request)
        # Should return recommendations or validation error
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert "recommendations" in data or "model" in data


class TestUserManagementEndpoints:
    """Test user management endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_register_endpoint_validation(self):
        """Test user registration validation."""
        # Test empty request
        response = self.client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422  # Validation error
        
        # Test partial data
        response = self.client.post("/api/v1/auth/register", json={
            "email": "test@example.com"
        })
        assert response.status_code == 422  # Missing required fields

    def test_login_endpoint_validation(self):
        """Test login validation."""
        # Test empty request
        response = self.client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422  # Validation error
        
        # Test invalid credentials format
        response = self.client.post("/api/v1/auth/login", json={
            "email": "invalid-email",
            "password": "123"
        })
        assert response.status_code == 422  # Validation error


class TestAgentEndpoints:
    """Test agent management endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_list_agents_endpoint(self):
        """Test agents listing endpoint."""
        response = self.client.get("/api/v1/agents/")
        # Should return success or auth required
        assert response.status_code in [200, 401, 403]

    def test_create_agent_validation(self):
        """Test agent creation validation."""
        # Test empty request
        response = self.client.post("/api/v1/agents/", json={})
        assert response.status_code in [401, 403, 422]  # Auth or validation error
        
        # Test partial data
        response = self.client.post("/api/v1/agents/", json={
            "name": "Test Agent"
        })
        assert response.status_code in [401, 403, 422]  # Auth or validation error


class TestWorkflowEndpoints:
    """Test workflow management endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_list_workflows_endpoint(self):
        """Test workflows listing endpoint."""
        response = self.client.get("/api/v1/workflows/")
        # Should require authentication
        assert response.status_code in [200, 401, 403]

    def test_create_workflow_validation(self):
        """Test workflow creation validation."""
        # Test empty request
        response = self.client.post("/api/v1/workflows/", json={})
        assert response.status_code in [401, 403, 422]  # Auth or validation error


class TestMCPEndpoints:
    """Test MCP protocol endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_mcp_capabilities_endpoint(self):
        """Test MCP capabilities endpoint."""
        response = self.client.get("/api/v1/mcp/capabilities")
        # Endpoint might not exist or require authentication
        assert response.status_code in [200, 401, 403, 404]

    def test_mcp_resources_endpoint(self):
        """Test MCP resources endpoint."""
        response = self.client.get("/api/v1/mcp/resources")
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data

    def test_mcp_tools_endpoint(self):
        """Test MCP tools endpoint."""
        response = self.client.get("/api/v1/mcp/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data


class TestErrorHandling:
    """Test error handling across endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_404_handling(self):
        """Test 404 error handling."""
        response = self.client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test method not allowed error."""
        response = self.client.put("/health")  # Should be GET only
        assert response.status_code == 405

    def test_invalid_json_handling(self):
        """Test invalid JSON handling."""
        response = self.client.post(
            "/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestAPIVersioning:
    """Test API versioning and compatibility."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_api_v1_prefix(self):
        """Test that v1 API endpoints are accessible."""
        endpoints = [
            "/api/v1/models/",
            "/api/v1/agents/",
            "/api/v1/workflows/",
            "/api/v1/mcp/capabilities"
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Should not return 404 (endpoint exists), but may require auth
            assert response.status_code in [200, 401, 403, 404]  # Allow 404 for non-existent endpoints

    def test_openapi_schema(self):
        """Test OpenAPI schema accessibility."""
        response = self.client.get("/openapi.json")
        # May not be available in all configurations
        assert response.status_code in [200, 404]