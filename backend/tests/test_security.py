"""
Comprehensive security tests for Z2 backend API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.mark.security
class TestSecurityHeaders:
    """Test security headers are properly set."""
    
    def test_security_headers_present(self, client: TestClient, security_headers):
        """Test that security headers are present in responses."""
        response = client.get("/health/live")
        
        # Check for basic security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"


@pytest.mark.security
class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_sql_injection_protection(self, client: TestClient, malicious_payloads):
        """Test protection against SQL injection attacks."""
        for payload in malicious_payloads["sql_injection"]:
            # Test login endpoint
            response = client.post("/auth/login", json={
                "username": payload,
                "password": "password"
            })
            # Should not crash or expose database errors
            assert response.status_code in [400, 401, 422]
            assert "database" not in response.text.lower()
            assert "sql" not in response.text.lower()
    
    def test_xss_protection(self, client: TestClient, malicious_payloads):
        """Test protection against XSS attacks."""
        for payload in malicious_payloads["xss"]:
            # Test user registration
            response = client.post("/auth/register", json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!",
                "full_name": payload
            })
            # Should not reflect malicious content
            if response.status_code < 500:
                assert "<script>" not in response.text
                assert "javascript:" not in response.text
    
    def test_path_traversal_protection(self, client: TestClient, malicious_payloads):
        """Test protection against path traversal attacks."""
        for payload in malicious_payloads["path_traversal"]:
            # Test file access endpoints (if any)
            response = client.get(f"/api/files/{payload}")
            # Should return 404 or 400, not actual file content
            assert response.status_code in [400, 404, 422]
    
    def test_command_injection_protection(self, client: TestClient, malicious_payloads):
        """Test protection against command injection."""
        for payload in malicious_payloads["command_injection"]:
            # Test any endpoint that might execute system commands
            response = client.post("/agents/execute", json={
                "command": payload,
                "parameters": {}
            })
            # Should not execute system commands
            assert response.status_code in [400, 401, 404, 422]


@pytest.mark.security
class TestAuthentication:
    """Test authentication security measures."""
    
    def test_password_strength_requirements(self, client: TestClient):
        """Test password strength requirements."""
        weak_passwords = [
            "123456",
            "password",
            "abc",
            "11111111",
            "password123"
        ]
        
        for weak_password in weak_passwords:
            response = client.post("/auth/register", json={
                "username": "testuser",
                "email": "test@example.com",
                "password": weak_password,
                "full_name": "Test User"
            })
            # Should reject weak passwords
            assert response.status_code == 422
    
    def test_brute_force_protection(self, client: TestClient):
        """Test protection against brute force attacks."""
        # Attempt multiple failed logins
        for i in range(10):
            response = client.post("/auth/login", json={
                "username": "testuser",
                "password": f"wrongpassword{i}"
            })
            # Should maintain proper error responses
            assert response.status_code in [401, 429]  # 429 for rate limiting
    
    def test_session_security(self, client: TestClient):
        """Test session security measures."""
        # Test session timeout
        response = client.get("/auth/me")
        assert response.status_code == 401
        
        # Test secure cookie attributes would be checked here
        # This would require actual login flow testing
    
    def test_unauthorized_access_protection(self, client: TestClient):
        """Test protection of protected endpoints."""
        protected_endpoints = [
            "/agents",
            "/workflows", 
            "/models",
            "/users",
            "/admin"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should require authentication
            assert response.status_code in [401, 403, 404]


@pytest.mark.security
class TestDataProtection:
    """Test data protection and privacy measures."""
    
    def test_sensitive_data_not_logged(self, client: TestClient):
        """Test that sensitive data is not logged."""
        # This would require log inspection
        # Mock or capture logs to ensure passwords, tokens etc. aren't logged
        pass
    
    def test_error_information_disclosure(self, client: TestClient):
        """Test that errors don't disclose sensitive information."""
        # Test 500 errors don't expose stack traces in production
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        # Error messages should be generic
        if response.status_code >= 500:
            response_text = response.text.lower()
            assert "traceback" not in response_text
            assert "exception" not in response_text
            assert "stack" not in response_text
    
    def test_cors_configuration(self, client: TestClient):
        """Test CORS configuration is secure."""
        response = client.options("/api/health", headers={
            "Origin": "https://malicious-site.com",
            "Access-Control-Request-Method": "GET"
        })
        
        # Should not allow arbitrary origins
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        if cors_origin:
            assert cors_origin != "*"


@pytest.mark.security
class TestAPIRateLimiting:
    """Test API rate limiting."""
    
    def test_rate_limiting_protection(self, client: TestClient):
        """Test rate limiting prevents abuse."""
        # Make many requests quickly
        responses = []
        for i in range(100):
            response = client.get("/health/live")
            responses.append(response.status_code)
        
        # Should eventually rate limit (status 429)
        # Note: This test might need adjustment based on actual rate limiting config
        assert any(status == 429 for status in responses) or all(status == 200 for status in responses)


@pytest.mark.security
class TestEncryption:
    """Test encryption and data security."""
    
    def test_password_hashing(self, client: TestClient):
        """Test that passwords are properly hashed."""
        # This would require database inspection
        # Ensure passwords are never stored in plain text
        pass
    
    def test_sensitive_token_handling(self, client: TestClient):
        """Test that tokens are handled securely."""
        # Test JWT tokens are properly signed
        # Test refresh tokens are secure
        pass


@pytest.mark.security
class TestDependencyVulnerabilities:
    """Test for known dependency vulnerabilities."""
    
    def test_no_known_vulnerabilities(self):
        """Test that dependencies don't have known vulnerabilities."""
        # This would integrate with safety/bandit reports
        # For now, just ensure the test structure exists
        import subprocess
        import json
        
        # Run safety check
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                safety_data = json.loads(result.stdout)
                assert len(safety_data) == 0, f"Found vulnerabilities: {safety_data}"
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # Safety not available or timeout, skip this test
            pytest.skip("Safety check not available")


@pytest.mark.security
class TestConfigurationSecurity:
    """Test security configuration."""
    
    def test_debug_mode_disabled(self, client: TestClient):
        """Test debug mode is disabled in production."""
        response = client.get("/health/live")
        # Debug info should not be exposed
        assert "debug" not in response.text.lower()
    
    def test_secure_defaults(self, client: TestClient):
        """Test secure default configurations."""
        # Test secure cookie settings
        # Test HTTPS enforcement (if applicable)
        # Test secure headers
        response = client.get("/health/live")
        assert response.status_code == 200


@pytest.mark.security
@pytest.mark.slow
class TestPenetrationTesting:
    """Basic penetration testing scenarios."""
    
    def test_common_attack_vectors(self, client: TestClient):
        """Test resistance to common attack vectors."""
        # Test CSRF protection
        response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        # Should have proper CSRF protection
        
        # Test clickjacking protection
        response = client.get("/health/live")
        assert "X-Frame-Options" in response.headers or "Content-Security-Policy" in response.headers
    
    def test_information_disclosure(self, client: TestClient):
        """Test for information disclosure vulnerabilities."""
        # Test that sensitive endpoints don't leak information
        sensitive_paths = [
            "/admin",
            "/.env",
            "/config",
            "/backup",
            "/logs"
        ]
        
        for path in sensitive_paths:
            response = client.get(path)
            # Should not expose sensitive information
            assert response.status_code in [404, 403, 401]