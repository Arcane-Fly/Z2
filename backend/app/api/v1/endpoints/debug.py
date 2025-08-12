"""
Debug endpoints for troubleshooting Railway storage and deployment issues.
"""

import os
import platform
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.auth_dependencies import get_current_active_user
from app.core.config import settings
from app.models.user import User

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/storage")
async def debug_storage(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Debug storage configuration and test storage access.
    
    This endpoint helps troubleshoot Railway volume mount issues by:
    - Checking storage path configuration
    - Testing directory access and permissions
    - Providing alternative path suggestions
    """
    try:
        storage_path = Path(settings.storage_path)
        
        # Test directory creation and access
        directory_tests = {}
        write_tests = {}
        
        # Test current storage path
        try:
            storage_path.mkdir(parents=True, exist_ok=True)
            directory_tests[str(storage_path)] = "✅ Directory created/exists"
        except Exception as e:
            directory_tests[str(storage_path)] = f"❌ Cannot create: {str(e)}"
        
        # Test write access
        if storage_path.exists():
            try:
                test_file = storage_path / "test_write.txt"
                test_file.write_text(f"Test write at {datetime.now(UTC)}")
                test_file.unlink()  # Clean up
                write_tests[str(storage_path)] = "✅ Write access OK"
            except Exception as e:
                write_tests[str(storage_path)] = f"❌ Cannot write: {str(e)}"
        
        # Test alternative paths
        alternative_paths = [
            "/data",
            "/storage", 
            "/workspace/storage",
            "/opt/app/storage",
            "/tmp/storage",
        ]
        
        alternative_tests = {}
        for alt_path in alternative_paths:
            try:
                alt_path_obj = Path(alt_path)
                alt_path_obj.mkdir(parents=True, exist_ok=True)
                
                # Test write
                test_file = alt_path_obj / "test_write.txt"
                test_file.write_text(f"Test write at {datetime.now(UTC)}")
                test_file.unlink()  # Clean up
                
                alternative_tests[alt_path] = "✅ Available and writable"
            except Exception as e:
                alternative_tests[alt_path] = f"❌ Not available: {str(e)}"
        
        # Get disk usage if possible
        disk_usage = {}
        try:
            if storage_path.exists():
                usage = shutil.disk_usage(storage_path)
                disk_usage = {
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                }
        except Exception as e:
            disk_usage = {"error": str(e)}
        
        # Check Railway-specific environment variables
        railway_vars = {}
        railway_env_vars = [
            "RAILWAY_ENVIRONMENT",
            "RAILWAY_PROJECT_ID", 
            "RAILWAY_SERVICE_ID",
            "RAILWAY_DEPLOYMENT_ID",
            "RAILWAY_PUBLIC_DOMAIN",
            "RAILWAY_PRIVATE_DOMAIN",
            "PORT",
        ]
        
        for var in railway_env_vars:
            railway_vars[var] = os.getenv(var, "Not set")
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "storage_configuration": {
                "configured_path": settings.storage_path,
                "storage_type": settings.storage_type,
                "max_file_size_mb": settings.max_file_size_mb,
                "path_is_absolute": storage_path.is_absolute(),
                "path_exists": storage_path.exists(),
                "parent_exists": storage_path.parent.exists(),
            },
            "directory_tests": directory_tests,
            "write_tests": write_tests,
            "alternative_paths": alternative_tests,
            "disk_usage": disk_usage,
            "system_info": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "user": os.getenv("USER", "unknown"),
                "home": os.getenv("HOME", "unknown"),
            },
            "railway_environment": railway_vars,
            "recommendations": _get_storage_recommendations(
                directory_tests, alternative_tests
            ),
        }
        
    except Exception as e:
        logger.error("Storage debug failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage debug failed: {str(e)}"
        )


@router.get("/environment")
async def debug_environment(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Debug environment variables and configuration."""
    try:
        # Get all environment variables
        env_vars = dict(os.environ)
        
        # Separate Railway-specific vars
        railway_vars = {k: v for k, v in env_vars.items() if k.startswith("RAILWAY_")}
        storage_vars = {k: v for k, v in env_vars.items() if "STORAGE" in k.upper()}
        
        # Get application settings
        app_settings = {
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "debug": settings.debug,
            "port": settings.port,
            "host": settings.host,
            "storage_path": settings.storage_path,
            "storage_type": settings.storage_type,
            "max_file_size_mb": settings.max_file_size_mb,
        }
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "application_settings": app_settings,
            "railway_variables": railway_vars,
            "storage_variables": storage_vars,
            "total_env_vars": len(env_vars),
            "system_paths": {
                "current_directory": os.getcwd(),
                "python_path": sys.executable,
                "python_version": sys.version,
            }
        }
        
    except Exception as e:
        logger.error("Environment debug failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Environment debug failed: {str(e)}"
        )


