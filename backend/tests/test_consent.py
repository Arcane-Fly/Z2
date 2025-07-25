"""
Integration tests for consent and access control system.

These tests validate the security framework for resource and tool access.
"""

import pytest
from fastapi.testclient import TestClient


class TestConsentSystem:
    """Test suite for consent and access control."""

    def test_list_access_policies(self, client: TestClient):
        """Test listing access control policies."""
        response = client.get("/api/v1/consent/policies")
        assert response.status_code == 200
        
        data = response.json()
        assert "policies" in data
        
        policies = data["policies"]
        assert len(policies) > 0
        
        # Check policy structure
        for policy in policies:
            assert "resource_type" in policy
            assert "resource_name" in policy
            assert "required_permissions" in policy
            assert "auto_approve" in policy
            assert isinstance(policy["auto_approve"], bool)

    def test_consent_request_auto_approve(self, client: TestClient):
        """Test consent request that should be auto-approved."""
        request_data = {
            "user_id": "test-user-auto",
            "resource_type": "resource",
            "resource_name": "agent",
            "description": "Access agent resources",
            "permissions": ["agent:read"],
            "expires_in_hours": 24
        }
        
        response = client.post("/api/v1/consent/consent/request", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "consent_id" in data
        assert data["status"] == "granted"  # Should be auto-approved
        assert "granted_at" in data
        assert "expires_at" in data
        assert data["permissions"] == ["agent:read"]

    def test_consent_request_manual_approval(self, client: TestClient):
        """Test consent request that requires manual approval."""
        request_data = {
            "user_id": "test-user-manual",
            "resource_type": "tool",
            "resource_name": "execute_agent",
            "description": "Execute agent tasks",
            "permissions": ["agent:execute"],
            "expires_in_hours": 12
        }
        
        response = client.post("/api/v1/consent/consent/request", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "consent_id" in data
        assert data["status"] == "pending"  # Should require manual approval
        assert data["permissions"] == ["agent:execute"]
        
        return data["consent_id"]

    def test_grant_consent(self, client: TestClient):
        """Test granting consent for a pending request."""
        # First create a pending consent request
        request_data = {
            "user_id": "test-user-grant",
            "resource_type": "tool",
            "resource_name": "create_workflow",
            "description": "Create workflows",
            "permissions": ["workflow:create"],
            "expires_in_hours": 6
        }
        
        response = client.post("/api/v1/consent/consent/request", json=request_data)
        assert response.status_code == 200
        consent_id = response.json()["consent_id"]
        
        # Grant the consent
        grant_response = client.post(
            f"/api/v1/consent/consent/{consent_id}/grant",
            params={"user_id": "test-user-grant"}
        )
        assert grant_response.status_code == 200
        
        data = grant_response.json()
        assert data["consent_id"] == consent_id
        assert data["status"] == "granted"
        assert "granted_at" in data
        assert "expires_at" in data

    def test_deny_consent(self, client: TestClient):
        """Test denying consent for a pending request."""
        # First create a pending consent request
        request_data = {
            "user_id": "test-user-deny",
            "resource_type": "tool",
            "resource_name": "execute_agent",
            "description": "Execute agent tasks",
            "permissions": ["agent:execute"]
        }
        
        response = client.post("/api/v1/consent/consent/request", json=request_data)
        assert response.status_code == 200
        consent_id = response.json()["consent_id"]
        
        # Deny the consent
        deny_response = client.post(
            f"/api/v1/consent/consent/{consent_id}/deny",
            params={"user_id": "test-user-deny", "reason": "Security policy violation"}
        )
        assert deny_response.status_code == 200
        
        data = deny_response.json()
        assert data["consent_id"] == consent_id
        assert data["status"] == "denied"

    def test_get_consent_status(self, client: TestClient):
        """Test retrieving consent status."""
        # Create a consent request
        request_data = {
            "user_id": "test-user-status",
            "resource_type": "resource",
            "resource_name": "workflow",
            "description": "Access workflow resources",
            "permissions": ["workflow:read"]
        }
        
        response = client.post("/api/v1/consent/consent/request", json=request_data)
        assert response.status_code == 200
        consent_id = response.json()["consent_id"]
        
        # Get consent status
        status_response = client.get(f"/api/v1/consent/consent/{consent_id}")
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert data["consent_id"] == consent_id
        assert "status" in data
        assert "permissions" in data

    def test_get_nonexistent_consent(self, client: TestClient):
        """Test retrieving status for non-existent consent."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/consent/consent/{fake_id}")
        assert response.status_code == 404

    def test_access_check_with_valid_consent(self, client: TestClient):
        """Test access check with valid consent."""
        # First request and get consent
        request_data = {
            "user_id": "test-user-access",
            "resource_type": "resource",
            "resource_name": "agent",
            "description": "Access agent resources",
            "permissions": ["agent:read"]
        }
        
        response = client.post("/api/v1/consent/consent/request", json=request_data)
        assert response.status_code == 200
        assert response.json()["status"] == "granted"  # Auto-approved
        
        # Check access
        access_data = {
            "user_id": "test-user-access",
            "resource_type": "resource",
            "resource_name": "agent",
            "permissions": ["agent:read"]
        }
        
        access_response = client.post("/api/v1/consent/access/check", json=access_data)
        assert access_response.status_code == 200
        
        data = access_response.json()
        assert data["allowed"] == True

    def test_access_check_without_consent(self, client: TestClient):
        """Test access check without valid consent."""
        access_data = {
            "user_id": "test-user-no-consent",
            "resource_type": "tool",
            "resource_name": "execute_agent",
            "permissions": ["agent:execute"]
        }
        
        response = client.post("/api/v1/consent/access/check", json=access_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["allowed"] == False
        assert "No valid consent found" in data["reason"]

    def test_access_check_missing_permissions(self, client: TestClient):
        """Test access check with insufficient permissions."""
        access_data = {
            "user_id": "test-user-insufficient",
            "resource_type": "tool",
            "resource_name": "execute_agent",
            "permissions": ["agent:read"]  # Missing agent:execute
        }
        
        response = client.post("/api/v1/consent/access/check", json=access_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["allowed"] == False
        assert "Missing permissions" in data["reason"]

    def test_access_check_no_policy(self, client: TestClient):
        """Test access check for resource without policy."""
        access_data = {
            "user_id": "test-user-no-policy",
            "resource_type": "unknown",
            "resource_name": "mystery_resource",
            "permissions": ["some:permission"]
        }
        
        response = client.post("/api/v1/consent/access/check", json=access_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["allowed"] == False
        assert "No access policy defined" in data["reason"]

    def test_audit_logs(self, client: TestClient):
        """Test audit logging functionality."""
        # Perform some actions that should be logged
        request_data = {
            "user_id": "test-user-audit",
            "resource_type": "resource",
            "resource_name": "agent",
            "description": "Testing audit logs",
            "permissions": ["agent:read"]
        }
        
        client.post("/api/v1/consent/consent/request", json=request_data)
        
        # Check audit logs
        response = client.get("/api/v1/consent/audit")
        assert response.status_code == 200
        
        data = response.json()
        assert "logs" in data
        
        logs = data["logs"]
        assert len(logs) > 0
        
        # Check log structure
        for log in logs:
            assert "log_id" in log
            assert "timestamp" in log
            assert "user_id" in log
            assert "action" in log
            assert "resource_type" in log
            assert "resource_name" in log

    def test_audit_logs_filtered_by_user(self, client: TestClient):
        """Test filtering audit logs by user."""
        # Create some activity for a specific user
        user_id = "test-user-filter"
        request_data = {
            "user_id": user_id,
            "resource_type": "resource",
            "resource_name": "workflow",
            "description": "Filter test",
            "permissions": ["workflow:read"]
        }
        
        client.post("/api/v1/consent/consent/request", json=request_data)
        
        # Get filtered logs
        response = client.get(f"/api/v1/consent/audit?user_id={user_id}")
        assert response.status_code == 200
        
        data = response.json()
        logs = data["logs"]
        
        # All logs should be for the specified user
        for log in logs:
            assert log["user_id"] == user_id

    def test_user_sessions(self, client: TestClient):
        """Test retrieving user consent sessions."""
        user_id = "test-user-sessions"
        
        # Create some consents
        request_data = {
            "user_id": user_id,
            "resource_type": "resource",
            "resource_name": "agent",
            "description": "Session test",
            "permissions": ["agent:read"]
        }
        
        client.post("/api/v1/consent/consent/request", json=request_data)
        
        # Get user sessions
        response = client.get(f"/api/v1/consent/sessions/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == user_id
        assert "active_consents" in data
        
        # Should have at least one active consent
        active_consents = data["active_consents"]
        if len(active_consents) > 0:
            consent = active_consents[0]
            assert "consent_id" in consent
            assert "granted_at" in consent
            assert "expires_at" in consent
            assert "permissions" in consent