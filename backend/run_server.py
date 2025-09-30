#!/usr/bin/env python3
"""
Z2 Backend Server Entry Point

This script serves as the entry point for the Z2 backend service
when deployed via Railway.
"""

import os
import uvicorn

def main():
    """Main entry point for the Z2 backend server."""
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Z2 Backend Server on {host}:{port}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Start the server with explicit app reference
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True,
    )

if __name__ == "__main__":
    main()