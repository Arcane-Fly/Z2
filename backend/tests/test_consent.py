"""
Integration tests for consent and access control system.

These tests validate the security framework for resource and tool access.
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


class TestConsentSystem:
    """Test suite for consent and access control."""

    def test_list_access_policies(self, client: TestClient, mock_db, mock_consent_service):
        """Test listing access control policies."""
        # Mock policy response
        mock_policies = [
            {
                "resource_type": "tool",
                "resource_name": "execute_agent",
                "required_permissions": ["agent:execute"],
                "auto_approve": False,
                "max_usage_per_hour": 10,
                "max_usage_per_day": None,
                "description": "Execute agent tool"
            }
        ]
        mock_consent_service.list_access_policies.return_value = [
            AsyncMock(**policy) for policy in mock_policies
        ]

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

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

    def test_consent_request_auto_approve(self, client: TestClient, mock_db, mock_consent_service):
        """Test consent request that should be auto-approved."""
        # Mock auto-approval policy
        mock_policy = AsyncMock()
        mock_policy.auto_approve = True
        mock_consent_service.get_access_policy.return_value = mock_policy

        # Mock consent request creation
        mock_request = AsyncMock()
        mock_request.id = "test-consent-id"
        mock_consent_service.create_consent_request.return_value = mock_request

        # Mock grant creation
        mock_grant = AsyncMock()
        mock_grant.granted_at = AsyncMock()
        mock_grant.expires_at = AsyncMock()
        mock_consent_service.grant_consent.return_value = mock_grant

        request_data = {
            "user_id": "test-user-auto",
            "resource_type": "resource",
            "resource_name": "agent",
            "description": "Access agent resources",
            "permissions": ["agent:read"],
            "expires_in_hours": 24
        }

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.post("/api/v1/consent/consent/request", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "consent_id" in data
            assert data["status"] == "granted"  # Should be auto-approved
            assert "granted_at" in data
            assert "expires_at" in data
            assert data["permissions"] == ["agent:read"]

    def test_consent_request_manual_approval(self, client: TestClient, mock_db, mock_consent_service):
        """Test consent request that requires manual approval."""
        # Mock policy requiring manual approval
        mock_policy = AsyncMock()
        mock_policy.auto_approve = False
        mock_consent_service.get_access_policy.return_value = mock_policy

        # Mock consent request creation
        mock_request = AsyncMock()
        mock_request.id = "test-consent-manual"
        mock_consent_service.create_consent_request.return_value = mock_request

        # No grant for manual approval
        mock_consent_service.grant_consent.return_value = None

        request_data = {
            "user_id": "test-user-manual",
            "resource_type": "tool",
            "resource_name": "execute_agent",
            "description": "Execute agent tasks",
            "permissions": ["agent:execute"],
            "expires_in_hours": 12
        }

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.post("/api/v1/consent/consent/request", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "consent_id" in data
            assert data["status"] == "pending"  # Should require manual approval
            assert data["permissions"] == ["agent:execute"]

    def test_grant_consent(self, client: TestClient, mock_db, mock_consent_service):
        """Test granting consent for a pending request."""
        consent_id = "test-consent-grant"

        # Mock consent request
        mock_request = AsyncMock()
        mock_request.user_id = "test-user-grant"
        mock_request.permissions = ["workflow:create"]
        mock_consent_service.get_consent_request.return_value = mock_request

        # Mock grant creation
        mock_grant = AsyncMock()
        mock_grant.granted_at = AsyncMock()
        mock_grant.expires_at = AsyncMock()
        mock_consent_service.grant_consent.return_value = mock_grant

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

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

    def test_deny_consent(self, client: TestClient, mock_db, mock_consent_service):
        """Test denying consent for a pending request."""
        consent_id = "test-consent-deny"

        # Mock consent request
        mock_request = AsyncMock()
        mock_request.permissions = ["agent:execute"]
        mock_consent_service.get_consent_request.return_value = mock_request

        # Mock successful denial
        mock_consent_service.deny_consent.return_value = True

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            deny_response = client.post(
                f"/api/v1/consent/consent/{consent_id}/deny",
                params={"user_id": "test-user-deny", "reason": "Security policy violation"}
            )
            assert deny_response.status_code == 200

            data = deny_response.json()
            assert data["consent_id"] == consent_id
            assert data["status"] == "denied"

    def test_get_consent_status(self, client: TestClient, mock_db, mock_consent_service):
        """Test retrieving consent status."""
        consent_id = "test-consent-status"

        # Mock consent request
        mock_request = AsyncMock()
        mock_request.status = "granted"
        mock_request.permissions = ["workflow:read"]
        mock_request.granted_at = None
        mock_request.expires_at = None
        mock_consent_service.get_consent_request.return_value = mock_request

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            status_response = client.get(f"/api/v1/consent/consent/{consent_id}")
            assert status_response.status_code == 200

            data = status_response.json()
            assert data["consent_id"] == consent_id
            assert "status" in data
            assert "permissions" in data

    def test_get_nonexistent_consent(self, client: TestClient, mock_db, mock_consent_service):
        """Test retrieving status for non-existent consent."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        mock_consent_service.get_consent_request.return_value = None

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.get(f"/api/v1/consent/consent/{fake_id}")
            assert response.status_code == 404

    def test_access_check_with_valid_consent(self, client: TestClient, mock_db, mock_consent_service):
        """Test access check with valid consent."""
        # Mock successful access check
        mock_consent_service.check_access.return_value = {
            "allowed": True,
            "reason": "Access granted",
            "grant_id": "test-grant-123"
        }

        access_data = {
            "user_id": "test-user-access",
            "resource_type": "resource",
            "resource_name": "agent",
            "permissions": ["agent:read"]
        }

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            access_response = client.post("/api/v1/consent/access/check", json=access_data)
            assert access_response.status_code == 200

            data = access_response.json()
            assert data["allowed"] is True

    def test_access_check_without_consent(self, client: TestClient, mock_db, mock_consent_service):
        """Test access check without valid consent."""
        # Mock access denied
        mock_consent_service.check_access.return_value = {
            "allowed": False,
            "reason": "No valid consent found"
        }

        access_data = {
            "user_id": "test-user-no-consent",
            "resource_type": "tool",
            "resource_name": "execute_agent",
            "permissions": ["agent:execute"]
        }

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.post("/api/v1/consent/access/check", json=access_data)
            assert response.status_code == 200

            data = response.json()
            assert data["allowed"] is False
            assert "No valid consent found" in data["reason"]

    def test_access_check_missing_permissions(self, client: TestClient, mock_db, mock_consent_service):
        """Test access check with insufficient permissions."""
        # Mock insufficient permissions
        mock_consent_service.check_access.return_value = {
            "allowed": False,
            "reason": "Missing permissions: ['agent:execute']"
        }

        access_data = {
            "user_id": "test-user-insufficient",
            "resource_type": "tool",
            "resource_name": "execute_agent",
            "permissions": ["agent:read"]  # Missing agent:execute
        }

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.post("/api/v1/consent/access/check", json=access_data)
            assert response.status_code == 200

            data = response.json()
            assert data["allowed"] is False
            assert "Missing permissions" in data["reason"]

    def test_access_check_no_policy(self, client: TestClient, mock_db, mock_consent_service):
        """Test access check for resource without policy."""
        # Mock no policy found
        mock_consent_service.check_access.return_value = {
            "allowed": False,
            "reason": "No access policy defined"
        }

        access_data = {
            "user_id": "test-user-no-policy",
            "resource_type": "unknown",
            "resource_name": "mystery_resource",
            "permissions": ["some:permission"]
        }

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.post("/api/v1/consent/access/check", json=access_data)
            assert response.status_code == 200

            data = response.json()
            assert data["allowed"] is False
            assert "No access policy defined" in data["reason"]

    def test_audit_logs(self, client: TestClient, mock_db, mock_consent_service):
        """Test audit logging functionality."""
        # Mock audit logs
        mock_logs = [
            AsyncMock(
                id="log-1",
                timestamp=AsyncMock(),
                user_id="test-user-audit",
                action="request",
                resource_type="resource",
                resource_name="agent",
                details={"test": "data"}
            )
        ]
        mock_consent_service.get_audit_logs.return_value = mock_logs

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

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

    def test_audit_logs_filtered_by_user(self, client: TestClient, mock_db, mock_consent_service):
        """Test filtering audit logs by user."""
        user_id = "test-user-filter"

        # Mock filtered logs
        mock_logs = [
            AsyncMock(
                id="log-filtered",
                timestamp=AsyncMock(),
                user_id=user_id,
                action="request",
                resource_type="resource",
                resource_name="workflow",
                details={}
            )
        ]
        mock_consent_service.get_audit_logs.return_value = mock_logs

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.get(f"/api/v1/consent/audit?user_id={user_id}")
            assert response.status_code == 200

            data = response.json()
            logs = data["logs"]

            # All logs should be for the specified user
            for log in logs:
                assert log["user_id"] == user_id

    def test_user_sessions(self, client: TestClient, mock_db, mock_consent_service):
        """Test retrieving user consent sessions."""
        user_id = "test-user-sessions"

        # Mock active consents
        mock_grant = AsyncMock()
        mock_grant.id = "grant-123"
        mock_grant.request_id = "request-123"
        mock_grant.granted_at = AsyncMock()
        mock_grant.expires_at = AsyncMock()
        mock_grant.granted_permissions = ["agent:read"]
        mock_grant.usage_count = 5
        mock_grant.last_used_at = None
        mock_grant.request = AsyncMock()
        mock_grant.request.resource_type = "resource"
        mock_grant.request.resource_name = "agent"
        mock_grant.request.description = "Session test"

        mock_consent_service.get_user_active_consents.return_value = [mock_grant]

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

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

    def test_setup_default_policies(self, client: TestClient, mock_db, mock_consent_service):
        """Test setting up default access policies."""
        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.post("/api/v1/consent/setup-default-policies")
            assert response.status_code == 200

            data = response.json()
            assert "message" in data
            assert "policies" in data["message"]

    def test_cleanup_expired_consents(self, client: TestClient, mock_db, mock_consent_service):
        """Test cleanup of expired consents."""
        # Mock cleanup result
        mock_consent_service.cleanup_expired_consents.return_value = 5

        with patch('app.api.v1.endpoints.consent.get_db', return_value=mock_db), \
             patch('app.api.v1.endpoints.consent.get_consent_service', return_value=mock_consent_service):

            response = client.post("/api/v1/consent/cleanup-expired")
            assert response.status_code == 200

            data = response.json()
            assert "expired_consents_cleaned" in data
            assert data["expired_consents_cleaned"] == 5
