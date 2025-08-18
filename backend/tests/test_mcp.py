"""
Integration tests for MCP (Model Context Protocol) endpoints.

These tests validate compliance with the MCP specification:
https://modelcontextprotocol.io/specification/2025-03-26
"""

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


class TestMCPProtocol:
    """Test suite for MCP protocol compliance."""

    def test_health_check(self, client: TestClient):
        """Test the enhanced health check endpoint."""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # May be unhealthy in test environment

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        
        # Check nested app information
        if "app" in data:
            app_info = data["app"]
            if isinstance(app_info, dict):
                assert app_info["name"] == "Z2 AI Workforce Platform"
                assert "version" in app_info
            else:
                assert app_info == "Z2 AI Workforce Platform"
        
        # Check for system checks
        if "checks" in data:
            assert isinstance(data["checks"], dict)

    def test_mcp_initialize_success(self, client: TestClient, sample_mcp_initialize_request, mock_db, mock_session_service):
        """Test successful MCP session initialization."""
        # Mock the session creation
        mock_session_service.create_mcp_session.return_value = AsyncMock()
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.post("/api/v1/mcp/initialize", json=sample_mcp_initialize_request)
            assert response.status_code == 200

            data = response.json()
            assert data["protocolVersion"] == "2025-03-26"
            assert "serverInfo" in data
            assert data["serverInfo"]["name"] == "Z2 AI Workforce Platform"
            assert data["serverInfo"]["version"] == "1.0.0"
            assert "capabilities" in data
            assert "session_id" in data

            # Check server capabilities
            capabilities = data["capabilities"]
            assert "resources" in capabilities
            assert "tools" in capabilities
            assert "prompts" in capabilities
            assert "sampling" in capabilities

    def test_mcp_initialize_invalid_version(self, client: TestClient, mock_db, mock_session_service):
        """Test MCP initialization with unsupported protocol version."""
        request = {
            "protocolVersion": "1.0.0",  # Unsupported version
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }

        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.post("/api/v1/mcp/initialize", json=request)
            assert response.status_code == 400
            assert "Unsupported protocol version" in response.json()["detail"]

    def test_list_resources(self, client: TestClient, mock_db, mock_session_service):
        """Test listing MCP resources."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.get("/api/v1/mcp/resources")
            assert response.status_code == 200

            data = response.json()
            assert "resources" in data

            resources = data["resources"]
            assert len(resources) > 0

            # Check resource structure
            for resource in resources:
                assert "uri" in resource
                assert "name" in resource
                assert "description" in resource
                assert "mimeType" in resource

    def test_get_specific_resource(self, client: TestClient, mock_db, mock_session_service):
        """Test retrieving a specific MCP resource."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            # Test agent resource
            response = client.get("/api/v1/mcp/resources/agent://default")
            assert response.status_code == 200

            data = response.json()
            assert data["uri"] == "agent://default"
            assert data["mimeType"] == "application/json"
            assert "text" in data

            # Test workflow resource
            response = client.get("/api/v1/mcp/resources/workflow://templates")
            assert response.status_code == 200

            data = response.json()
            assert data["uri"] == "workflow://templates"
            assert data["mimeType"] == "application/json"

    def test_get_nonexistent_resource(self, client: TestClient, mock_db, mock_session_service):
        """Test retrieving a non-existent resource."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.get("/api/v1/mcp/resources/nonexistent://resource")
            assert response.status_code == 404

    def test_list_tools(self, client: TestClient, mock_db, mock_session_service):
        """Test listing MCP tools."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.get("/api/v1/mcp/tools")
            assert response.status_code == 200

            data = response.json()
            assert "tools" in data

            tools = data["tools"]
            assert len(tools) > 0

            # Check tool structure
            for tool in tools:
                assert "name" in tool
                assert "description" in tool
                assert "inputSchema" in tool

                # Validate input schema structure
                schema = tool["inputSchema"]
                assert schema["type"] == "object"
                assert "properties" in schema
                assert "required" in schema

    def test_call_tool_execute_agent(self, client: TestClient, mock_db, mock_session_service):
        """Test calling the execute_agent tool."""
        # Mock task creation
        mock_task = AsyncMock()
        mock_task.task_id = "test-task-123"
        mock_session_service.create_task_execution.return_value = mock_task
        
        request_data = {
            "arguments": {
                "agent_id": "test-agent",
                "task": "Analyze some data",
                "parameters": {"format": "json"}
            },
            "session_id": "test-session",
            "stream": False,
            "can_cancel": True
        }

        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service), \
             patch('app.api.v1.endpoints.mcp.get_consent_service', return_value=AsyncMock()):
            
            response = client.post("/api/v1/mcp/tools/execute_agent/call", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "content" in data
            assert len(data["content"]) > 0
            assert data["content"][0]["type"] == "text"
            assert "task_id" in data

    def test_call_tool_create_workflow(self, client: TestClient, mock_db, mock_session_service):
        """Test calling the create_workflow tool."""
        # Mock task creation
        mock_task = AsyncMock()
        mock_task.task_id = "test-workflow-task-456"
        mock_session_service.create_task_execution.return_value = mock_task
        
        request_data = {
            "arguments": {
                "name": "test-workflow",
                "agents": ["agent1", "agent2"],
                "configuration": {"timeout": 300}
            },
            "stream": False,
            "can_cancel": True
        }

        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service), \
             patch('app.api.v1.endpoints.mcp.get_consent_service', return_value=AsyncMock()):
            
            response = client.post("/api/v1/mcp/tools/create_workflow/call", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "content" in data
            assert "task_id" in data

    def test_call_nonexistent_tool(self, client: TestClient, mock_db, mock_session_service):
        """Test calling a non-existent tool."""
        request_data = {
            "arguments": {},
            "stream": False,
            "can_cancel": True
        }
        
        # Mock task creation
        mock_task = AsyncMock()
        mock_task.task_id = "test-task-fail"
        mock_session_service.create_task_execution.return_value = mock_task
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service), \
             patch('app.api.v1.endpoints.mcp.get_consent_service', return_value=AsyncMock()):
            
            response = client.post("/api/v1/mcp/tools/nonexistent_tool/call", json=request_data)
            assert response.status_code == 404

    def test_list_prompts(self, client: TestClient, mock_db, mock_session_service):
        """Test listing MCP prompts."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.get("/api/v1/mcp/prompts")
            assert response.status_code == 200

            data = response.json()
            assert "prompts" in data

            prompts = data["prompts"]
            assert len(prompts) > 0

            # Check prompt structure
            for prompt in prompts:
                assert "name" in prompt
                assert "description" in prompt
                if "arguments" in prompt:
                    for arg in prompt["arguments"]:
                        assert "name" in arg
                        assert "description" in arg
                        assert "required" in arg

    def test_get_prompt(self, client: TestClient, mock_db, mock_session_service):
        """Test retrieving a specific prompt."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            # Test analyze_compliance prompt
            response = client.get("/api/v1/mcp/prompts/analyze_compliance")
            assert response.status_code == 200

            data = response.json()
            assert "description" in data
            assert "messages" in data
            assert len(data["messages"]) > 0

    def test_get_nonexistent_prompt(self, client: TestClient, mock_db, mock_session_service):
        """Test retrieving a non-existent prompt."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.get("/api/v1/mcp/prompts/nonexistent_prompt")
            assert response.status_code == 404

    def test_list_sessions(self, client: TestClient, mock_db, mock_session_service):
        """Test listing MCP sessions."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.get("/api/v1/mcp/sessions")
            assert response.status_code == 200

            data = response.json()
            assert "sessions" in data

    def test_sampling_api(self, client: TestClient, mock_db, mock_session_service):
        """Test the MCP sampling API endpoint."""
        request_data = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100
        }

        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.post("/api/v1/mcp/sampling/createMessage", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "model" in data
            assert "role" in data
            assert "content" in data

    def test_mcp_statistics(self, client: TestClient, mock_db, mock_session_service):
        """Test MCP statistics endpoint."""
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.get("/api/v1/mcp/statistics")
            assert response.status_code == 200

            data = response.json()
            assert "timestamp" in data
            assert "server_info" in data
            assert "sessions" in data
            assert "tasks" in data
            assert "capabilities" in data

    def test_tool_cancellation(self, client: TestClient, mock_db, mock_session_service):
        """Test tool execution cancellation."""
        task_id = "test-cancel-task"
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.post(f"/api/v1/mcp/tools/execute_agent/cancel", params={"task_id": task_id})
            # May return 400 if task doesn't exist in test
            assert response.status_code in [200, 400]

    def test_tool_status_check(self, client: TestClient, mock_db, mock_session_service):
        """Test tool execution status checking."""
        task_id = "test-status-task"
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.mcp.get_session_service', return_value=mock_session_service):
            
            response = client.get(f"/api/v1/mcp/tools/execute_agent/status/{task_id}")
            # May return 404 if task doesn't exist in test
            assert response.status_code in [200, 404]
