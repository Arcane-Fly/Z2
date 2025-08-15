#!/usr/bin/env python3
"""
Storage initialization and diagnostic script for Railway deployment.

This script helps diagnose and fix storage-related issues in Railway deployments.
It can be run independently or integrated into the application startup.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add the backend directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.core.config import settings
    from app.core.storage_config import StorageConfig
except ImportError:
    # Fallback if imports fail
    settings = None
    StorageConfig = None


class StorageDiagnostic:
    """Comprehensive storage diagnostic and repair utility."""

    CRITICAL_PATHS = [
        "/app/storage",
        "/data",
        "/storage",
        "/workspace/storage",
        "/opt/app/storage",
        "/tmp/storage"
    ]

    def __init__(self):
        self.results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "environment": self._get_environment_info(),
            "path_tests": {},
            "recommendations": [],
            "actions_taken": [],
            "final_status": "unknown"
        }

    def run_full_diagnostic(self) -> dict[str, Any]:
        """Run complete storage diagnostic."""
        print("🔍 Running Z2 Storage Diagnostic...")
        print("=" * 50)

        # Test all potential storage paths
        self._test_all_paths()

        # Check Railway environment
        self._check_railway_environment()

        # Test current configuration
        self._test_current_config()

        # Generate recommendations
        self._generate_recommendations()

        # Attempt automatic fixes
        self._attempt_fixes()

        # Print results
        self._print_results()

        return self.results

    def _get_environment_info(self) -> dict[str, Any]:
        """Get environment information."""
        env_info = {
            "platform": os.name,
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "user": os.getenv("USER", "unknown"),
            "home": os.getenv("HOME", "unknown"),
        }

        # Railway-specific variables
        railway_vars = {}
        for key in os.environ:
            if key.startswith("RAILWAY_"):
                railway_vars[key] = os.environ[key]
        env_info["railway_variables"] = railway_vars

        # Storage-related variables
        storage_vars = {}
        for key in os.environ:
            if "STORAGE" in key.upper():
                storage_vars[key] = os.environ[key]
        env_info["storage_variables"] = storage_vars

        return env_info

    def _test_all_paths(self):
        """Test all potential storage paths."""
        print("🧪 Testing storage paths...")

        for path in self.CRITICAL_PATHS:
            result = self._test_path(path)
            self.results["path_tests"][path] = result

            status_icon = "✅" if result["accessible"] else "❌"
            print(f"  {status_icon} {path}: {result['status']}")

    def _test_path(self, path: str) -> dict[str, Any]:
        """Test a specific storage path."""
        path_obj = Path(path)
        result = {
            "path": path,
            "exists": False,
            "accessible": False,
            "writable": False,
            "status": "",
            "error": None
        }

        try:
            # Test existence
            result["exists"] = path_obj.exists()

            # Test accessibility (try to create if not exists)
            path_obj.mkdir(parents=True, exist_ok=True)
            result["accessible"] = True

            # Test write access
            test_file = path_obj / f".test_{int(datetime.now(UTC).timestamp())}"
            test_file.write_text("test")
            test_file.unlink()
            result["writable"] = True

            result["status"] = "Fully accessible and writable"

        except PermissionError as e:
            result["error"] = str(e)
            result["status"] = "Permission denied"
        except OSError as e:
            result["error"] = str(e)
            result["status"] = f"OS error: {str(e)}"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = f"Unexpected error: {str(e)}"

        return result

    def _check_railway_environment(self):
        """Check Railway-specific environment."""
        print("🚂 Checking Railway environment...")

        railway_vars = self.results["environment"]["railway_variables"]

        if not railway_vars:
            print("  ⚠️  Not running in Railway environment")
            return

        print("  ✅ Railway environment detected")
        print(f"     Project ID: {railway_vars.get('RAILWAY_PROJECT_ID', 'N/A')}")
        print(f"     Service ID: {railway_vars.get('RAILWAY_SERVICE_ID', 'N/A')}")
        print(f"     Environment: {railway_vars.get('RAILWAY_ENVIRONMENT', 'N/A')}")

    def _test_current_config(self):
        """Test current application configuration."""
        print("⚙️  Testing current configuration...")

        if settings:
            current_path = settings.storage_path
            print(f"  📁 Configured storage path: {current_path}")

            if current_path in self.results["path_tests"]:
                result = self.results["path_tests"][current_path]
                if result["accessible"]:
                    print("  ✅ Current configuration is working")
                else:
                    print(f"  ❌ Current configuration failed: {result['status']}")
            else:
                # Test the configured path separately
                result = self._test_path(current_path)
                self.results["path_tests"][current_path] = result

                status_icon = "✅" if result["accessible"] else "❌"
                print(f"  {status_icon} {result['status']}")
        else:
            print("  ⚠️  Could not load application configuration")

    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        print("💡 Generating recommendations...")

        working_paths = [
            path for path, result in self.results["path_tests"].items()
            if result["accessible"]
        ]

        if not working_paths:
            self.results["recommendations"].extend([
                "❌ No storage paths are accessible",
                "🔧 Check Railway volume configuration",
                "🔧 Verify Railway service permissions",
                "🔧 Contact Railway support if issue persists"
            ])
            self.results["final_status"] = "critical"
        elif settings and settings.storage_path in working_paths:
            self.results["recommendations"].append("✅ Current configuration is optimal")
            self.results["final_status"] = "good"
        else:
            preferred_path = working_paths[0]
            self.results["recommendations"].extend([
                f"🔧 Change Railway volume mount to: {preferred_path}",
                f"🔧 Set environment variable: STORAGE_PATH={preferred_path}",
                "🔧 Redeploy the service after making changes"
            ])
            self.results["final_status"] = "needs_attention"

        for rec in self.results["recommendations"]:
            print(f"  {rec}")

    def _attempt_fixes(self):
        """Attempt automatic fixes where possible."""
        print("🔧 Attempting automatic fixes...")

        working_paths = [
            path for path, result in self.results["path_tests"].items()
            if result["accessible"]
        ]

        if working_paths:
            # Initialize working storage paths
            for path in working_paths[:2]:  # Initialize top 2 working paths
                try:
                    self._initialize_storage_structure(path)
                    self.results["actions_taken"].append(f"Initialized storage structure at {path}")
                    print(f"  ✅ Initialized storage at {path}")
                except Exception as e:
                    print(f"  ❌ Failed to initialize {path}: {str(e)}")

        # Create Railway configuration file
        try:
            self._create_railway_config_file()
            self.results["actions_taken"].append("Created Railway configuration guide")
            print("  ✅ Created Railway configuration guide")
        except Exception as e:
            print(f"  ❌ Failed to create config guide: {str(e)}")

    def _initialize_storage_structure(self, base_path: str):
        """Initialize storage directory structure."""
        base = Path(base_path)
        subdirs = ["uploads", "temp", "cache", "logs", "backups"]

        for subdir in subdirs:
            (base / subdir).mkdir(exist_ok=True)

        # Create marker file
        marker = base / ".z2_storage_initialized"
        marker.write_text(json.dumps({
            "initialized_at": datetime.now(UTC).isoformat(),
            "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID", "unknown"),
            "service_id": os.getenv("RAILWAY_SERVICE_ID", "unknown"),
            "diagnostic_version": "1.0"
        }, indent=2))

    def _create_railway_config_file(self):
        """Create Railway configuration guide file."""
        working_paths = [
            path for path, result in self.results["path_tests"].items()
            if result["accessible"]
        ]

        if not working_paths:
            return

        config_guide = {
            "railway_storage_configuration": {
                "recommended_mount_path": working_paths[0],
                "alternative_paths": working_paths[1:3] if len(working_paths) > 1 else [],
                "environment_variables": {
                    "STORAGE_PATH": working_paths[0],
                    "STORAGE_TYPE": "local"
                },
                "volume_configuration": {
                    "name": "z2_storage",
                    "mount_path": working_paths[0]
                },
                "verification_endpoints": [
                    "/api/v1/debug/storage",
                    "/api/v1/debug/test-storage",
                    "/health"
                ],
                "troubleshooting_steps": [
                    "1. Update Railway service volume mount path",
                    "2. Set STORAGE_PATH environment variable",
                    "3. Redeploy the service",
                    "4. Check /api/v1/debug/storage endpoint",
                    "5. Monitor application logs for storage errors"
                ]
            },
            "diagnostic_results": self.results
        }

        config_file = Path("/tmp/railway_storage_config.json")
        config_file.write_text(json.dumps(config_guide, indent=2))

    def _print_results(self):
        """Print final diagnostic results."""
        print("\n" + "=" * 50)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 50)

        status_emoji = {
            "good": "✅",
            "needs_attention": "⚠️",
            "critical": "❌",
            "unknown": "❓"
        }

        final_status = self.results["final_status"]
        print(f"Status: {status_emoji.get(final_status, '❓')} {final_status.upper()}")

        working_count = sum(1 for result in self.results["path_tests"].values() if result["accessible"])
        total_count = len(self.results["path_tests"])
        print(f"Working paths: {working_count}/{total_count}")

        if self.results["actions_taken"]:
            print("\nActions taken:")
            for action in self.results["actions_taken"]:
                print(f"  • {action}")

        print("\nDetailed results saved to: /tmp/railway_storage_config.json")
        print("=" * 50)


def main():
    """Main diagnostic entry point."""
    try:
        diagnostic = StorageDiagnostic()
        results = diagnostic.run_full_diagnostic()

        # Exit with appropriate code
        if results["final_status"] == "critical":
            sys.exit(1)
        elif results["final_status"] == "needs_attention":
            sys.exit(2)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"❌ Diagnostic failed: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    main()
