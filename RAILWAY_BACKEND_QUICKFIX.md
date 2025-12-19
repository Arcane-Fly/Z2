# Railway Backend Deployment - Quick Fix

## The Problem
```
❌ Error: /bin/bash: line 1: yarn: command not found
❌ Service: Z2B (Backend)
❌ Cause: Wrong root directory in Railway service settings
```

## The Solution

### Option 1: Railway Dashboard (Recommended)
1. Go to: https://railway.app/project/359de66a-b9de-486c-8fb4-c56fda52344f
2. Click: Z2B service
3. Click: Settings tab
4. Find: Root Directory
5. Change: `/` → `backend`
6. Click: Save
7. Click: Deploy > Redeploy

### Option 2: Railway CLI
```bash
railway link 169631f2-0f90-466d-89b8-a67f240a18b5
railway service settings --root backend
railway up --force
```

## Verify Fix

After deployment, check:
```bash
curl https://z2b-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "Z2 Backend",
  ...
}
```

## Why This Works

**Before (WRONG):**
```
Railway Service Root: /
Uses: railpack.json (Node.js config)
Tries: yarn start ❌
```

**After (CORRECT):**
```
Railway Service Root: backend
Uses: backend/railpack.json (Python config)
Runs: uvicorn app.main:app --host 0.0.0.0 --port $PORT ✅
```

## Need More Details?

See: `docs/RAILWAY_BACKEND_FIX.md`

## Validate Config

Before deploying, run:
```bash
./scripts/validate-railway-backend.sh
```

All checks should pass ✅