@router.post("/test-storage")
async def test_storage_operations(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Test basic storage operations (create, write, read, delete)."""
    try:
        storage_path = Path(settings.storage_path)
        test_results = {}
        
        # Test 1: Directory creation
        try:
            storage_path.mkdir(parents=True, exist_ok=True)
            test_results["directory_creation"] = "✅ Success"
        except Exception as e:
            test_results["directory_creation"] = f"❌ Failed: {str(e)}"
            return {"test_results": test_results, "overall_status": "failed"}
        
        # Test 2: File creation
        test_file = storage_path / f"test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            test_content = f"Storage test at {datetime.now(UTC).isoformat()}"
            test_file.write_text(test_content)
            test_results["file_creation"] = "✅ Success"
        except Exception as e:
            test_results["file_creation"] = f"❌ Failed: {str(e)}"
            return {"test_results": test_results, "overall_status": "failed"}
        
        # Test 3: File reading
        try:
            read_content = test_file.read_text()
            if read_content == test_content:
                test_results["file_reading"] = "✅ Success"
            else:
                test_results["file_reading"] = "❌ Content mismatch"
        except Exception as e:
            test_results["file_reading"] = f"❌ Failed: {str(e)}"
        
        # Test 4: File deletion
        try:
            test_file.unlink()
            test_results["file_deletion"] = "✅ Success"
        except Exception as e:
            test_results["file_deletion"] = f"❌ Failed: {str(e)}"
        
        # Test 5: List directory contents
        try:
            files = list(storage_path.iterdir())
            test_results["directory_listing"] = f"✅ Success ({len(files)} items)"
        except Exception as e:
            test_results["directory_listing"] = f"❌ Failed: {str(e)}"
        
        overall_status = "success" if all("✅" in result for result in test_results.values()) else "partial"
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "storage_path": str(storage_path),
            "test_results": test_results,
            "overall_status": overall_status,
        }
        
    except Exception as e:
        logger.error("Storage test failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage test failed: {str(e)}"
        )


def _get_storage_recommendations(
    directory_tests: Dict[str, str], alternative_tests: Dict[str, str]
) -> Dict[str, Any]:
    """Generate storage configuration recommendations based on test results."""
    recommendations = {
        "immediate_actions": [],
        "alternative_paths": [],
        "railway_config": {},
    }
    
    # Check if current path is working
    current_path_working = any("✅" in result for result in directory_tests.values())
    
    if not current_path_working:
        recommendations["immediate_actions"].append(
            "Current storage path is not accessible - try alternative mount paths"
        )
        
        # Find working alternatives
        working_alternatives = [
            path for path, result in alternative_tests.items() 
            if "✅" in result
        ]
        
        if working_alternatives:
            recommendations["alternative_paths"] = working_alternatives
            recommendations["railway_config"] = {
                "recommended_mount_path": working_alternatives[0],
                "environment_variable": f"STORAGE_PATH={working_alternatives[0]}",
                "instructions": "Update Railway service volume mount path and set environment variable"
            }
        else:
            recommendations["immediate_actions"].append(
                "No alternative paths are working - check Railway volume configuration"
            )
    else:
        recommendations["immediate_actions"].append("Storage configuration is working correctly")
    
    return recommendations