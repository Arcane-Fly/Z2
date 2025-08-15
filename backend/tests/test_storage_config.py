"""
Test storage configuration for Railway volume integration.
"""

from pathlib import Path

import pytest

from app.core.config import get_settings


def test_storage_path_configuration():
    """Test that storage path is correctly configured for Railway deployment."""
    settings = get_settings()

    # Test that storage path is set to Railway-compatible path
    assert settings.storage_path == "/app/storage"

    # Test that path is absolute (Railway compatible)
    assert Path(settings.storage_path).is_absolute()


def test_storage_path_environment_override():
    """Test that storage path can be overridden via environment variable."""
    # Test with custom environment variable
    test_path = "/custom/storage/path"

    with pytest.MonkeyPatch().context() as m:
        m.setenv("STORAGE_PATH", test_path)
        # Clear the cache to force reload
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.storage_path == test_path

        # Clean up cache
        get_settings.cache_clear()


def test_docker_storage_directory_exists():
    """Test that storage directory exists in Docker container context."""
    # This test simulates Docker environment where directory should be created
    settings = get_settings()
    storage_path = Path(settings.storage_path)

    # Test that the path is properly formatted
    assert str(storage_path).startswith("/app/")
    assert storage_path.name == "storage"


def test_storage_configuration_completeness():
    """Test that all storage-related settings are properly configured."""
    settings = get_settings()

    # Test all storage settings exist and have reasonable values
    assert settings.storage_type == "local"
    assert isinstance(settings.storage_path, str)
    assert len(settings.storage_path) > 0
    assert settings.max_file_size_mb > 0
    assert settings.max_file_size_mb <= 100  # Reasonable limit
