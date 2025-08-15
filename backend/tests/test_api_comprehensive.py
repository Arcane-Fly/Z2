"""
Tests for API endpoints with proper authentication.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json

from tests.utils import (
    create_test_client_with_auth,
    create_mock_user,
    create_sample_agent_data,
    create_sample_workflow_data,
    MockRedisClient
)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, unauthenticated_client):
        """Test root endpoint returns application info."""
        response = unauthenticated_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "Z2 AI Workforce Platform" in data["message"]
        
    def test_health_endpoint(self, unauthenticated_client):
        """Test health check endpoint."""
        response = unauthenticated_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        
    def test_health_detailed_endpoint(self, unauthenticated_client):
        """Test detailed health check endpoint."""
        with patch('app.utils.monitoring.get_system_metrics') as mock_metrics:
            mock_metrics.return_value = {
                "cpu_percent": 25.0,
                "memory_percent": 60.0,
                "disk_percent": 45.0
            }
            
            response = unauthenticated_client.get("/health/detailed")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "system_metrics" in data
            assert "database_status" in data


class TestAuthenticationEndpoints:
    """Test authentication endpoints with proper mocking."""
    
    @patch('app.services.auth_service.AuthService.register_user')
    def test_register_user_success(self, mock_register, unauthenticated_client):
        """Test successful user registration."""
        # Mock successful registration
        mock_user = create_mock_user()
        mock_register.return_value = mock_user
        
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User",
            "user_type": "operator"
        }
        
        response = unauthenticated_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        
    @patch('app.services.auth_service.AuthService.authenticate_user')
    @patch('app.utils.security.create_access_token')
    def test_login_success(self, mock_create_token, mock_auth, unauthenticated_client):
        """Test successful user login."""
        # Mock successful authentication
        mock_user = create_mock_user()
        mock_auth.return_value = mock_user
        mock_create_token.return_value = "test-jwt-token"
        
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        
        response = unauthenticated_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test-jwt-token"
        assert data["token_type"] == "bearer"
        assert "user" in data
        
    def test_login_invalid_credentials(self, unauthenticated_client):
        """Test login with invalid credentials."""
        with patch('app.services.auth_service.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            login_data = {
                "email": "test@example.com",
                "password": "WrongPassword"
            }
            
            response = unauthenticated_client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 401
            
    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        with patch('app.services.auth_service.AuthService.logout_user') as mock_logout:
            mock_logout.return_value = True
            
            response = authenticated_client.post("/api/v1/auth/logout")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Successfully logged out"
            
    def test_get_current_user(self, authenticated_client, sample_user):
        """Test getting current user info."""
        response = authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user.email
        assert data["full_name"] == sample_user.full_name


class TestAgentEndpoints:
    """Test agent management endpoints."""
    
    @patch('app.services.agent_service.AgentService.create_agent')
    def test_create_agent_success(self, mock_create, authenticated_client, sample_user):
        """Test successful agent creation."""
        agent_data = create_sample_agent_data()
        mock_agent = MagicMock()
        mock_agent.id = "test-agent-id"
        mock_agent.name = agent_data["name"]
        mock_agent.description = agent_data["description"]
        mock_agent.role = agent_data["role"]
        mock_agent.user_id = sample_user.id
        mock_create.return_value = mock_agent
        
        response = authenticated_client.post("/api/v1/agents", json=agent_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == agent_data["name"]
        assert data["role"] == agent_data["role"]
        
    @patch('app.services.agent_service.AgentService.list_agents')
    def test_list_agents_success(self, mock_list, authenticated_client, sample_user):
        """Test listing agents."""
        mock_agents = [
            MagicMock(id="agent-1", name="Agent 1", role="assistant", user_id=sample_user.id),
            MagicMock(id="agent-2", name="Agent 2", role="analyst", user_id=sample_user.id)
        ]
        mock_list.return_value = mock_agents
        
        response = authenticated_client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Agent 1"
        assert data[1]["name"] == "Agent 2"
        
    @patch('app.services.agent_service.AgentService.get_agent')
    def test_get_agent_by_id(self, mock_get, authenticated_client, sample_user):
        """Test getting agent by ID."""
        mock_agent = MagicMock()
        mock_agent.id = "test-agent-id"
        mock_agent.name = "Test Agent"
        mock_agent.role = "assistant"
        mock_agent.user_id = sample_user.id
        mock_get.return_value = mock_agent
        
        response = authenticated_client.get("/api/v1/agents/test-agent-id")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-agent-id"
        assert data["name"] == "Test Agent"
        
    @patch('app.services.agent_service.AgentService.get_agent')
    def test_get_agent_not_found(self, mock_get, authenticated_client):
        """Test getting non-existent agent."""
        mock_get.return_value = None
        
        response = authenticated_client.get("/api/v1/agents/non-existent-id")
        assert response.status_code == 404
        
    @patch('app.services.agent_service.AgentService.execute_agent')
    def test_execute_agent_success(self, mock_execute, authenticated_client, sample_user):
        """Test agent execution."""
        execution_data = {
            "input": "Test input for agent execution",
            "context": {"key": "value"}
        }
        
        mock_result = {
            "output": "Test agent response",
            "execution_id": "exec-123",
            "status": "completed"
        }
        mock_execute.return_value = mock_result
        
        response = authenticated_client.post(
            "/api/v1/agents/test-agent-id/execute",
            json=execution_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["output"] == "Test agent response"
        assert data["status"] == "completed"


class TestWorkflowEndpoints:
    """Test workflow management endpoints."""
    
    @patch('app.services.workflow_service.WorkflowService.create_workflow')
    def test_create_workflow_success(self, mock_create, authenticated_client, sample_user):
        """Test successful workflow creation."""
        workflow_data = create_sample_workflow_data()
        mock_workflow = MagicMock()
        mock_workflow.id = "test-workflow-id"
        mock_workflow.name = workflow_data["name"]
        mock_workflow.description = workflow_data["description"]
        mock_workflow.user_id = sample_user.id
        mock_create.return_value = mock_workflow
        
        response = authenticated_client.post("/api/v1/workflows", json=workflow_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == workflow_data["name"]
        assert data["description"] == workflow_data["description"]
        
    @patch('app.services.workflow_service.WorkflowService.list_workflows')
    def test_list_workflows_success(self, mock_list, authenticated_client, sample_user):
        """Test listing workflows."""
        mock_workflows = [
            MagicMock(id="wf-1", name="Workflow 1", user_id=sample_user.id),
            MagicMock(id="wf-2", name="Workflow 2", user_id=sample_user.id)
        ]
        mock_list.return_value = mock_workflows
        
        response = authenticated_client.get("/api/v1/workflows")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Workflow 1"
        assert data[1]["name"] == "Workflow 2"
        
    @patch('app.services.workflow_service.WorkflowService.execute_workflow')
    def test_execute_workflow_success(self, mock_execute, authenticated_client, sample_user):
        """Test workflow execution."""
        execution_data = {
            "inputs": {"step1_input": "test value"},
            "context": {"execution_mode": "async"}
        }
        
        mock_result = {
            "execution_id": "wf-exec-123",
            "status": "running",
            "steps": []
        }
        mock_execute.return_value = mock_result
        
        response = authenticated_client.post(
            "/api/v1/workflows/test-workflow-id/execute",
            json=execution_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["execution_id"] == "wf-exec-123"
        assert data["status"] == "running"


class TestMCPEndpoints:
    """Test MCP (Model Context Protocol) endpoints."""
    
    @patch('app.services.mcp_service.MCPService.initialize_session')
    def test_initialize_mcp_session(self, mock_init, authenticated_client):
        """Test MCP session initialization."""
        mock_session = {
            "session_id": "mcp-session-123",
            "status": "active",
            "capabilities": {
                "supports_resources": True,
                "supports_tools": True
            }
        }
        mock_init.return_value = mock_session
        
        response = authenticated_client.post("/api/v1/mcp/sessions")
        assert response.status_code == 201
        data = response.json()
        assert data["session_id"] == "mcp-session-123"
        assert data["status"] == "active"
        
    @patch('app.services.mcp_service.MCPService.list_resources')
    def test_list_mcp_resources(self, mock_list, authenticated_client):
        """Test listing MCP resources."""
        mock_resources = [
            {"uri": "resource://agents", "name": "Agents", "type": "collection"},
            {"uri": "resource://workflows", "name": "Workflows", "type": "collection"}
        ]
        mock_list.return_value = mock_resources
        
        response = authenticated_client.get("/api/v1/mcp/resources")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Agents"
        assert data[1]["name"] == "Workflows"
        
    @patch('app.services.mcp_service.MCPService.execute_tool')
    def test_execute_mcp_tool(self, mock_execute, authenticated_client):
        """Test MCP tool execution."""
        tool_data = {
            "tool_name": "agent_creator",
            "arguments": {
                "name": "Test Agent",
                "role": "assistant"
            }
        }
        
        mock_result = {
            "tool_name": "agent_creator",
            "result": {"agent_id": "new-agent-123"},
            "status": "completed"
        }
        mock_execute.return_value = mock_result
        
        response = authenticated_client.post("/api/v1/mcp/tools/execute", json=tool_data)
        assert response.status_code == 200
        data = response.json()
        assert data["tool_name"] == "agent_creator"
        assert data["status"] == "completed"


class TestModelEndpoints:
    """Test model management endpoints."""
    
    @patch('app.services.model_service.ModelService.list_available_models')
    def test_list_available_models(self, mock_list, authenticated_client):
        """Test listing available AI models."""
        mock_models = [
            {
                "id": "gpt-4",
                "provider": "openai",
                "name": "GPT-4",
                "capabilities": ["text", "function_calling"],
                "cost_per_token": 0.00003
            },
            {
                "id": "claude-3-sonnet",
                "provider": "anthropic", 
                "name": "Claude 3 Sonnet",
                "capabilities": ["text", "vision"],
                "cost_per_token": 0.000015
            }
        ]
        mock_list.return_value = mock_models
        
        response = authenticated_client.get("/api/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "gpt-4"
        assert data[1]["id"] == "claude-3-sonnet"
        
    @patch('app.services.model_service.ModelService.get_model_info')
    def test_get_model_info(self, mock_get, authenticated_client):
        """Test getting model information."""
        mock_model = {
            "id": "gpt-4",
            "provider": "openai",
            "name": "GPT-4",
            "description": "Latest GPT-4 model",
            "capabilities": ["text", "function_calling"],
            "context_length": 128000,
            "cost_per_token": 0.00003
        }
        mock_get.return_value = mock_model
        
        response = authenticated_client.get("/api/v1/models/gpt-4")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "gpt-4"
        assert data["name"] == "GPT-4"
        assert data["context_length"] == 128000


class TestAPIValidation:
    """Test API request validation."""
    
    def test_invalid_json_format(self, authenticated_client):
        """Test API response to invalid JSON."""
        response = authenticated_client.post(
            "/api/v1/agents",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
    def test_missing_required_fields(self, authenticated_client):
        """Test API response to missing required fields."""
        incomplete_data = {
            "name": "Test Agent"
            # Missing required fields like role, description
        }
        
        with patch('app.services.agent_service.AgentService.create_agent'):
            response = authenticated_client.post("/api/v1/agents", json=incomplete_data)
            assert response.status_code == 422
            
    def test_invalid_uuid_format(self, authenticated_client):
        """Test API response to invalid UUID format."""
        response = authenticated_client.get("/api/v1/agents/invalid-uuid-format")
        assert response.status_code == 422
        
    def test_pagination_validation(self, authenticated_client):
        """Test pagination parameter validation."""
        # Invalid page number
        response = authenticated_client.get("/api/v1/agents?page=-1&limit=10")
        assert response.status_code == 422
        
        # Invalid limit
        response = authenticated_client.get("/api/v1/agents?page=1&limit=0")
        assert response.status_code == 422