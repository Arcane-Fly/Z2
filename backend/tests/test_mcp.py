"""
Integration tests for MCP (Model Context Protocol) endpoints.

These tests validate compliance with the MCP specification:
https://modelcontextprotocol.io/specification/2025-03-26
"""

from fastapi.testclient import TestClient


class TestMCPProtocol:
    """Test suite for MCP protocol compliance."""

    def test_health_check(self, client: TestClient):
        """Test the enhanced health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "Z2 AI Workforce Platform"
        assert "version" in data
        assert "timestamp" in data
        assert "environment" in data
        assert "checks" in data

    def test_mcp_initialize_success(self, client: TestClient, sample_mcp_initialize_request):
        """Test successful MCP session initialization."""
        response = client.post("/api/v1/mcp/initialize", json=sample_mcp_initialize_request)
        assert response.status_code == 200

        data = response.json()
        assert data["protocolVersion"] == "2025-03-26"
        assert "serverInfo" in data
        assert data["serverInfo"]["name"] == "Z2 AI Workforce Platform"
        assert data["serverInfo"]["version"] == "1.0.0"
        assert "capabilities" in data

        # Check server capabilities
        capabilities = data["capabilities"]
        assert "resources" in capabilities
        assert "tools" in capabilities
        assert "prompts" in capabilities
        assert "sampling" in capabilities

    def test_mcp_initialize_invalid_version(self, client: TestClient):
        """Test MCP initialization with unsupported protocol version."""
        request = {
            "protocolVersion": "1.0.0",  # Unsupported version
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }

        response = client.post("/api/v1/mcp/initialize", json=request)
        assert response.status_code == 400
        assert "Unsupported protocol version" in response.json()["detail"]

    def test_list_resources(self, client: TestClient):
        """Test listing MCP resources."""
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

    def test_get_specific_resource(self, client: TestClient):
        """Test retrieving a specific MCP resource."""
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

    def test_get_nonexistent_resource(self, client: TestClient):
        """Test retrieving a non-existent resource."""
        response = client.get("/api/v1/mcp/resources/nonexistent://resource")
        assert response.status_code == 404

    def test_list_tools(self, client: TestClient):
        """Test listing MCP tools."""
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

    def test_call_tool_execute_agent(self, client: TestClient):
        """Test calling the execute_agent tool."""
        request_data = {
            "agent_id": "test-agent",
            "task": "Analyze some data",
            "parameters": {"format": "json"}
        }

        response = client.post("/api/v1/mcp/tools/execute_agent/call", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "content" in data
        assert len(data["content"]) > 0
        assert data["content"][0]["type"] == "text"

    def test_call_tool_create_workflow(self, client: TestClient):
        """Test calling the create_workflow tool."""
        request_data = {
            "name": "test-workflow",
            "agents": ["agent1", "agent2"],
            "configuration": {"timeout": 300}
        }

        response = client.post("/api/v1/mcp/tools/create_workflow/call", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "content" in data

    def test_call_nonexistent_tool(self, client: TestClient):
        """Test calling a non-existent tool."""
        response = client.post("/api/v1/mcp/tools/nonexistent_tool/call", json={})
        assert response.status_code == 404

    def test_list_prompts(self, client: TestClient):
        """Test listing MCP prompts."""
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

    def test_get_prompt(self, client: TestClient):
        """Test retrieving a specific prompt."""
        # Test analyze_compliance prompt
        response = client.get("/api/v1/mcp/prompts/analyze_compliance")
        assert response.status_code == 200

        data = response.json()
        assert "description" in data
        assert "messages" in data
        assert len(data["messages"]) > 0

    def test_get_nonexistent_prompt(self, client: TestClient):
        """Test retrieving a non-existent prompt."""
        response = client.get("/api/v1/mcp/prompts/nonexistent_prompt")
        assert response.status_code == 404

    def test_list_sessions(self, client: TestClient):
        """Test listing MCP sessions."""
        # First initialize a session
        init_request = {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }
        client.post("/api/v1/mcp/initialize", json=init_request)

        # Then list sessions
        response = client.get("/api/v1/mcp/sessions")
        assert response.status_code == 200

        data = response.json()
        assert "sessions" in data

    def test_sampling_api(self, client: TestClient):
        """Test the MCP sampling API endpoint."""
        request_data = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100
        }

        response = client.post("/api/v1/mcp/sampling/createMessage", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "model" in data
        assert "role" in data
        assert "content" in data
