# Railway Z2B Deployment Troubleshooting

## Current Issue: "yarn: command not found"

If you're seeing this error in the Deploy Logs:
```
/bin/bash: line 1: yarn: command not found
```

This means Railway is trying to execute `yarn start` in a Python container, which will always fail.

## Root Cause

Even though:
- ✅ Root Directory is set to `backend`
- ✅ `railpack.json` has correct `startCommand: "uvicorn..."`
- ✅ `nixpacks.toml` has correct start command
- ✅ `Procfile` has correct start command

**Railway is ignoring all of these** because there's likely a **Custom Start Command** explicitly set in the dashboard that overrides everything.

## Solution: Check and Update Start Command in Railway Dashboard

### Step 1: Check Current Start Command

1. Go to Railway Dashboard → Z2B Service → **Settings**
2. Look for **Deploy** section
3. Find **Custom Start Command** or **Start Command** field

### Step 2: Fix the Start Command

You have two options:

#### Option A: Clear the Custom Start Command (Recommended)
1. If the field shows `yarn start` or anything else
2. **Delete/Clear** the entire Custom Start Command field
3. Leave it **empty** or set to **default**
4. Railway will auto-detect from `railpack.json`, `Procfile`, or `nixpacks.toml`

#### Option B: Set the Correct Command Explicitly
1. Set Custom Start Command to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Step 3: Verify Other Settings

While you're in Settings, double-check:

**Service Settings:**
- ✅ Root Directory: `backend`
- ✅ Builder: Nixpacks (default)

**Deploy Settings:**
- ✅ Start Command: Empty OR `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ Health Check Path: `/health`
- ✅ Health Check Timeout: `300` (or 5 minutes)

### Step 4: Trigger Redeploy

1. Save all changes
2. Go to **Deployments** tab
3. Click **Deploy** → **Redeploy**
4. Or make a small code change and push to trigger auto-deploy

## Expected Results After Fix

### Build Logs Should Show:
```
✓ install apt packages: libpq-dev python3-dev
✓ install mise packages: python
✓ pip install -r requirements.txt
✓ poetry install --no-root --only=main
```

### Deploy Logs Should Show:
```
Starting Container
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Health Check Should Show:
```
====================
Starting Healthcheck
====================
Path: /health

[1/1] Healthcheck succeeded!
```

## If Problem Persists

### Check 1: Environment Variables
Ensure these are set in Railway:
- `DATABASE_URL` (if using database)
- `REDIS_URL` (if using Redis)
- Any required API keys

### Check 2: View Deployment Settings via Railway CLI

If you have Railway CLI installed:
```bash
cd backend
railway status
railway variables
```

### Check 3: Manual Deploy Test

Test if the start command works:
```bash
cd backend
export PORT=8000
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Then check: http://localhost:8000/health

## Common Mistakes

1. ❌ **Setting Custom Start Command to `yarn start`** - This is for Node.js, not Python
2. ❌ **Root Directory not set to `backend`** - Railway will use wrong config files
3. ❌ **Health check path wrong** - Should be `/health` not `/api/health` for backend
4. ❌ **Missing PORT variable in command** - Must use `$PORT` not `8000`

## Configuration Priority in Railway

Railway uses this priority order (highest to lowest):

1. **Custom Start Command in Dashboard** ← This overrides everything!
2. `railway.toml` start command
3. `Procfile` command
4. `nixpacks.toml` start command
5. `railpack.json` startCommand
6. Auto-detected start command

If #1 (Custom Start Command) is set to `yarn start`, Railway will never look at any config files.

## Screenshots Reference

When you're in Railway Dashboard Settings, you should see:

```
Service
├─ Service Name: Z2B
├─ Root Directory: backend ← MUST be set
└─ ...

Deploy
├─ Custom Start Command: [empty or uvicorn command] ← CHECK THIS
├─ Health Check Path: /health
└─ Health Check Timeout: 300
```

## Need More Help?

1. **Check the Railway Service Settings** - Screenshot the Deploy section and share
2. **Export Service Configuration** - Use Railway CLI: `railway service`
3. **Contact Railway Support** - Reference Service ID: `169631f2-0f90-466d-89b8-a67f240a18b5`

---

**Last Updated**: October 22, 2025
**Status**: Configuration files are correct, awaiting Railway dashboard update
