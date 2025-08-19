"""
Tests for security utility functions.
"""

import pytest
from datetime import datetime, timedelta
import jwt

from app.utils.security import (
    generate_secure_token,
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    hash_password_legacy,
    verify_password_legacy,
    get_utc_now,
    is_expired,
    sanitize_filename,
    SECRET_KEY,
    ALGORITHM
)


class TestTokenGeneration:
    """Test token generation utilities."""

    def test_generate_secure_token_default_length(self):
        """Test secure token generation with default length."""
        token = generate_secure_token()
        assert len(token) == 64  # 32 bytes = 64 hex chars

    def test_generate_secure_token_custom_length(self):
        """Test secure token generation with custom length."""
        token = generate_secure_token(16)
        assert len(token) == 32  # 16 bytes = 32 hex chars

    def test_generate_secure_token_uniqueness(self):
        """Test that generated tokens are unique."""
        token1 = generate_secure_token()
        token2 = generate_secure_token()
        assert token1 != token2


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 20  # Bcrypt hashes are long
        assert hashed != password  # Should be different from original

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) == False

    def test_hash_password_different_results(self):
        """Test that same password produces different hashes (salt)."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different salts should produce different hashes
        assert verify_password(password, hash1) == True
        assert verify_password(password, hash2) == True


class TestJWTTokens:
    """Test JWT token utilities."""

    def test_create_access_token(self):
        """Test JWT access token creation."""
        user_id = "test_user_123"
        token = create_access_token(user_id)
        
        assert isinstance(token, str)
        assert len(token) > 10  # JWT tokens are reasonably long

    def test_create_access_token_custom_expiry(self):
        """Test JWT token with custom expiration."""
        user_id = "test_user_123"
        expires_delta = timedelta(hours=1)
        token = create_access_token(user_id, expires_delta)
        
        assert isinstance(token, str)
        # Verify the token contains the custom expiry
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_verify_access_token_valid(self):
        """Test verification of valid JWT token."""
        user_id = "test_user_123"
        token = create_access_token(user_id)
        
        decoded_user_id = verify_access_token(token)
        assert decoded_user_id == user_id

    def test_verify_access_token_invalid(self):
        """Test verification of invalid JWT token."""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(Exception) as exc_info:
            verify_access_token(invalid_token)
        assert "Invalid token" in str(exc_info.value)

    def test_verify_access_token_expired(self):
        """Test verification of expired JWT token."""
        user_id = "test_user_123"
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(user_id, expires_delta)
        
        with pytest.raises(Exception) as exc_info:
            verify_access_token(token)
        assert "Invalid token" in str(exc_info.value)


class TestLegacyPasswordHashing:
    """Test legacy password hashing utilities."""

    def test_hash_password_legacy_with_salt(self):
        """Test legacy password hashing with provided salt."""
        password = "test_password_123"
        salt = "test_salt_123"
        hashed, returned_salt = hash_password_legacy(password, salt)
        
        assert isinstance(hashed, str)
        assert returned_salt == salt
        assert len(hashed) > 20  # Hash should be reasonably long

    def test_hash_password_legacy_without_salt(self):
        """Test legacy password hashing with generated salt."""
        password = "test_password_123"
        hashed, salt = hash_password_legacy(password)
        
        assert isinstance(hashed, str)
        assert isinstance(salt, str)
        assert len(salt) == 64  # 32 bytes = 64 hex chars

    def test_verify_password_legacy_correct(self):
        """Test legacy password verification with correct password."""
        password = "test_password_123"
        hashed, salt = hash_password_legacy(password)
        
        assert verify_password_legacy(password, hashed, salt) == True

    def test_verify_password_legacy_incorrect(self):
        """Test legacy password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed, salt = hash_password_legacy(password)
        
        assert verify_password_legacy(wrong_password, hashed, salt) == False


class TestDateTimeUtilities:
    """Test datetime utility functions."""

    def test_get_utc_now(self):
        """Test UTC timestamp generation."""
        now = get_utc_now()
        assert isinstance(now, datetime)
        assert now.tzinfo is not None  # Should have timezone info

    def test_is_expired_true(self):
        """Test expiration check with expired timestamp."""
        from app.utils.security import get_utc_now
        expired_time = get_utc_now() - timedelta(hours=1)  # 1 hour ago
        assert is_expired(expired_time) == True

    def test_is_expired_false(self):
        """Test expiration check with future timestamp."""
        from app.utils.security import get_utc_now
        future_time = get_utc_now() + timedelta(hours=1)  # 1 hour from now
        assert is_expired(future_time) == False


class TestFilenameUtilities:
    """Test filename sanitization utilities."""

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        filename = "test<>file*.txt"
        sanitized = sanitize_filename(filename)
        assert sanitized == "test__file_.txt"

    def test_sanitize_filename_dangerous_chars(self):
        """Test sanitization of dangerous characters."""
        filename = 'file:name/with\\dangerous|chars?.txt'
        sanitized = sanitize_filename(filename)
        # All dangerous chars should be replaced with underscores
        assert "<" not in sanitized
        assert ">" not in sanitized
        assert ":" not in sanitized
        assert "/" not in sanitized
        assert "\\" not in sanitized
        assert "|" not in sanitized
        assert "?" not in sanitized
        assert "*" not in sanitized

    def test_sanitize_filename_control_chars(self):
        """Test sanitization of control characters."""
        filename = "file\x00\x01name.txt"  # Contains control chars
        sanitized = sanitize_filename(filename)
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized

    def test_sanitize_filename_long_name(self):
        """Test sanitization of very long filenames."""
        long_filename = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_filename)
        assert len(sanitized) <= 255

    def test_sanitize_filename_empty(self):
        """Test sanitization of empty filename."""
        filename = ""
        sanitized = sanitize_filename(filename)
        assert sanitized == ""


class TestSecurityConstants:
    """Test security configuration constants."""

    def test_secret_key_exists(self):
        """Test that secret key is defined."""
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0

    def test_algorithm_is_valid(self):
        """Test that algorithm is valid."""
        assert ALGORITHM == "HS256"