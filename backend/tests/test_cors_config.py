"""
Test CORS configuration parsing functionality.

Tests the field validator that handles multiple CORS origins input formats
including JSON arrays and comma-separated strings.
"""

import os
import pytest
from unittest.mock import patch

from app.core.config import Settings


class TestCORSConfiguration:
    """Test CORS configuration parsing and validation."""

    def test_default_cors_origins(self):
        """Test default CORS origins when no environment variable is set."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.cors_origins_list == ["http://localhost:3000", "http://localhost:5173"]

    def test_json_array_format(self):
        """Test parsing CORS origins from JSON array format."""
        cors_value = '["https://frontend.com","https://app.domain.com","http://localhost:3000"]'
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            expected = ["https://frontend.com", "https://app.domain.com", "http://localhost:3000"]
            assert settings.cors_origins_list == expected

    def test_comma_separated_format(self):
        """Test parsing CORS origins from comma-separated format."""
        cors_value = "https://frontend.com,https://app.domain.com,http://localhost:3000"
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            expected = ["https://frontend.com", "https://app.domain.com", "http://localhost:3000"]
            assert settings.cors_origins_list == expected

    def test_comma_separated_with_spaces(self):
        """Test parsing CORS origins from comma-separated format with spaces."""
        cors_value = "https://frontend.com, https://app.domain.com, http://localhost:3000"
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            expected = ["https://frontend.com", "https://app.domain.com", "http://localhost:3000"]
            assert settings.cors_origins_list == expected

    def test_single_origin(self):
        """Test parsing single CORS origin."""
        cors_value = "https://frontend.com"
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            expected = ["https://frontend.com"]
            assert settings.cors_origins_list == expected

    def test_empty_string(self):
        """Test handling empty CORS origins string."""
        cors_value = ""
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            # Should fallback to defaults
            assert settings.cors_origins_list == ["http://localhost:3000", "http://localhost:5173"]

    def test_whitespace_only(self):
        """Test handling whitespace-only CORS origins string."""
        cors_value = "   "
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            # Should fallback to defaults
            assert settings.cors_origins_list == ["http://localhost:3000", "http://localhost:5173"]

    def test_railway_production_format(self):
        """Test Railway production JSON format with domain variables."""
        cors_value = '["https://z2f-production.up.railway.app"]'
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            expected = ["https://z2f-production.up.railway.app"]
            assert settings.cors_origins_list == expected

    def test_mixed_protocol_origins(self):
        """Test mixed HTTP and HTTPS origins."""
        cors_value = "https://secure.domain.com,http://localhost:3000,http://localhost:5173"
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            expected = ["https://secure.domain.com", "http://localhost:3000", "http://localhost:5173"]
            assert settings.cors_origins_list == expected

    def test_malformed_json_fallback_to_comma_parsing(self):
        """Test that malformed JSON falls back to comma-separated parsing."""
        # This is a malformed JSON but valid comma-separated string
        cors_value = '["https://frontend.com","missing-quote]'
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            # Should parse as comma-separated when JSON parsing fails
            expected = ['["https://frontend.com"', '"missing-quote]']
            assert settings.cors_origins_list == expected

    def test_empty_json_array(self):
        """Test empty JSON array."""
        cors_value = "[]"
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            # Should fallback to defaults when empty
            assert settings.cors_origins_list == ["http://localhost:3000", "http://localhost:5173"]

    def test_json_array_with_empty_strings(self):
        """Test JSON array with empty strings (should be filtered out)."""
        cors_value = '["https://frontend.com","","http://localhost:3000"]'
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            expected = ["https://frontend.com", "http://localhost:3000"]
            assert settings.cors_origins_list == expected

    def test_comma_separated_with_empty_values(self):
        """Test comma-separated with empty values (should be filtered out)."""
        cors_value = "https://frontend.com,,http://localhost:3000,"
        
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings = Settings()
            expected = ["https://frontend.com", "http://localhost:3000"]
            assert settings.cors_origins_list == expected

    def test_settings_instantiation_does_not_fail(self):
        """Test that Settings can be instantiated with various CORS formats without errors."""
        test_cases = [
            '["https://frontend.com"]',
            'https://frontend.com,http://localhost:3000',
            'https://frontend.com',
            '',
            '[]',
            'https://app1.com, https://app2.com',
        ]
        
        for cors_value in test_cases:
            with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
                # This should not raise any exceptions
                settings = Settings()
                assert isinstance(settings.cors_origins_list, list)
                assert len(settings.cors_origins_list) > 0  # Should always have at least defaults


@pytest.mark.asyncio
class TestCORSIntegration:
    """Test CORS configuration integration with FastAPI application."""

    def test_application_starts_with_comma_separated_cors(self):
        """Test that the FastAPI application starts successfully with comma-separated CORS."""
        from app.main import create_application
        
        cors_value = "https://frontend.com,http://localhost:3000"
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            # This should not raise any exceptions during app creation
            app = create_application()
            assert app is not None

    def test_application_starts_with_json_cors(self):
        """Test that the FastAPI application starts successfully with JSON CORS."""
        from app.main import create_application
        
        cors_value = '["https://frontend.com","http://localhost:3000"]'
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            # This should not raise any exceptions during app creation
            app = create_application()
            assert app is not None

    def test_cors_middleware_gets_correct_origins(self):
        """Test that CORS middleware receives the correct origins list."""
        from app.core.config import settings
        
        cors_value = "https://frontend.com,http://localhost:3000"
        with patch.dict(os.environ, {"CORS_ORIGINS": cors_value}):
            settings_instance = Settings()
            cors_list = settings_instance.cors_origins_list
            
            # Verify the list is properly formatted for middleware
            assert isinstance(cors_list, list)
            assert "https://frontend.com" in cors_list
            assert "http://localhost:3000" in cors_list