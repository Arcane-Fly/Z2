# Railway Backend Deployment Fix - Z2B Service

## Issue Summary

**Date**: December 19, 2025  
**Service**: Z2B (Backend)  
**Error**: `/bin/bash: line 1: yarn: command not found`  
**Status**: ❌ CONFIGURATION ERROR

## Root Cause

The Z2B backend service on Railway is configured to deploy from the **repository root** instead of the **`backend` directory**. This causes Railway to:

1. Find and use the root `railpack.json` (Node.js configuration)
2. Try to execute `yarn start` command (which doesn't exist in a Python environment)
3. Fail with "yarn: command not found" error

## The Problem

```
Railway Service Configuration (INCORRECT):
├── Root Directory: / (repository root)
├── Found: railpack.json (Node.js config)
└── Tries to run: yarn start ❌

Expected Configuration (CORRECT):
├── Root Directory: /backend
├── Found: backend/railpack.json (Python config)
└── Should run: uvicorn app.main:app --host 0.0.0.0 --port $PORT ✅
```

## Solution: Update Railway Service Settings

### ⚠️ CRITICAL: This fix MUST be done in Railway Dashboard

The Railway service configuration cannot be changed via git commits. You **MUST** update the service settings in the Railway dashboard.

### Steps to Fix

1. **Open Railway Dashboard**
   - Go to: https://railway.app/project/359de66a-b9de-486c-8fb4-c56fda52344f
   - Navigate to the Z2B service

2. **Update Service Settings**
   - Click on the Z2B service
   - Go to **Settings** tab
   - Find **Root Directory** setting
   - Change from `/` to `backend`
   - Click **Save**

3. **Verify Build Configuration**
   - Ensure **Builder** is set to "Railpack" (or auto-detect)
   - No custom Dockerfile or railway.toml should be present

4. **Trigger Redeploy**
   - Click **Deploy** > **Redeploy**
   - Watch the build logs to confirm it's using the correct railpack.json

### Expected Build Logs After Fix

```
✅ Using Railpack builder
✅ Found: /backend/railpack.json
✅ Provider: python
✅ Installing: pip, poetry
✅ Running: poetry install --no-root --only=main
✅ Starting: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Verification

### 1. Check Build Logs

After redeploying, verify the build logs show:
```
Found railpack.json in /backend
Provider: python
```

### 2. Test Health Endpoint

Once deployed, test the health endpoint:
```bash
curl https://z2b-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "Z2 Backend",
  "timestamp": "...",
  "checks": {...}
}
```

## Configuration Files

### Backend railpack.json (Correct Configuration)

File: `backend/railpack.json`

```json
{
  "version": "1",
  "metadata": {
    "name": "z2-backend"
  },
  "build": {
    "provider": "python",
    "steps": {
      "install": {
        "commands": [
          "pip install --upgrade pip",
          "pip install poetry==1.8.5",
          "poetry config virtualenvs.create false",
          "poetry install --no-root --only=main"
        ]
      }
    }
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Root railpack.json (NOT for Backend)

File: `railpack.json`

```json
{
  "version": "1",
  "metadata": {
    "name": "z2-workspace"
  },
  "build": {
    "provider": "node",
    ...
  },
  "deploy": {
    "startCommand": "yarn start",
    ...
  }
}
```

This is for the monorepo/frontend, NOT the backend service.

## Important Notes

### ✅ What's Already Correct

1. ✅ `backend/railpack.json` is properly configured for Python
2. ✅ No competing configuration files (Dockerfile, railway.toml, etc.)
3. ✅ Health check endpoint exists at `/health`
4. ✅ Start command uses `$PORT` and binds to `0.0.0.0`
5. ✅ Poetry dependencies are correctly defined in `pyproject.toml`

### ❌ What Needs to be Fixed

1. ❌ Railway service root directory setting (must be done in dashboard)

### 🚫 What NOT to Do

- ❌ Don't remove the root `railpack.json` (it's for frontend/monorepo)
- ❌ Don't add a Dockerfile or railway.toml to backend
- ❌ Don't try to fix this with git commits (service settings are not in git)

## Alternative: Using Railway CLI

If you prefer using Railway CLI:

```bash
# Link to the correct service
railway link 169631f2-0f90-466d-89b8-a67f240a18b5

# Set root directory
railway service settings --root backend

# Verify
railway service show

# Redeploy
railway up --force
```

## Monorepo Service Structure

For reference, here's how Railway services should be configured for this monorepo:

| Service | Root Directory | railpack.json | Provider | Start Command |
|---------|---------------|---------------|----------|---------------|
| Z2B (Backend) | `backend` | `backend/railpack.json` | Python | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Z2F (Frontend) | `frontend` | `frontend/railpack.json` | Node.js | `yarn start` |
| Monorepo (if used) | `/` | `railpack.json` | Node.js | `yarn start` |

## Related Documentation

- [RAILWAY_SERVICE_STATUS.md](../RAILWAY_SERVICE_STATUS.md)
- [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)
- [RAILWAY_RAILPACK_GUIDE.md](RAILWAY_RAILPACK_GUIDE.md)

---

**Last Updated**: December 19, 2025  
**Action Required**: Update Railway service settings to use `backend` as root directory
