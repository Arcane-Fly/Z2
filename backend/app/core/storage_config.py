"""
Enhanced storage configuration with Railway compatibility.
"""

import os
from pathlib import Path

import structlog

from app.core.config import Settings

logger = structlog.get_logger(__name__)


class StorageConfig:
    """
    Enhanced storage configuration with automatic Railway path detection.

    This class provides improved storage path resolution for Railway deployments,
    automatically falling back to working alternatives if the primary path fails.
    """

    # Ordered list of storage paths to try for Railway deployment
    RAILWAY_STORAGE_PATHS = [
        "/app/storage",        # Default Docker path (current)
        "/data",               # Simple data directory
        "/storage",            # Root storage directory
        "/workspace/storage",  # Railway workspace
        "/opt/app/storage",    # Alternative Docker path
        "/tmp/storage",        # Temporary fallback
    ]

    @classmethod
    def get_optimal_storage_path(cls, settings: Settings) -> str:
        """
        Determine the optimal storage path for the current environment.

        This method tests various paths and returns the first one that works,
        providing automatic fallback for Railway deployment issues.
        """
        # First try the configured path
        configured_path = settings.storage_path
        if cls._test_storage_path(configured_path):
            logger.info("Using configured storage path", path=configured_path)
            return configured_path

        logger.warning(
            "Configured storage path not accessible, trying alternatives",
            configured_path=configured_path
        )

        # Try Railway-optimized paths
        for path in cls.RAILWAY_STORAGE_PATHS:
            if cls._test_storage_path(path):
                logger.info("Found working storage path", path=path)
                return path

        # If all else fails, use /tmp as last resort
        fallback_path = "/tmp/z2_storage"
        logger.error(
            "No storage paths accessible, using temporary fallback",
            fallback_path=fallback_path
        )
        return fallback_path

    @classmethod
    def _test_storage_path(cls, path: str) -> bool:
        """Test if a storage path is accessible and writable."""
        try:
            path_obj = Path(path)

            # Try to create directory
            path_obj.mkdir(parents=True, exist_ok=True)

            # Test write access
            test_file = path_obj / ".storage_test"
            test_file.write_text("test")
            test_file.unlink()

            return True
        except Exception as e:
            logger.debug("Storage path test failed", path=path, error=str(e))
            return False

    @classmethod
    def initialize_storage(cls, storage_path: str) -> bool:
        """
        Initialize storage directory with proper structure.

        Creates necessary subdirectories and sets up storage structure.
        """
        try:
            base_path = Path(storage_path)
            base_path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories for organized storage
            subdirs = [
                "uploads",      # User file uploads
                "temp",         # Temporary files
                "cache",        # Cached data
                "logs",         # Application logs
                "backups",      # Data backups
            ]

            for subdir in subdirs:
                (base_path / subdir).mkdir(exist_ok=True)

            # Create a marker file to indicate successful initialization
            marker_file = base_path / ".storage_initialized"
            marker_file.write_text(f"Initialized at {os.getenv('RAILWAY_DEPLOYMENT_ID', 'local')}")

            logger.info("Storage initialized successfully", path=storage_path)
            return True

        except Exception as e:
            logger.error("Storage initialization failed", path=storage_path, error=str(e))
            return False

    @classmethod
    def get_railway_config_suggestions(cls) -> dict:
        """
        Get configuration suggestions for Railway deployment.

        Returns a dictionary with recommended Railway configuration.
        """
        return {
            "volume_mount_options": [
                {
                    "mount_path": "/data",
                    "description": "Simple data directory - recommended for most cases",
                    "environment_variable": "STORAGE_PATH=/data"
                },
                {
                    "mount_path": "/app/storage",
                    "description": "Current configuration - Docker app directory",
                    "environment_variable": "STORAGE_PATH=/app/storage"
                },
                {
                    "mount_path": "/workspace/storage",
                    "description": "Railway workspace directory",
                    "environment_variable": "STORAGE_PATH=/workspace/storage"
                },
                {
                    "mount_path": "/storage",
                    "description": "Root storage directory",
                    "environment_variable": "STORAGE_PATH=/storage"
                }
            ],
            "environment_variables": {
                "STORAGE_PATH": "Set to override default storage path",
                "STORAGE_TYPE": "Set to 'local' for file storage",
                "MAX_FILE_SIZE_MB": "Set maximum file upload size",
            },
            "troubleshooting_endpoints": [
                "/api/v1/debug/storage",
                "/api/v1/debug/environment",
                "/api/v1/debug/test-storage"
            ]
        }


class EnhancedSettings(Settings):
    """Enhanced settings with automatic storage path resolution."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Auto-detect optimal storage path for Railway
        if self._is_railway_environment():
            optimal_path = StorageConfig.get_optimal_storage_path(self)
            if optimal_path != self.storage_path:
                logger.info(
                    "Auto-adjusting storage path for Railway",
                    original=self.storage_path,
                    optimal=optimal_path
                )
                # Update the storage path
                object.__setattr__(self, 'storage_path', optimal_path)

        # Initialize storage directory
        StorageConfig.initialize_storage(self.storage_path)

    def _is_railway_environment(self) -> bool:
        """Check if running in Railway environment."""
        return any(
            env_var in os.environ
            for env_var in ['RAILWAY_ENVIRONMENT', 'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID']
        )

    @property
    def storage_subdirs(self) -> dict:
        """Get paths to storage subdirectories."""
        base_path = Path(self.storage_path)
        return {
            "uploads": str(base_path / "uploads"),
            "temp": str(base_path / "temp"),
            "cache": str(base_path / "cache"),
            "logs": str(base_path / "logs"),
            "backups": str(base_path / "backups"),
        }

    @property
    def railway_config_info(self) -> dict:
        """Get Railway configuration information."""
        return StorageConfig.get_railway_config_suggestions()


# Function to get enhanced settings (backward compatible)
def get_enhanced_settings() -> EnhancedSettings:
    """Get enhanced settings with Railway optimization."""
    return EnhancedSettings()
