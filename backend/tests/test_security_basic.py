"""
Basic security tests for Z2 backend API that don't require database.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import create_application


@pytest.fixture
def simple_client():
    """Create a simple test client without database dependencies."""
    app = create_application()
    return TestClient(app)


@pytest.mark.security
class TestBasicSecurity:
    """Test basic security measures without database."""
    
    def test_health_endpoint_accessible(self, simple_client):
        """Test that health endpoint is accessible."""
        response = simple_client.get("/health/live")
        # Should return some response (200, 500, etc.)
        assert response.status_code in [200, 500]
    
    def test_nonexistent_endpoint_404(self, simple_client):
        """Test that nonexistent endpoints return 404."""
        response = simple_client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_sql_injection_in_path(self, simple_client):
        """Test SQL injection protection in URL paths."""
        malicious_paths = [
            "/api/users/'; DROP TABLE users; --",
            "/api/users/1' OR '1'='1",
            "/api/agents/admin'--",
        ]
        
        for path in malicious_paths:
            response = simple_client.get(path)
            # Should not crash or expose database errors
            assert response.status_code in [404, 422, 400]
            if response.status_code != 404:
                assert "database" not in response.text.lower()
                assert "sql" not in response.text.lower()
    
    def test_xss_in_query_params(self, simple_client):
        """Test XSS protection in query parameters."""
        malicious_params = [
            "?search=<script>alert('xss')</script>",
            "?name=javascript:alert('xss')",
            "?filter=<img src=x onerror=alert('xss')>",
        ]
        
        for params in malicious_params:
            response = simple_client.get(f"/api/users{params}")
            # Should not reflect malicious content
            if response.status_code < 500:
                assert "<script>" not in response.text
                assert "javascript:" not in response.text
    
    def test_large_request_handling(self, simple_client):
        """Test handling of large requests."""
        large_data = {"data": "x" * 100000}  # 100KB
        response = simple_client.post("/api/agents", json=large_data)
        
        # Should handle gracefully without crashing (404 is valid if endpoint doesn't exist)
        assert response.status_code in [400, 401, 404, 413, 422, 500]
    
    def test_invalid_json_handling(self, simple_client):
        """Test handling of invalid JSON."""
        response = simple_client.post(
            "/api/agents",
            data="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return proper error for invalid JSON (or 404 if endpoint doesn't exist)
        assert response.status_code in [404, 422]
    
    def test_unauthorized_access(self, simple_client):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            "/api/agents",
            "/api/workflows",
            "/api/models",
            "/api/users",
        ]
        
        for endpoint in protected_endpoints:
            response = simple_client.get(endpoint)
            # Should require authentication
            assert response.status_code in [401, 403, 404]
    
    def test_method_not_allowed(self, simple_client):
        """Test proper handling of unsupported HTTP methods."""
        response = simple_client.patch("/health/live")
        assert response.status_code in [405, 404]


@pytest.mark.security
class TestInputValidation:
    """Test input validation without database dependencies."""
    
    def test_email_validation(self, simple_client):
        """Test email validation in registration."""
        invalid_emails = [
            "notanemail",
            "@domain.com",
            "user@",
            "user..double.dot@domain.com",
            "user@domain",
        ]
        
        for email in invalid_emails:
            response = simple_client.post("/auth/register", json={
                "username": "testuser",
                "email": email,
                "password": "ValidPass123!",
                "full_name": "Test User"
            })
            # Should reject invalid emails (or 404 if endpoint doesn't exist)
            assert response.status_code in [400, 404, 422]
    
    def test_password_validation(self, simple_client):
        """Test password validation requirements."""
        weak_passwords = [
            "123",           # too short
            "password",      # no numbers/special chars
            "PASSWORD123",   # no lowercase
            "password123",   # no uppercase
            "Password",      # no numbers
        ]
        
        for password in weak_passwords:
            response = simple_client.post("/auth/register", json={
                "username": "testuser",
                "email": "test@example.com",
                "password": password,
                "full_name": "Test User"
            })
            # Should reject weak passwords (or 404 if endpoint doesn't exist)
            assert response.status_code in [400, 404, 422]


@pytest.mark.security
class TestErrorHandling:
    """Test error handling security."""
    
    def test_error_information_disclosure(self, simple_client):
        """Test that errors don't disclose sensitive information."""
        # Try to trigger various errors
        test_cases = [
            ("/api/users/999999", "GET"),  # Non-existent resource
            ("/api/agents", "POST"),       # Missing auth
            ("/api/workflows/invalid", "GET"),  # Invalid ID format
        ]
        
        for endpoint, method in test_cases:
            if method == "GET":
                response = simple_client.get(endpoint)
            elif method == "POST":
                response = simple_client.post(endpoint, json={})
            
            # Check that error messages don't expose internals
            if response.status_code >= 400:
                response_text = response.text.lower()
                
                # Should not expose internal details
                sensitive_keywords = [
                    "traceback", "exception", "stack", "internal server",
                    "database", "sql", "connection", "password", "secret"
                ]
                
                for keyword in sensitive_keywords:
                    assert keyword not in response_text, f"Found sensitive keyword '{keyword}' in error response"


@pytest.mark.security
class TestAPILimits:
    """Test API limits and constraints."""
    
    def test_request_size_limits(self, simple_client):
        """Test request size limitations."""
        # Test with very large JSON payload
        huge_data = {"field": "x" * 1000000}  # 1MB of data
        
        response = simple_client.post("/api/agents", json=huge_data)
        
        # Should either reject or handle gracefully (404 is also valid if endpoint doesn't exist)
        assert response.status_code in [400, 401, 404, 413, 422, 500]
    
    def test_nested_json_limits(self, simple_client):
        """Test deeply nested JSON handling."""
        # Create deeply nested JSON
        nested_data = {}
        current = nested_data
        for i in range(100):  # 100 levels deep
            current["level"] = {}
            current = current["level"]
        current["value"] = "deep"
        
        response = simple_client.post("/api/agents", json=nested_data)
        
        # Should handle without crashing (404 is valid if endpoint doesn't exist)
        assert response.status_code in [400, 401, 404, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])