# Railway Deployment Fix

## Issue
The Z2F frontend service was incorrectly using Dockerfile.frontend instead of the railpack.json configuration, causing:
- Nginx worker processes instead of Vite preview server
- Service instability and crashes
- Incorrect environment setup

## Solution
1. Renamed Dockerfile.frontend to prevent automatic Docker detection
2. Updated railpack.json configuration 
3. Added .railpacignore to control build system selection
4. Updated Railway service configuration to use yarn/node commands

## Services
- **Z2F (Frontend)**: Should use railpack.json with Node.js/Yarn
- **Z2B (Backend)**: Should use railpack.json with Python/Poetry

## Files Modified
- Dockerfile.frontend → Dockerfile.frontend.backup
- Added .railpacignore
- Updated railpack.json (if needed)

## Testing
After merge, redeploy Z2F service to verify:
1. No more Nginx worker processes in logs
2. Vite preview server starts correctly
3. Service remains stable
4. Health checks pass
