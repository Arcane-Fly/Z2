# Railway Volume Mount Configuration Guide

## Problem Resolution

This document addresses the Railway Frontend Volume & Poetry Runtime issues where:
- ❌ Volume was mounting to auto-generated path instead of `/app/storage`
- ❌ Frontend service was trying to execute Poetry commands
- ❌ Container restart loops due to command-not-found errors

## Solution Applied

### 1. Fixed Railpack Configurations

**Root `railpack.json`**: Now properly configured as multi-service with explicit volume mounts
- Frontend service: Node.js provider with `npm run preview` (no Poetry)
- Backend service: Python provider with Poetry commands
- Both services: Explicit `/app/storage` volume mount configuration

**Individual Service Configs**: Updated with volume mount specifications
- `frontend/railpack.json`: Node.js configuration with storage volume
- `backend/railpack.json`: Python configuration with storage volume

### 2. Volume Mount Configuration

All configurations now include explicit volume definitions:
```json
{
  "volumes": [
    {
      "name": "app_storage",
      "mountPath": "/app/storage"
    }
  ],
  "variables": {
    "STORAGE_PATH": "/app/storage"
  }
}
```

## Railway Service Setup Instructions

### Option 1: Multi-Service Configuration (Recommended)

Use the root `railpack.json` for automatic service detection:

1. **Create Railway Project** from this repository
2. **Railway will automatically create two services**:
   - `backend`: Uses `./backend` root directory
   - `frontend`: Uses `./frontend` root directory
3. **Volume Configuration**: Both services share `app_storage` volume mounted at `/app/storage`

### Option 2: Manual Service Configuration

If you need to create services manually:

1. **Backend Service**:
   - Root Directory: `./backend`
   - Builder: Railpack
   - Uses: `backend/railpack.json`

2. **Frontend Service**:
   - Root Directory: `./frontend`
   - Builder: Railpack
   - Uses: `frontend/railpack.json`

3. **Volume Setup**:
   - Create shared volume named `app_storage`
   - Mount to `/app/storage` on both services

## Environment Variables

Services will automatically receive these variables:

### Frontend Service
- `PORT`: Railway-provided port
- `NODE_ENV`: production
- `VITE_API_BASE_URL`: Backend service URL
- `VITE_WS_BASE_URL`: Backend WebSocket URL
- `STORAGE_PATH`: /app/storage

### Backend Service
- `PORT`: Railway-provided port
- `PYTHON_VERSION`: 3.12
- `POETRY_VERSION`: 1.6.1
- `STORAGE_PATH`: /app/storage
- `CORS_ORIGINS`: Frontend service URL

## Validation

Run the validation script to verify configuration:
```bash
python3 scripts/validate_railpack_volume_config.py
```

Expected output:
- ✅ All railpack configurations valid
- ✅ Frontend uses Node.js (no Poetry dependency)
- ✅ Backend uses Python with Poetry
- ✅ Volume mount paths correctly set to `/app/storage`

## Troubleshooting

### If Frontend Still Shows Poetry Errors
1. Verify Railway service uses `./frontend` root directory
2. Check that `frontend/railpack.json` is being used (not root)
3. Confirm start command is `npm run preview`

### If Volume Mount Path is Auto-Generated
1. Check Railway dashboard volume configuration
2. Ensure volume mount path is explicitly set to `/app/storage`
3. Verify `RAILWAY_VOLUME_MOUNT_PATH` environment variable

### Build Verification
```bash
# Test frontend build
cd frontend && npm ci && npm run build

# Test validation
python3 scripts/validate_railpack_volume_config.py
```

## Expected Results After Deployment

1. **Frontend Service**:
   - ✅ Builds using Node.js/npm (no Poetry errors)
   - ✅ Starts with `npm run preview`
   - ✅ Volume mounted at `/app/storage`
   - ✅ No container restart loops

2. **Backend Service**:
   - ✅ Builds using Python/Poetry
   - ✅ Starts with `poetry run uvicorn`
   - ✅ Volume mounted at `/app/storage`
   - ✅ Shared storage with frontend

3. **Volume Storage**:
   - ✅ Persistent across deployments
   - ✅ Accessible at `/app/storage` path
   - ✅ Shared between frontend and backend
   - ✅ No auto-generated paths

## Files Modified

- `/railpack.json`: Updated to multi-service with volume configuration
- `/frontend/railpack.json`: Added volume mount and storage path
- `/backend/railpack.json`: Added volume mount configuration
- `/scripts/validate_railpack_volume_config.py`: New validation script
- `/docs/railway-volume-mount-fix.md`: This documentation