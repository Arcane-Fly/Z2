# Railway Mount Path Fix

## Problem Solved

**Issue**: Railway deployment was failing with "poetry: command not found" during volume mounting phase, causing repeated container restart attempts.

**Root Cause**: 
- Conflicting Railway configuration files caused Railway to use incorrect deployment strategy
- Root `railpack.json` with multi-service format was being detected instead of individual service configs
- Volume mounting was interfering with proper Python environment setup

## Solution Applied

### 1. Removed Conflicting Configuration

**Before**: Root `railpack.json` with multi-service format
```json
{
  "services": {
    "backend": { ... },
    "frontend": { ... }
  }
}
```

**After**: Moved to `railpack.json.multi-service-backup` and rely on individual service configs

### 2. Enhanced Backend Configuration

**File**: `/backend/railpack.json`

**Improvements**:
- Pinned Poetry version to `1.6.1` for consistency
- Added `poetry config virtualenvs.create false` to avoid virtual environment conflicts
- Changed to `--no-dev` for production builds
- Ensured proper dependency resolution order

```json
{
  "$schema": "https://schema.railpack.com",
  "provider": "python",
  "packages": {
    "python": "3.12"
  },
  "buildAptPackages": ["libpq-dev", "gcc", "g++"],
  "steps": {
    "install": {
      "commands": [
        "pip install --upgrade pip",
        "pip install poetry==1.6.1",
        "poetry config virtualenvs.create false",
        "poetry install --no-root --no-dev"
      ]
    }
  },
  "deploy": {
    "inputs": ["...", { "step": "install" }],
    "startCommand": "poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### 3. Service Configuration Strategy

**Backend Service**:
- Root directory: `backend/`
- Builder: RAILPACK (as specified in `backend/railway.json`)
- Configuration: `backend/railpack.json`

**Frontend Service**:
- Root directory: `frontend/`
- Builder: RAILPACK (as specified in `frontend/railway.json`)
- Configuration: `frontend/railpack.json` (if needed) or relies on default Node.js detection

## Expected Results

After applying these changes:

1. **Build Logs**: Should show "Using Railpack" without configuration conflicts
2. **Poetry Installation**: Will be available during container startup
3. **Volume Mounting**: Will occur after proper environment setup
4. **Service Isolation**: Each service uses its own configuration without interference

## Railway Deployment Instructions

1. **Service Creation**:
   - Create backend service with root directory: `backend/`
   - Create frontend service with root directory: `frontend/`

2. **Builder Configuration**:
   - Backend: Will use RAILPACK builder via `backend/railway.json`
   - Frontend: Will use RAILPACK builder via `frontend/railway.json`

3. **Volume Configuration**:
   - Both services can share the `app_storage` volume at `/app/storage`
   - Volume mounting will occur after successful environment setup

## Validation

The fix addresses the specific error pattern:
```
Mounting volume on: /var/lib/containers/railwayapp/bind-mounts/.../vol_*
/bin/bash: line 1: poetry: command not found
```

By ensuring:
1. ✅ Poetry is installed before any startup commands
2. ✅ No configuration conflicts between root and service-specific configs
3. ✅ Proper service isolation and dependency resolution
4. ✅ Volume mounting happens after environment is ready

## Files Modified

- ✅ `railpack.json` → `railpack.json.multi-service-backup` (moved to backup)
- ✅ `backend/railpack.json` (enhanced Poetry installation)
- ✅ Added this documentation file

## Validation

A validation script has been created to verify the configuration:

```bash
cd backend/
../scripts/validate-backend-config.sh
```

This script checks:
- ✅ JSON syntax validity
- ✅ Required Railpack fields
- ✅ Poetry installation commands
- ✅ FastAPI app structure
- ✅ Builder configuration

## Next Steps

1. **Deploy the backend service**:
   - Create service in Railway
   - Set root directory to `backend/`
   - Railway will auto-detect configurations

2. **Monitor deployment**:
   - Check logs for "Using Railpack" confirmation
   - Verify Poetry installation completes successfully
   - Ensure volume mounting occurs after environment setup

3. **Verify deployment**:
   - Check service health at `/health` endpoint
   - Confirm no "poetry: command not found" errors
   - Test application functionality

## Troubleshooting

If issues persist:

1. **Check service root directory**: Must be set to `backend/`
2. **Verify builder**: Should show "RAILPACK" in Railway settings
3. **Check logs**: Look for Poetry installation in build logs
4. **Volume timing**: Ensure volume mounting happens after build steps