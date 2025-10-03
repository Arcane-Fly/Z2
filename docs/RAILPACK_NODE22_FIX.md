# Railway Railpack Configuration Fix - Node.js 22 & Yarn 4.9.2

## Problem Resolved

**Issue**: Railway was using Nixpacks v1.39.0 instead of Railpack despite `railpack.json` configuration existing, and the root `railpack.json` had an incorrect multi-service format that Railpack doesn't support.

**Root Cause**: 
- Root `railpack.json` used unsupported multi-service configuration format
- Railway requires explicit opt-in to Railpack beta through service settings
- Node version mismatch between configurations (20.19.5 vs requirement for 22)
- Missing explicit Yarn version specification in frontend configuration

## Solution Implemented

### 1. Fixed Root railpack.json

**Before**: Multi-service configuration (NOT supported by Railpack)
```json
{
  "$schema": "https://schema.railpack.com",
  "services": {
    "backend": {
      "root": "backend"
    },
    "frontend": {
      "root": "frontend"
    }
  }
}
```

**After**: Proper Node.js/Yarn configuration
```json
{
  "$schema": "https://schema.railpack.com",
  "packages": {
    "node": "22",
    "yarn": "4.9.2"
  },
  "steps": {
    "install": {
      "commands": [
        "corepack enable",
        "yarn install --immutable"
      ]
    },
    "build": {
      "commands": [
        "yarn build"
      ]
    }
  },
  "deploy": {
    "startCommand": "yarn start"
  }
}
```

### 2. Updated Frontend railpack.json

**Changes**:
- Updated Node version from `"20.19.5"` to `"22"`
- Added explicit Yarn version `"4.9.2"`
- Aligns with `package.json` specification: `"packageManager": "yarn@4.9.2+sha512..."`

**Result**:
```json
{
  "$schema": "https://schema.railpack.com",
  "provider": "node",
  "packages": {
    "node": "22",
    "yarn": "4.9.2"
  },
  "steps": {
    "install": {
      "cache": ["yarn-cache"],
      "commands": [
        "corepack enable",
        "corepack prepare yarn@4.9.2 --activate",
        "yarn install --immutable"
      ]
    },
    "build": {
      "inputs": [{ "step": "install" }],
      "commands": ["yarn build"]
    }
  },
  "deploy": {
    "inputs": [{ "step": "build" }],
    "startCommand": "yarn start",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300
  }
}
```

## Railway Setup Instructions

### CRITICAL: Enable Railpack Builder

Railway does **NOT** automatically use Railpack - you must enable it manually:

1. **Go to Railway Dashboard**:
   - Navigate to your project
   - Select your frontend service
   - Click on **Settings**

2. **Change Builder**:
   - Find the "Builder" setting
   - Change from **"NIXPACKS"** to **"RAILPACK"**
   - Click **Save**

3. **Redeploy**:
   - Trigger a new deployment
   - Monitor build logs - should show **"Using Railpack"** instead of "Using Nixpacks"

### Service Configuration

#### For Root-Level Deployment
- Use root directory (entire repo)
- Railway will use `/railpack.json`
- Suitable for monorepo with frontend at root

#### For Frontend-Only Deployment
- Set root directory to `frontend/`
- Railway will use `frontend/railpack.json`
- Recommended for separate frontend service

## Key Benefits of This Configuration

### 1. Eliminates Corepack Hash Mismatch
The problem statement mentioned:
> "The corepack hash issue will disappear because railpack handles package manager versions differently than nixpacks - it doesn't use Nix's commit-based versioning that caused your hash mismatch."

**How this fix addresses it**:
- Railpack uses explicit version strings (`"yarn": "4.9.2"`) instead of Nix hash-based versioning
- `corepack enable` command ensures proper Yarn 4.9.2 activation
- `yarn install --immutable` prevents lockfile modifications that cause hash mismatches

### 2. Proper Node.js 22 Support
- Aligns with latest LTS Node.js version
- Better performance and security features
- Consistent with modern JavaScript tooling requirements

### 3. Explicit Yarn 4.9.2 Configuration
- Matches `package.json` packageManager specification exactly
- Prevents version drift between local development and deployment
- Leverages Yarn 4's improved performance and features

## Validation

Run the validation scripts to confirm configuration:

```bash
# Validate Railpack configuration
./scripts/railway-railpack-validation.sh

# Test Railpack configuration
./scripts/test-railpack-config.sh
```

**Expected Output**:
```
✅ No competing build configurations found - Railpack-only setup confirmed
✅ All JSON configuration files have valid syntax
✅ Configuration follows Railway/Railpack best practices
```

## Expected Deployment Behavior

After applying these changes and enabling Railpack in Railway:

### Build Logs Should Show:
```
Using Railpack
Installing Node.js 22
Installing Yarn 4.9.2
Running: corepack enable
Running: yarn install --immutable
Running: yarn build
```

### Instead of Previous Error:
```
Using Nixpacks v1.39.0
ERROR: Corepack hash mismatch
ERROR: No start command could be found
```

### Health Check
- Frontend will be accessible at Railway-provided URL
- Health check endpoint: `/health` (if configured)
- Start command: `yarn start` (serves built production files)

## Troubleshooting

### If "Using Nixpacks" Still Appears

1. **Verify Railpack is enabled in Railway UI**:
   - Dashboard → Service → Settings → Builder = "RAILPACK"
   
2. **Check for competing configurations**:
   - Ensure no `Dockerfile`, `railway.toml`, `nixpacks.toml`, or `Procfile` exists
   - These have higher precedence than railpack.json

3. **Clear Railway build cache**:
   - In Railway dashboard, trigger rebuild
   - Or redeploy from scratch

### If Yarn Install Fails

1. **Check lockfile integrity**:
   ```bash
   cd frontend
   yarn install --immutable --check-cache
   ```

2. **Regenerate lockfile if needed** (only in development):
   ```bash
   cd frontend
   rm yarn.lock
   corepack enable && corepack prepare yarn@4.9.2 --activate
   yarn install
   ```

### If Build Fails

1. **Verify Node 22 compatibility**:
   - Check all dependencies support Node 22
   - Update packages if necessary

2. **Check build output**:
   - Ensure `yarn build` works locally with Node 22
   - Verify dist/build folder is created

## References

- [Railpack Schema Documentation](https://schema.railpack.com)
- [Railway Railpack Beta Announcement](https://blog.railway.app/p/railpack)
- [Yarn 4 Documentation](https://yarnpkg.com)
- [Node.js 22 Release Notes](https://nodejs.org)

## Files Modified

- `/railpack.json` - Root configuration for Node.js 22 and Yarn 4.9.2
- `/frontend/railpack.json` - Updated Node version and added Yarn version

## Next Steps

1. ✅ Configuration files updated
2. ⏭️ **Enable Railpack in Railway service settings** (REQUIRED)
3. ⏭️ Redeploy the service
4. ⏭️ Monitor logs for "Using Railpack" confirmation
5. ⏭️ Verify service health at deployed URL
