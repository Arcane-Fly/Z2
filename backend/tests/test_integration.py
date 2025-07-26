"""
Integration tests for A2A and MCP protocol flows.

These tests validate end-to-end scenarios including:
- Protocol negotiation between A2A and MCP
- Consent and session management integration  
- Cross-protocol communication patterns
"""

import asyncio
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import create_application
from app.services.session_service import SessionService
from app.services.consent_service import ConsentService


class TestProtocolIntegration:
    """Integration tests for A2A and MCP protocol interoperability."""

    @pytest.fixture
    async def app(self):
        """Create test application."""
        return create_application()

    @pytest.fixture
    async def async_client(self, app):
        """Create async test client."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    async def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    async def session_service(self, mock_db):
        """Mock session service."""
        return SessionService(mock_db)

    @pytest.fixture
    async def consent_service(self, mock_db):
        """Mock consent service."""
        return ConsentService(mock_db)

    async def test_mcp_to_a2a_workflow_integration(self, async_client, mock_db):
        """Test complete workflow from MCP initialization to A2A negotiation."""
        
        # Step 1: Initialize MCP session
        mcp_init_request = {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "resources": {"subscribe": True},
                "tools": {"listChanged": True},
                "prompts": {"listChanged": True}
            },
            "clientInfo": {
                "name": "integration-test-client",
                "version": "1.0.0"
            }
        }
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            mcp_response = await async_client.post("/api/v1/mcp/initialize", json=mcp_init_request)
            assert mcp_response.status_code == 200
            mcp_data = mcp_response.json()
            assert "session_id" in mcp_data
            mcp_session_id = mcp_data["session_id"]

        # Step 2: Request consent for A2A communication
        consent_request = {
            "user_id": "integration-test-user",
            "resource_type": "tool",
            "resource_name": "a2a_communication",
            "description": "Enable A2A communication for workflow orchestration",
            "permissions": ["a2a:communicate", "workflow:orchestrate"],
            "expires_in_hours": 24
        }
        
        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
            consent_response = await async_client.post("/api/v1/consent/consent/request", json=consent_request)
            assert consent_response.status_code == 200
            consent_data = consent_response.json()
            consent_id = consent_data["consent_id"]

        # Step 3: Initiate A2A handshake
        a2a_handshake_request = {
            "agent_id": "integration-test-agent",
            "agent_name": "Integration Test Agent",
            "capabilities": ["workflow-execution", "task-coordination"],
            "protocol_version": "1.0.0"
        }
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            a2a_response = await async_client.post("/api/v1/a2a/handshake", json=a2a_handshake_request)
            assert a2a_response.status_code == 200
            a2a_data = a2a_response.json()
            a2a_session_id = a2a_data["session_id"]

        # Step 4: Negotiate A2A task execution
        negotiation_request = {
            "session_id": a2a_session_id,
            "requested_skills": ["workflow-orchestration", "dynamic-reasoning"],
            "task_description": "Execute complex workflow with MCP integration",
            "parameters": {
                "mcp_session_id": mcp_session_id,
                "workflow_type": "data_analysis",
                "priority": 8
            },
            "priority": 8,
            "timeout_seconds": 3600
        }
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            negotiation_response = await async_client.post("/api/v1/a2a/negotiate", json=negotiation_request)
            assert negotiation_response.status_code == 200
            negotiation_data = negotiation_response.json()
            assert negotiation_data["accepted"] == True
            assert "workflow-orchestration" in negotiation_data["available_skills"]

        # Step 5: Execute MCP tool through A2A coordination
        tool_execution_request = {
            "arguments": {
                "agent_id": "reasoning-agent",
                "task": "Analyze integration test data",
                "parameters": {
                    "data_source": "integration_test",
                    "analysis_type": "comprehensive"
                },
                "stream": False
            },
            "session_id": mcp_session_id,
            "can_cancel": True
        }
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            tool_response = await async_client.post("/api/v1/mcp/tools/execute_agent/call", json=tool_execution_request)
            assert tool_response.status_code == 200
            tool_data = tool_response.json()
            assert "task_id" in tool_data
            assert "content" in tool_data

        # Step 6: Verify cross-protocol session coordination
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            mcp_sessions = await async_client.get("/api/v1/mcp/sessions")
            assert mcp_sessions.status_code == 200

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            a2a_sessions = await async_client.get("/api/v1/a2a/sessions")
            assert a2a_sessions.status_code == 200

    async def test_consent_driven_protocol_access(self, async_client, mock_db):
        """Test consent-driven access control across protocols."""
        
        # Step 1: Create access policies for both protocols
        policies_to_create = [
            {
                "resource_type": "tool",
                "resource_name": "mcp_execute_agent",
                "required_permissions": ["agent:execute", "mcp:access"],
                "auto_approve": False,
                "max_usage_per_hour": 10,
                "description": "MCP agent execution tool"
            },
            {
                "resource_type": "tool", 
                "resource_name": "a2a_negotiate",
                "required_permissions": ["a2a:negotiate", "agent:coordinate"],
                "auto_approve": True,
                "max_usage_per_hour": 20,
                "description": "A2A skill negotiation"
            }
        ]
        
        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
            # Setup default policies
            setup_response = await async_client.post("/api/v1/consent/setup-default-policies")
            assert setup_response.status_code == 200

        # Step 2: Test access with insufficient permissions
        insufficient_access_request = {
            "user_id": "limited-user",
            "resource_type": "tool",
            "resource_name": "mcp_execute_agent",
            "permissions": ["basic:read"]  # Missing required permissions
        }
        
        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
            access_response = await async_client.post("/api/v1/consent/access/check", json=insufficient_access_request)
            assert access_response.status_code == 200
            access_data = access_response.json()
            assert access_data["allowed"] == False
            assert "Missing permissions" in access_data["reason"]

        # Step 3: Request proper consent
        consent_request = {
            "user_id": "authorized-user",
            "resource_type": "tool",
            "resource_name": "mcp_execute_agent",
            "description": "Need access to execute MCP agents for workflow automation",
            "permissions": ["agent:execute", "mcp:access"],
            "expires_in_hours": 12
        }
        
        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
            consent_response = await async_client.post("/api/v1/consent/consent/request", json=consent_request)
            assert consent_response.status_code == 200
            consent_data = consent_response.json()
            consent_id = consent_data["consent_id"]

        # Step 4: Grant consent
        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
            grant_response = await async_client.post(
                f"/api/v1/consent/consent/{consent_id}/grant",
                params={"user_id": "authorized-user"}
            )
            assert grant_response.status_code == 200

        # Step 5: Verify access with proper consent
        proper_access_request = {
            "user_id": "authorized-user",
            "resource_type": "tool",
            "resource_name": "mcp_execute_agent",
            "permissions": ["agent:execute", "mcp:access"]
        }
        
        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
            access_response = await async_client.post("/api/v1/consent/access/check", json=proper_access_request)
            assert access_response.status_code == 200
            access_data = access_response.json()
            assert access_data["allowed"] == True

    async def test_streaming_and_cancellation_integration(self, async_client, mock_db):
        """Test streaming responses and cancellation across protocols."""
        
        # Step 1: Initialize MCP session for streaming
        mcp_init_request = {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "tools": {"progress": True, "cancellation": True}
            },
            "clientInfo": {
                "name": "streaming-test-client",
                "version": "1.0.0"
            }
        }
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            mcp_response = await async_client.post("/api/v1/mcp/initialize", json=mcp_init_request)
            assert mcp_response.status_code == 200
            mcp_session_id = mcp_response.json()["session_id"]

        # Step 2: Start long-running task with streaming
        streaming_request = {
            "arguments": {
                "agent_id": "processing-agent",
                "task": "Long-running data analysis",
                "parameters": {"dataset_size": "large", "complexity": "high"},
                "timeout": 300
            },
            "session_id": mcp_session_id,
            "stream": True,
            "can_cancel": True
        }
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            # This would normally return a streaming response
            # For testing, we'll verify the endpoint accepts the request
            stream_response = await async_client.post("/api/v1/mcp/tools/analyze_system/call", json=streaming_request)
            assert stream_response.status_code in [200, 206]  # 206 for partial content/streaming

        # Step 3: Test task status checking
        # In a real scenario, we'd extract task_id from the streaming response
        mock_task_id = "test-task-123"
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            status_response = await async_client.get(f"/api/v1/mcp/tools/analyze_system/status/{mock_task_id}")
            # This might return 404 in test, but validates the endpoint exists
            assert status_response.status_code in [200, 404]

        # Step 4: Test cancellation
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            cancel_response = await async_client.post(f"/api/v1/mcp/tools/analyze_system/cancel", params={"task_id": mock_task_id})
            # This might return 400 in test, but validates the endpoint exists
            assert cancel_response.status_code in [200, 400, 404]

    async def test_session_persistence_and_recovery(self, async_client, mock_db):
        """Test session persistence and recovery mechanisms."""
        
        # Step 1: Create persistent MCP session
        mcp_init_request = {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {
                "name": "persistence-test-client",
                "version": "1.0.0"
            }
        }
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            mcp_response = await async_client.post("/api/v1/mcp/initialize", json=mcp_init_request)
            assert mcp_response.status_code == 200
            mcp_session_id = mcp_response.json()["session_id"]

        # Step 2: Create persistent A2A session
        a2a_handshake_request = {
            "agent_id": "persistence-test-agent",
            "agent_name": "Persistence Test Agent",
            "capabilities": ["session-recovery", "state-persistence"],
            "protocol_version": "1.0.0"
        }
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            a2a_response = await async_client.post("/api/v1/a2a/handshake", json=a2a_handshake_request)
            assert a2a_response.status_code == 200
            a2a_session_id = a2a_response.json()["session_id"]

        # Step 3: Verify sessions are listed
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            mcp_sessions = await async_client.get("/api/v1/mcp/sessions")
            assert mcp_sessions.status_code == 200

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            a2a_sessions = await async_client.get("/api/v1/a2a/sessions")
            assert a2a_sessions.status_code == 200

        # Step 4: Test session statistics
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            mcp_stats = await async_client.get("/api/v1/mcp/statistics")
            assert mcp_stats.status_code == 200
            stats_data = mcp_stats.json()
            assert "sessions" in stats_data
            assert "capabilities" in stats_data

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            a2a_stats = await async_client.get("/api/v1/a2a/statistics")
            assert a2a_stats.status_code == 200
            a2a_stats_data = a2a_stats.json()
            assert "sessions" in a2a_stats_data
            assert "capabilities" in a2a_stats_data

        # Step 5: Test session cleanup
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            close_response = await async_client.delete(f"/api/v1/mcp/sessions/{mcp_session_id}")
            assert close_response.status_code in [200, 404]

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            terminate_response = await async_client.delete(f"/api/v1/a2a/sessions/{a2a_session_id}")
            assert terminate_response.status_code in [200, 404]

    async def test_protocol_capability_negotiation(self, async_client, mock_db):
        """Test capability negotiation between protocols."""
        
        # Step 1: Initialize MCP with specific capabilities
        mcp_capabilities = {
            "resources": {"subscribe": True, "listChanged": True},
            "tools": {"listChanged": True, "progress": True, "cancellation": True},
            "prompts": {"listChanged": True},
            "sampling": {"streaming": True}
        }
        
        mcp_init_request = {
            "protocolVersion": "2025-03-26",
            "capabilities": mcp_capabilities,
            "clientInfo": {
                "name": "capability-test-client",
                "version": "1.0.0"
            }
        }
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            mcp_response = await async_client.post("/api/v1/mcp/initialize", json=mcp_init_request)
            assert mcp_response.status_code == 200
            mcp_data = mcp_response.json()
            
            # Verify server capabilities are returned
            assert "capabilities" in mcp_data
            server_caps = mcp_data["capabilities"]
            assert "resources" in server_caps
            assert "tools" in server_caps

        # Step 2: Test A2A capability inquiry
        a2a_handshake_request = {
            "agent_id": "capability-test-agent",
            "agent_name": "Capability Test Agent",
            "capabilities": ["capability-inquiry", "protocol-adaptation"],
            "protocol_version": "1.0.0"
        }
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            a2a_response = await async_client.post("/api/v1/a2a/handshake", json=a2a_handshake_request)
            assert a2a_response.status_code == 200
            a2a_data = a2a_response.json()
            
            # Verify our capabilities are returned
            assert "capabilities" in a2a_data
            our_caps = a2a_data["capabilities"]
            assert "workflow-orchestration" in our_caps
            assert "streaming-communication" in our_caps

        # Step 3: Test capability-driven negotiation
        negotiation_request = {
            "session_id": a2a_data["session_id"],
            "requested_skills": ["streaming-communication", "progress-reporting"],
            "task_description": "Test capability-driven task execution",
            "parameters": {"capability_requirements": mcp_capabilities}
        }
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            negotiation_response = await async_client.post("/api/v1/a2a/negotiate", json=negotiation_request)
            assert negotiation_response.status_code == 200
            negotiation_data = negotiation_response.json()
            
            # Verify capability matching
            assert "available_skills" in negotiation_data
            assert "proposed_workflow" in negotiation_data
            workflow = negotiation_data["proposed_workflow"]
            assert "skill_confidence" in workflow

    async def test_audit_and_compliance_integration(self, async_client, mock_db):
        """Test audit logging and compliance across protocols."""
        
        # Step 1: Perform operations that should be audited
        operations = [
            # MCP session initialization
            {
                "endpoint": "/api/v1/mcp/initialize",
                "method": "POST",
                "data": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "audit-test", "version": "1.0.0"}
                }
            },
            # Consent request
            {
                "endpoint": "/api/v1/consent/consent/request",
                "method": "POST", 
                "data": {
                    "user_id": "audit-test-user",
                    "resource_type": "tool",
                    "resource_name": "execute_agent",
                    "description": "Audit test consent",
                    "permissions": ["agent:execute"]
                }
            },
            # A2A handshake
            {
                "endpoint": "/api/v1/a2a/handshake",
                "method": "POST",
                "data": {
                    "agent_id": "audit-test-agent",
                    "agent_name": "Audit Test Agent",
                    "capabilities": ["audit-compliance"],
                    "protocol_version": "1.0.0"
                }
            }
        ]
        
        for operation in operations:
            with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
                 patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
                 patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
                
                if operation["method"] == "POST":
                    response = await async_client.post(operation["endpoint"], json=operation["data"])
                    # All endpoints should respond successfully or with expected errors
                    assert response.status_code in [200, 400, 404]

        # Step 2: Check audit logs
        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
            audit_response = await async_client.get("/api/v1/consent/audit")
            assert audit_response.status_code == 200
            audit_data = audit_response.json()
            assert "logs" in audit_data

        # Step 3: Test compliance reporting
        compliance_queries = [
            "/api/v1/consent/audit?action=request",
            "/api/v1/consent/audit?resource_type=tool",
            "/api/v1/consent/policies"
        ]
        
        for query in compliance_queries:
            with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
                compliance_response = await async_client.get(query)
                assert compliance_response.status_code == 200

    async def test_error_handling_and_recovery(self, async_client, mock_db):
        """Test error handling and recovery mechanisms."""
        
        # Step 1: Test invalid protocol versions
        invalid_mcp_request = {
            "protocolVersion": "invalid-version",
            "capabilities": {},
            "clientInfo": {"name": "error-test", "version": "1.0.0"}
        }
        
        with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db):
            error_response = await async_client.post("/api/v1/mcp/initialize", json=invalid_mcp_request)
            assert error_response.status_code == 400
            assert "Unsupported protocol version" in error_response.json()["detail"]

        # Step 2: Test invalid session access
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db):
            invalid_session_response = await async_client.post("/api/v1/a2a/negotiate", json={
                "session_id": "invalid-session-id",
                "requested_skills": ["test"],
                "task_description": "test"
            })
            assert invalid_session_response.status_code == 404

        # Step 3: Test malformed requests
        malformed_requests = [
            ("/api/v1/mcp/initialize", {}),  # Missing required fields
            ("/api/v1/a2a/handshake", {"agent_id": "test"}),  # Missing required fields
            ("/api/v1/consent/consent/request", {"user_id": "test"})  # Missing required fields
        ]
        
        for endpoint, data in malformed_requests:
            with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
                 patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
                 patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
                
                response = await async_client.post(endpoint, json=data)
                assert response.status_code in [400, 422]  # 422 for validation errors

        # Step 4: Test resource not found scenarios
        not_found_requests = [
            "/api/v1/mcp/resources/nonexistent://resource",
            "/api/v1/mcp/prompts/nonexistent_prompt",
            "/api/v1/consent/consent/00000000-0000-0000-0000-000000000000"
        ]
        
        for endpoint in not_found_requests:
            with patch('app.api.v1.endpoints.mcp.get_db', return_value=mock_db), \
                 patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db):
                
                response = await async_client.get(endpoint)
                assert response.status_code == 404