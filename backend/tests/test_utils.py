"""
Tests for utility functions.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from app.utils.security import (
    verify_password,
    hash_password, 
    create_access_token,
    verify_access_token
)
from app.utils.monitoring import (
    PerformanceMetrics,
    format_performance_summary,
    get_system_metrics
)


class TestSecurityUtils:
    """Test security utility functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        
        # Test hashing
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 0
        
        # Test verification
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
        
    def test_password_hashing_different_results(self):
        """Test that hashing the same password produces different results."""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Different hashes due to salt
        assert hash1 != hash2
        
        # But both verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
        
    def test_access_token_creation_and_verification(self):
        """Test JWT access token creation and verification."""
        user_id = "test-user-123"
        
        # Create token
        token = create_access_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        decoded_user_id = verify_access_token(token)
        assert decoded_user_id == user_id
        
    def test_invalid_access_token(self):
        """Test verification of invalid access token."""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(Exception):
            verify_access_token(invalid_token)
            
    def test_expired_access_token(self):
        """Test verification of expired access token."""
        user_id = "test-user-123"
        
        # Create token with negative expiry (already expired)
        with patch('app.utils.security.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow() - timedelta(hours=1)
            token = create_access_token(user_id)
        
        # Should raise exception when verifying expired token
        with pytest.raises(Exception):
            verify_access_token(token)


class TestMonitoringUtils:
    """Test monitoring utility functions."""
    
    def test_performance_metrics_initialization(self):
        """Test PerformanceMetrics initialization."""
        metrics = PerformanceMetrics()
        
        assert metrics.request_count == 0
        assert metrics.total_response_time == 0.0
        assert metrics.error_count == 0
        assert len(metrics.response_times) == 0
        assert len(metrics.memory_usage) == 0
        
    def test_performance_metrics_add_request(self):
        """Test adding request to performance metrics."""
        metrics = PerformanceMetrics()
        
        # Add successful request
        metrics.add_request(0.5, False)
        assert metrics.request_count == 1
        assert metrics.total_response_time == 0.5
        assert metrics.error_count == 0
        assert metrics.response_times == [0.5]
        
        # Add error request
        metrics.add_request(1.0, True)
        assert metrics.request_count == 2
        assert metrics.total_response_time == 1.5
        assert metrics.error_count == 1
        assert metrics.response_times == [0.5, 1.0]
        
    def test_performance_metrics_average_response_time(self):
        """Test average response time calculation."""
        metrics = PerformanceMetrics()
        
        # No requests
        assert metrics.average_response_time == 0.0
        
        # With requests
        metrics.add_request(0.5, False)
        metrics.add_request(1.5, False)
        assert metrics.average_response_time == 1.0
        
    def test_performance_metrics_error_rate(self):
        """Test error rate calculation."""
        metrics = PerformanceMetrics()
        
        # No requests
        assert metrics.error_rate == 0.0
        
        # With requests
        metrics.add_request(0.5, False)
        metrics.add_request(1.0, True)
        metrics.add_request(0.8, False)
        
        # 1 error out of 3 requests = 33.33%
        assert abs(metrics.error_rate - 33.33) < 0.01
        
    def test_format_performance_summary(self):
        """Test performance summary formatting."""
        metrics = PerformanceMetrics()
        metrics.add_request(0.5, False)
        metrics.add_request(1.0, True)
        metrics.add_request(0.8, False)
        
        summary = format_performance_summary(metrics)
        
        assert "Requests: 3" in summary
        assert "Average Response Time:" in summary
        assert "Error Rate:" in summary
        
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_system_metrics(self, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection."""
        # Mock system metrics
        mock_cpu.return_value = 25.5
        mock_memory.return_value = MagicMock(percent=60.2, available=1073741824)
        mock_disk.return_value = MagicMock(percent=45.8, free=2147483648)
        
        metrics = get_system_metrics()
        
        assert metrics['cpu_percent'] == 25.5
        assert metrics['memory_percent'] == 60.2
        assert metrics['disk_percent'] == 45.8
        assert 'memory_available_gb' in metrics
        assert 'disk_free_gb' in metrics


class TestStringUtils:
    """Test string utility functions."""
    
    def test_truncate_string(self):
        """Test string truncation utility."""
        from app.utils.helpers import truncate_string
        
        # Short string
        short = "Hello"
        assert truncate_string(short, 10) == "Hello"
        
        # Long string
        long_str = "This is a very long string that should be truncated"
        truncated = truncate_string(long_str, 20)
        assert len(truncated) <= 23  # 20 + "..."
        assert truncated.endswith("...")
        
    def test_format_file_size(self):
        """Test file size formatting utility."""
        from app.utils.helpers import format_file_size
        
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(1073741824) == "1.0 GB"
        
    def test_validate_email(self):
        """Test email validation utility."""
        from app.utils.helpers import validate_email
        
        # Valid emails
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True
        
        # Invalid emails
        assert validate_email("invalid-email") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False
        assert validate_email("") is False


class TestDateUtils:
    """Test date utility functions."""
    
    def test_format_datetime(self):
        """Test datetime formatting utility."""
        from app.utils.helpers import format_datetime
        
        dt = datetime(2024, 1, 15, 14, 30, 45)
        formatted = format_datetime(dt)
        
        assert "2024-01-15" in formatted
        assert "14:30:45" in formatted
        
    def test_calculate_time_diff(self):
        """Test time difference calculation."""
        from app.utils.helpers import calculate_time_diff
        
        start = datetime(2024, 1, 15, 14, 30, 0)
        end = datetime(2024, 1, 15, 14, 32, 30)
        
        diff = calculate_time_diff(start, end)
        assert diff == 150  # 2.5 minutes = 150 seconds


class TestConfigUtils:
    """Test configuration utility functions."""
    
    def test_get_config_value(self):
        """Test configuration value retrieval."""
        from app.utils.helpers import get_config_value
        
        # Test with default
        value = get_config_value("NON_EXISTENT_CONFIG", "default_value")
        assert value == "default_value"
        
        # Test with environment variable
        with patch.dict('os.environ', {'TEST_CONFIG': 'test_value'}):
            value = get_config_value("TEST_CONFIG", "default")
            assert value == "test_value"
            
    def test_parse_bool_config(self):
        """Test boolean configuration parsing."""
        from app.utils.helpers import parse_bool_config
        
        assert parse_bool_config("true") is True
        assert parse_bool_config("TRUE") is True
        assert parse_bool_config("1") is True
        assert parse_bool_config("yes") is True
        
        assert parse_bool_config("false") is False
        assert parse_bool_config("FALSE") is False
        assert parse_bool_config("0") is False
        assert parse_bool_config("no") is False
        assert parse_bool_config("") is False