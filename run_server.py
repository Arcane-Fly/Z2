#!/usr/bin/env python3
"""
Z2 Platform Server Entry Point

This script serves as the main entry point for the Z2 platform when deployed
as a monorepo. It starts the FastAPI backend server.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def main():
    """Main entry point for the Z2 server."""
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Configure uvicorn settings
    config = {
        "app": "app.main:app",
        "host": host,
        "port": port,
        "log_level": os.getenv("LOG_LEVEL", "info").lower(),
        "access_log": True,
        "workers": int(os.getenv("WORKERS", 1)),
    }
    
    # Add reload in development
    if os.getenv("PYTHON_ENV") != "production":
        config["reload"] = True
        config["reload_dirs"] = [str(backend_path / "app")]
    
    print(f"🚀 Starting Z2 Backend Server on {host}:{port}")
    print(f"📁 Backend path: {backend_path}")
    print(f"🌍 Environment: {os.getenv('PYTHON_ENV', 'development')}")
    
    # Change to backend directory for proper imports
    os.chdir(backend_path)
    
    # Start the server
    uvicorn.run(**config)

if __name__ == "__main__":
    main()