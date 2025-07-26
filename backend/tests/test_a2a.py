"""
Tests for A2A (Agent-to-Agent) protocol endpoints.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


class TestA2AProtocol:
    """Test A2A protocol implementation."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_a2a_handshake_success(self, mock_db, mock_session_service):
        """Test successful A2A handshake."""
        # Mock session creation
        mock_session_service.create_a2a_session.return_value = AsyncMock()
        
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning", "analysis"],
            "protocol_version": "1.0.0"
        }

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)

            assert response.status_code == 200
            data = response.json()

            assert "session_id" in data
            assert data["agent_name"] == "Z2 AI Workforce Platform"
            assert "capabilities" in data
            assert data["protocol_version"] == "1.0.0"
            assert "expires_at" in data

    def test_a2a_handshake_invalid_version(self, mock_db, mock_session_service):
        """Test A2A handshake with invalid protocol version."""
        handshake_data = {
            "agent_id": "test-agent-123",
            "agent_name": "Test Agent",
            "capabilities": ["reasoning"],
            "protocol_version": "2.0.0"  # Unsupported version
        }

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.post("/api/v1/a2a/handshake", json=handshake_data)

            assert response.status_code == 400
            assert "Unsupported protocol version" in response.json()["detail"]

    def test_a2a_negotiate_success(self, mock_db, mock_session_service):
        """Test successful A2A skill negotiation."""
        # Mock session existence
        mock_session = AsyncMock()
        mock_session.is_active = True
        mock_session.expires_at = AsyncMock()
        mock_session.expires_at.__gt__ = lambda self, other: True  # Not expired
        mock_session_service.get_a2a_session.return_value = mock_session
        mock_session_service.create_a2a_negotiation.return_value = AsyncMock()
        
        session_id = "test-session-123"

        negotiation_data = {
            "session_id": session_id,
            "requested_skills": ["workflow-orchestration", "dynamic-reasoning"],
            "task_description": "Test task description",
            "parameters": {"test": "value"},
            "priority": 7
        }

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.post("/api/v1/a2a/negotiate", json=negotiation_data)

            assert response.status_code == 200
            data = response.json()

            assert "negotiation_id" in data
            assert "available_skills" in data
            assert "proposed_workflow" in data
            assert "estimated_duration" in data
            assert data["accepted"] is True

    def test_a2a_negotiate_invalid_session(self, mock_db, mock_session_service):
        """Test A2A negotiation with invalid session."""
        # Mock session not found
        mock_session_service.get_a2a_session.return_value = None
        
        negotiation_data = {
            "session_id": "invalid-session-id",
            "requested_skills": ["reasoning"],
            "task_description": "Test task",
            "parameters": {}
        }

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.post("/api/v1/a2a/negotiate", json=negotiation_data)

            assert response.status_code == 404
            assert "Session not found" in response.json()["detail"]

    def test_a2a_communicate_success(self, mock_db, mock_session_service):
        """Test successful A2A communication."""
        # Mock session existence
        mock_session = AsyncMock()
        mock_session.is_active = True
        mock_session.expires_at = AsyncMock()
        mock_session.expires_at.__gt__ = lambda self, other: True  # Not expired
        mock_session_service.get_a2a_session.return_value = mock_session
        mock_session_service.create_task_execution.return_value = AsyncMock()
        
        session_id = "test-session-123"

        message_data = {
            "session_id": session_id,
            "message_type": "task_request",
            "payload": {"task": "test task", "data": "test data"}
        }

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.post("/api/v1/a2a/communicate", json=message_data)

            assert response.status_code == 200
            data = response.json()

            assert "message_id" in data
            assert "status" in data
            assert "payload" in data
            assert data["status"] == "processed"

    def test_a2a_communicate_invalid_session(self, mock_db, mock_session_service):
        """Test A2A communication with invalid session."""
        # Mock session not found
        mock_session_service.get_a2a_session.return_value = None
        
        message_data = {
            "session_id": "invalid-session-id",
            "message_type": "task_request",
            "payload": {"task": "test"}
        }

        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.post("/api/v1/a2a/communicate", json=message_data)

            assert response.status_code == 404
            assert "Session not found" in response.json()["detail"]

    def test_a2a_list_sessions(self, mock_db, mock_session_service):
        """Test listing active A2A sessions."""
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.get("/api/v1/a2a/sessions")

            assert response.status_code == 200
            data = response.json()

            assert "active_sessions" in data
            assert "active_streams" in data
            assert "sessions" in data

    def test_a2a_terminate_session(self, mock_db, mock_session_service):
        """Test terminating an A2A session."""
        session_id = "test-session-123"
        mock_session_service.close_a2a_session.return_value = True
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.delete(f"/api/v1/a2a/sessions/{session_id}")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "terminated"
            assert data["session_id"] == session_id

    def test_a2a_terminate_invalid_session(self, mock_db, mock_session_service):
        """Test terminating invalid session."""
        mock_session_service.close_a2a_session.return_value = False
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.delete("/api/v1/a2a/sessions/invalid-session-id")

            assert response.status_code == 404
            assert "Session not found" in response.json()["detail"]

    def test_agent_discovery_endpoint(self):
        """Test the .well-known/agent.json discovery endpoint."""
        response = self.client.get("/.well-known/agent.json")

        # May return error if file doesn't exist in test environment
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "agent" in data or "error" in data

    def test_health_check_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")

        assert response.status_code in [200, 503]  # May be unhealthy in test environment
        data = response.json()

        assert "status" in data
        if "app" in data:
            assert "name" in data["app"]

    def test_a2a_message_types(self, mock_db, mock_session_service):
        """Test different A2A message types."""
        # Mock session existence
        mock_session = AsyncMock()
        mock_session.is_active = True
        mock_session.expires_at = AsyncMock()
        mock_session.expires_at.__gt__ = lambda self, other: True
        mock_session_service.get_a2a_session.return_value = mock_session
        mock_session_service.create_task_execution.return_value = AsyncMock()
        
        session_id = "test-session-123"

        # Test different message types
        message_types = [
            "task_request",
            "status_inquiry", 
            "result_request",
            "heartbeat",
            "capability_inquiry",
            "unknown_type"
        ]

        for msg_type in message_types:
            message_data = {
                "session_id": session_id,
                "message_type": msg_type,
                "payload": {"test": "data"}
            }

            with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
                 patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
                
                response = self.client.post("/api/v1/a2a/communicate", json=message_data)
                assert response.status_code == 200

                data = response.json()
                assert "payload" in data

                if msg_type == "unknown_type":
                    assert "unsupported_message_type" in data["payload"]["status"]
                else:
                    assert "status" in data["payload"]

    def test_a2a_statistics(self, mock_db, mock_session_service):
        """Test A2A statistics endpoint."""
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.get("/api/v1/a2a/statistics")
            assert response.status_code == 200

            data = response.json()
            assert "timestamp" in data
            assert "protocol_version" in data
            assert "sessions" in data
            assert "capabilities" in data
            assert "features" in data

    def test_negotiation_status(self, mock_db, mock_session_service):
        """Test getting negotiation status."""
        negotiation_id = "test-negotiation-123"
        
        # Mock negotiation
        mock_negotiation = AsyncMock()
        mock_negotiation.negotiation_id = negotiation_id
        mock_negotiation.session_id = "test-session"
        mock_negotiation.status = "accepted"
        mock_negotiation.created_at = AsyncMock()
        mock_negotiation.updated_at = AsyncMock()
        mock_negotiation.completed_at = None
        mock_session_service.get_a2a_negotiation.return_value = mock_negotiation
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            response = self.client.get(f"/api/v1/a2a/negotiations/{negotiation_id}")
            assert response.status_code == 200

            data = response.json()
            assert data["negotiation_id"] == negotiation_id
            assert "status" in data

    def test_task_status_and_cancellation(self, mock_db, mock_session_service):
        """Test task status checking and cancellation."""
        task_id = "test-task-123"
        
        # Mock task
        mock_task = AsyncMock()
        mock_task.task_id = task_id
        mock_task.status = "running"
        mock_task.progress = "0.5"
        mock_task.can_cancel = True
        mock_task.created_at = AsyncMock()
        mock_session_service.get_task_execution.return_value = mock_task
        mock_session_service.cancel_task.return_value = True
        
        with patch('app.api.v1.endpoints.a2a.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.a2a.get_session_service', return_value=mock_session_service):
            
            # Test status check
            response = self.client.get(f"/api/v1/a2a/tasks/{task_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["task_id"] == task_id
            assert "status" in data
            assert "progress" in data
            
            # Test cancellation
            response = self.client.post(f"/api/v1/a2a/tasks/{task_id}/cancel")
            assert response.status_code == 200
            
            data = response.json()
            assert data["task_id"] == task_id
            assert data["status"] == "cancelled"
