"""
Test monitoring and observability features for Z2 platform.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_endpoint():
    """Test the general health check endpoint."""
    response = client.get("/health")
    assert response.status_code in [200, 503]  # Can be degraded but should respond
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "app" in data
    assert data["app"]["name"] == "Z2 AI Workforce Platform"


def test_liveness_probe():
    """Test Kubernetes liveness probe endpoint."""
    response = client.get("/health/live")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data
    assert "uptime_seconds" in data


def test_readiness_probe():
    """Test Kubernetes readiness probe endpoint."""
    response = client.get("/health/ready")
    # Can be 200 or 503 depending on external dependencies
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data


def test_prometheus_metrics():
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    
    # Check for expected metrics
    content = response.content.decode()
    assert "z2_http_requests_total" in content
    assert "z2_http_request_duration_seconds" in content


def test_json_metrics():
    """Test JSON metrics endpoint."""
    response = client.get("/metrics/json")
    assert response.status_code == 200
    
    data = response.json()
    assert "timestamp" in data
    assert "app" in data
    assert "metrics" in data
    assert "request_counts" in data["metrics"]


def test_metrics_collection():
    """Test that metrics are properly collected."""
    from app.utils.monitoring import metrics_collector
    
    # Record some test metrics
    metrics_collector.record_request("/test", "GET", 200, 0.5)
    metrics_collector.record_model_request("openai", "gpt-4o-mini", "success", 1.2)
    
    # Check metrics are recorded
    metrics = metrics_collector.get_metrics()
    assert "GET_/test" in metrics["request_counts"]
    assert metrics["request_counts"]["GET_/test"] == 1
    
    # Check Prometheus format
    prometheus_metrics = metrics_collector.get_prometheus_metrics()
    assert b"z2_http_requests_total" in prometheus_metrics
    assert b"z2_model_requests_total" in prometheus_metrics


def test_agent_discovery_endpoint():
    """Test A2A protocol agent discovery endpoint."""
    response = client.get("/.well-known/agent.json")
    assert response.status_code == 200
    
    data = response.json()
    # Should contain agent configuration or error info
    assert isinstance(data, dict)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "Z2 AI Workforce Platform" in data["message"]