"""
Tests for A2A (Agent-to-Agent) protocol endpoints.
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app


class TestA2AProtocol:
    """Test A2A protocol implementation."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_a2a_handshake_success(self):
        """Test successful A2A handshake."""
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning", "analysis"],
            "protocol_version": "1.0.0"
        }
        
        response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert data["agent_name"] == "Z2 AI Workforce Platform"
        assert "capabilities" in data
        assert data["protocol_version"] == "1.0.0"
        assert "expires_at" in data

    def test_a2a_handshake_invalid_version(self):
        """Test A2A handshake with invalid protocol version."""
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning"],
            "protocol_version": "2.0.0"  # Unsupported version
        }
        
        response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)
        
        assert response.status_code == 400
        assert "Unsupported protocol version" in response.json()["detail"]

    def test_a2a_negotiate_success(self):
        """Test successful A2A skill negotiation."""
        # First establish handshake
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning"],
            "protocol_version": "1.0.0"
        }
        
        handshake_response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)
        session_id = handshake_response.json()["session_id"]
        
        # Now negotiate
        negotiation_data = {
            "session_id": session_id,
            "requested_skills": ["workflow-orchestration", "dynamic-reasoning"],
            "task_description": "Test task description",
            "parameters": {"test": "value"},
            "priority": 7
        }
        
        response = self.client.post("/api/v1/a2a/negotiate", json=negotiation_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "negotiation_id" in data
        assert "available_skills" in data
        assert "proposed_workflow" in data
        assert "estimated_duration" in data
        assert data["accepted"] is True

    def test_a2a_negotiate_invalid_session(self):
        """Test A2A negotiation with invalid session."""
        negotiation_data = {
            "session_id": "invalid-session-id",
            "requested_skills": ["reasoning"],
            "task_description": "Test task",
            "parameters": {}
        }
        
        response = self.client.post("/api/v1/a2a/negotiate", json=negotiation_data)
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_a2a_communicate_success(self):
        """Test successful A2A communication."""
        # Establish handshake first
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning"],
            "protocol_version": "1.0.0"
        }
        
        handshake_response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)
        session_id = handshake_response.json()["session_id"]
        
        # Send communication
        message_data = {
            "session_id": session_id,
            "message_type": "task_request",
            "payload": {"task": "test task", "data": "test data"}
        }
        
        response = self.client.post("/api/v1/a2a/communicate", json=message_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message_id" in data
        assert "status" in data
        assert "payload" in data
        assert data["status"] == "processed"

    def test_a2a_communicate_invalid_session(self):
        """Test A2A communication with invalid session."""
        message_data = {
            "session_id": "invalid-session-id",
            "message_type": "task_request",
            "payload": {"task": "test"}
        }
        
        response = self.client.post("/api/v1/a2a/communicate", json=message_data)
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_a2a_list_sessions(self):
        """Test listing active A2A sessions."""
        # Create a session first
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning"],
            "protocol_version": "1.0.0"
        }
        
        self.client.post("/api/v1/a2a/handshake", json=handshake_data)
        
        # List sessions
        response = self.client.get("/api/v1/a2a/sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "active_sessions" in data
        assert "active_streams" in data
        assert "sessions" in data
        assert data["active_sessions"] >= 1

    def test_a2a_terminate_session(self):
        """Test terminating an A2A session."""
        # Create a session first
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning"],
            "protocol_version": "1.0.0"
        }
        
        handshake_response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)
        session_id = handshake_response.json()["session_id"]
        
        # Terminate session
        response = self.client.delete(f"/api/v1/a2a/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "terminated"
        assert data["session_id"] == session_id

    def test_a2a_terminate_invalid_session(self):
        """Test terminating invalid session."""
        response = self.client.delete("/api/v1/a2a/sessions/invalid-session-id")
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_agent_discovery_endpoint(self):
        """Test the .well-known/agent.json discovery endpoint."""
        response = self.client.get("/.well-known/agent.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "agent" in data
        agent_info = data["agent"]
        
        assert "name" in agent_info
        assert "version" in agent_info
        assert "capabilities" in agent_info
        assert "protocols" in agent_info
        assert "skills" in agent_info
        
        # Check A2A protocol info
        assert "a2a" in agent_info["protocols"]
        a2a_protocol = agent_info["protocols"]["a2a"]
        
        assert "version" in a2a_protocol
        assert "endpoints" in a2a_protocol
        assert "supported_formats" in a2a_protocol

    def test_health_check_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "app" in data
        assert "version" in data
        assert "timestamp" in data
        assert "checks" in data

    @pytest.mark.asyncio
    async def test_a2a_websocket_stream(self):
        """Test A2A WebSocket streaming (basic connection test)."""
        # This would require more complex WebSocket testing setup
        # For now, we'll test that the endpoint exists and is properly configured
        
        # Create a session first for the WebSocket test
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning"],
            "protocol_version": "1.0.0"
        }
        
        handshake_response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)
        session_id = handshake_response.json()["session_id"]
        
        # Note: Full WebSocket testing would require additional setup
        # This test ensures the session exists for WebSocket connection
        assert session_id is not None
        assert len(session_id) > 0

    def test_a2a_message_types(self):
        """Test different A2A message types."""
        # Establish session
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning"],
            "protocol_version": "1.0.0"
        }
        
        handshake_response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)
        session_id = handshake_response.json()["session_id"]
        
        # Test different message types
        message_types = [
            "task_request",
            "status_inquiry", 
            "result_request",
            "unknown_type"
        ]
        
        for msg_type in message_types:
            message_data = {
                "session_id": session_id,
                "message_type": msg_type,
                "payload": {"test": "data"}
            }
            
            response = self.client.post("/api/v1/a2a/communicate", json=message_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "payload" in data
            
            if msg_type == "unknown_type":
                assert "unsupported_message_type" in data["payload"]["status"]
            else:
                assert "status" in data["payload"]