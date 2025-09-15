"""
Tests for utility helper functions.
"""

import pytest
from datetime import datetime
from uuid import uuid4
import time

from app.utils.helpers import (
    truncate_string,
    format_file_size,
    validate_email,
    format_datetime,
    calculate_time_diff,
    get_config_value,
    parse_bool_config,
    sanitize_filename,
    generate_uuid_str,
    mask_sensitive_data,
    chunk_list,
    deep_merge_dicts,
    retry_with_backoff
)


class TestStringUtilities:
    """Test string utility functions."""

    def test_truncate_string_no_truncation(self):
        """Test truncate_string when text is shorter than max_length."""
        result = truncate_string("hello", 10)
        assert result == "hello"

    def test_truncate_string_with_truncation(self):
        """Test truncate_string when text needs truncation."""
        result = truncate_string("hello world", 5)
        assert result == "hello..."

    def test_truncate_string_custom_suffix(self):
        """Test truncate_string with custom suffix."""
        result = truncate_string("hello world", 5, " [more]")
        assert result == "hello [more]"

    def test_truncate_string_exact_length(self):
        """Test truncate_string when text equals max_length."""
        result = truncate_string("hello", 5)
        assert result == "hello"

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        result = sanitize_filename("file<>name*.txt")
        assert result == "file__name_.txt"

    def test_sanitize_filename_empty(self):
        """Test filename sanitization with empty string."""
        result = sanitize_filename("")
        assert result == "unnamed_file"

    def test_generate_uuid_str(self):
        """Test UUID string generation."""
        result = generate_uuid_str()
        assert len(result) == 36  # Standard UUID length
        assert result.count('-') == 4  # Standard UUID format

    def test_mask_sensitive_data(self):
        """Test sensitive data masking."""
        result = mask_sensitive_data("1234567890", "*", 2)
        assert result == "12******90"

    def test_mask_sensitive_data_short(self):
        """Test masking short data."""
        result = mask_sensitive_data("123", "*", 2)
        assert result == "***"


class TestFileUtilities:
    """Test file and size utility functions."""

    def test_format_file_size_zero(self):
        """Test format_file_size with zero bytes."""
        result = format_file_size(0)
        assert result == "0 B"

    def test_format_file_size_bytes(self):
        """Test format_file_size with bytes."""
        result = format_file_size(512)
        assert result == "512.0 B"

    def test_format_file_size_kilobytes(self):
        """Test format_file_size with kilobytes."""
        result = format_file_size(1536)  # 1.5 KB
        assert result == "1.5 KB"

    def test_format_file_size_megabytes(self):
        """Test format_file_size with megabytes."""
        result = format_file_size(1572864)  # 1.5 MB
        assert result == "1.5 MB"


class TestValidationUtilities:
    """Test validation utility functions."""

    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        assert validate_email("test@example.com") == True
        assert validate_email("user.name+tag@domain.co.uk") == True

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        assert validate_email("invalid-email") == False
        assert validate_email("@domain.com") == False
        assert validate_email("user@") == False
        assert validate_email("") == False


class TestDateTimeUtilities:
    """Test datetime utility functions."""

    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = format_datetime(dt)
        assert result == "2023-01-01 12:00:00"

    def test_format_datetime_custom_format(self):
        """Test datetime formatting with custom format."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = format_datetime(dt, "%Y-%m-%d")
        assert result == "2023-01-01"

    def test_calculate_time_diff(self):
        """Test time difference calculation."""
        start = datetime(2023, 1, 1, 12, 0, 0)
        end = datetime(2023, 1, 1, 12, 0, 5)
        result = calculate_time_diff(start, end)
        assert result == 5.0


class TestConfigUtilities:
    """Test configuration utility functions."""

    def test_get_config_value_with_default(self):
        """Test getting config value with default."""
        result = get_config_value("NON_EXISTENT_KEY", "default_value")
        assert result == "default_value"

    def test_parse_bool_config_true_values(self):
        """Test parsing boolean config for true values."""
        assert parse_bool_config("true") == True
        assert parse_bool_config("1") == True
        assert parse_bool_config("yes") == True
        assert parse_bool_config("on") == True
        assert parse_bool_config("enabled") == True

    def test_parse_bool_config_false_values(self):
        """Test parsing boolean config for false values."""
        assert parse_bool_config("false") == False
        assert parse_bool_config("0") == False
        assert parse_bool_config("no") == False
        assert parse_bool_config("") == False


class TestDataUtilities:
    """Test data manipulation utilities."""

    def test_chunk_list(self):
        """Test list chunking."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = chunk_list(data, 3)
        assert len(result) == 4  # 3 full chunks + 1 partial
        assert result[0] == [1, 2, 3]
        assert result[3] == [10]

    def test_deep_merge_dicts(self):
        """Test deep dictionary merging."""
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}
        result = deep_merge_dicts(dict1, dict2)
        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 3
        assert result["e"] == 4


class TestRetryUtilities:
    """Test retry utility functions."""

    def test_retry_with_backoff_success(self):
        """Test retry function that succeeds immediately."""
        def always_succeed():
            return "success"
        
        result = retry_with_backoff(always_succeed)
        assert result == "success"

    def test_retry_with_backoff_eventual_success(self):
        """Test retry function that succeeds after failures."""
        attempts = [0]  # Use list to modify from inner function
        
        def succeed_on_third_try():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("Not yet")
            return "success"
        
        result = retry_with_backoff(succeed_on_third_try, max_retries=3, backoff_factor=0.01)
        assert result == "success"
        assert attempts[0] == 3

    def test_retry_with_backoff_max_retries_exceeded(self):
        """Test retry function that always fails."""
        def always_fail():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            retry_with_backoff(always_fail, max_retries=2, backoff_factor=0.01)