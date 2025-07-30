# Railway Railpack Deployment Fix

## Problem Solved

**Issue**: Railway deployment was failing because the service was configured to use Nixpacks instead of Railpack builder, despite having a railpack.json configuration file.

**Root Cause**: 
- Railway requires explicit opt-in to Railpack beta through service settings
- The original railpack.json had incorrect multi-service format (not supported by Railpack)
- Start command included redundant `cd backend` when using proper root directory configuration

## Solution Applied

### 1. Fixed Railpack Configuration

**Before**: Multi-service configuration with incorrect format
```json
{
  "services": {
    "backend": {
      "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    }
  }
}
```

**After**: Single-service Railpack configuration
```json
{
  "$schema": "https://schema.railpack.com",
  "provider": "python",
  "packages": {
    "python": "3.11"
  },
  "buildAptPackages": ["gcc", "g++"],
  "steps": {
    "install": {
      "commands": ["pip install poetry", "poetry install --no-root"]
    }
  },
  "deploy": {
    "startCommand": "poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### 2. Configuration Placement

- **Root**: `railpack.json` (for services using entire repo)
- **Backend**: `backend/railpack.json` (for services with backend root directory)

### 3. Validation Script

Created `scripts/validate-railpack.sh` to verify configuration correctness:
- ✅ JSON syntax validation
- ✅ Schema compliance check
- ✅ Required fields verification
- ✅ FastAPI app import test

## Railway Setup Instructions

### Option 1: Use Railpack Builder (Recommended)

1. **Enable Railpack in Railway Dashboard:**
   - Go to your Railway project
   - Navigate to service settings
   - Change "Builder" from "Nixpacks" to "Railpack"
   - Save changes

2. **Service Configuration:**
   - Set root directory to `backend/` for the backend service
   - Railway will automatically detect and use `backend/railpack.json`

3. **Environment Variables:**
   Railway will automatically provide `$PORT` and other variables.

### Option 2: Multi-Service Docker Deployment

If you need both frontend and backend services:

1. Create separate services in Railway:
   - Backend service: root directory `backend/`, uses `Dockerfile.backend`
   - Frontend service: root directory `frontend/`, uses `Dockerfile.frontend`

2. Use Docker builder instead of Railpack for multi-service setup

## Verification

Run the validation script:
```bash
cd backend/
../scripts/validate-railpack.sh
```

Expected output:
```
✅ Railpack configuration valid
✅ FastAPI application module is valid
```

## Key Changes Made

1. **Simplified railpack.json**: Removed multi-service configuration, used proper Railpack schema
2. **Fixed start command**: Removed redundant `cd backend` command
3. **Added validation**: Created script to verify configuration
4. **Proper schema**: Uses official Railpack schema with Python provider

## Expected Deployment Behavior

After applying these changes and enabling Railpack in Railway:

1. **Build Logs**: Should show "Using Railpack" instead of "Using Nixpacks"
2. **Build Process**: Poetry dependencies installed, app starts with uvicorn
3. **Health Check**: `/health` endpoint responds correctly
4. **Service Status**: Running and accessible via Railway public domain

## Next Steps

1. Enable Railpack builder in Railway service settings
2. Redeploy the service
3. Monitor logs for "Using Railpack" confirmation
4. Verify service health at deployed URL