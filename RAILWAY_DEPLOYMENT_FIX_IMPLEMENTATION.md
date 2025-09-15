# Railway Deployment Configuration Fix

## Problem Solved

**Issue**: Railway was attempting to execute `yarn` commands in the nginx:alpine production container, which doesn't have Node.js or Yarn installed, causing startup failures.

**Root Cause**: Railway was defaulting to package.json scripts instead of respecting the Dockerfile CMD instruction for the nginx runtime container.

## Solution Implemented

### 1. Frontend Configuration (`frontend/railway.json`)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "nginx -g 'daemon off;'",
    "healthcheckPath": "/",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Key Fix**: The `startCommand` explicitly overrides Railway's default behavior and ensures nginx runs correctly in the production container.

### 2. Backend Configuration (`backend/railway.toml`)
```toml
[build]
builder = "nixpacks"
buildCommand = "pip install --upgrade pip && pip install -r requirements.txt"

[deploy]
startCommand = "python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 5

[env]
PYTHON_VERSION = "3.12"
```

### 3. Monorepo Configuration (`railway.json`)
Updated to properly define both services with their respective configurations.

## Health Check Endpoints

### Frontend (Nginx)
- **Path**: `/` (serves the React app)
- **Backup**: `/health` (nginx-specific health check)
- **Response**: HTTP 200 with app content

### Backend (FastAPI)
- **Path**: `/health` (comprehensive health check)
- **Additional**: `/health/live` and `/health/ready` for Kubernetes-style probes
- **Response**: JSON with service status and diagnostics

## Validation

Run the validation script to verify configuration:
```bash
./scripts/validate-railway-config.sh
```

## Deployment Commands

```bash
# Deploy both services
railway up

# Deploy specific service
railway up --service frontend
railway up --service backend

# Monitor logs
railway logs --service frontend --tail
railway logs --service backend --tail

# Check service status
railway status
```

## Architecture Overview

```
Frontend Build Flow:
node:20-alpine (build) → nginx:alpine (runtime)
├── yarn install & build (build stage)
└── nginx serves static files (runtime stage)

Backend Flow:
nixpacks → Python 3.12 → uvicorn
├── pip install requirements
└── uvicorn serves FastAPI app
```

## Key Benefits

1. **Eliminates startup failures** caused by yarn/nginx mismatch
2. **Proper health checks** for Railway monitoring
3. **Service isolation** with dedicated configurations
4. **Production-ready** with appropriate restart policies
5. **Validation script** for configuration verification

## Files Modified

- ✅ `frontend/railway.json` (created)
- ✅ `backend/railway.toml` (created)  
- ✅ `railway.json` (updated for monorepo)
- ✅ `scripts/validate-railway-config.sh` (created)

## Verification Steps

1. **Pre-deployment**: Run validation script
2. **Post-deployment**: Check service logs for successful startup
3. **Health checks**: Verify endpoints respond correctly
4. **Monitoring**: Ensure no startup failures in Railway dashboard