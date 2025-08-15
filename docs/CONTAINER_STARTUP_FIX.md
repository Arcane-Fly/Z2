# Container Startup Fix - Issue #106

## Problem Resolved

**Issue**: Railway deployment was failing with "The executable `yarn` could not be found" during container startup, despite successful Docker builds.

**Root Cause**: The `railpack.json` configuration specified `"startCommand": "yarn preview"` for the frontend service, but the production Docker container uses nginx:alpine which doesn't contain Node.js or yarn.

## Solution Applied

### 1. Removed Conflicting StartCommand
- **Removed**: `"startCommand": "yarn preview"` from frontend service in railpack.json
- **Effect**: Allows Railway to use the Docker container's native CMD (nginx)

### 2. Explicit Docker Builder Configuration  
- **Added**: `railway.json` with `"builder": "DOCKERFILE"` to explicitly use Docker deployment
- **Effect**: Ensures Railway uses the Dockerfile instead of trying to detect build system

### 3. Fixed nginx Configuration
- **Fixed**: Removed undefined `${CORS_ORIGINS}` variable from nginx.conf.template
- **Effect**: nginx starts successfully without template variable errors

### 4. Cleaned Up Conflicting Files
- **Removed**: `frontend/Procfile` (not needed for Docker deployment)
- **Removed**: `Dockerfile.frontend.backup` and other legacy files
- **Removed**: `frontend/DOCKERFILE_REMOVED.md` and related documentation

## Technical Details

### Before (Broken)
```json
// railpack.json
{
  "services": {
    "frontend": {
      "deploy": {
        "startCommand": "yarn preview"  // ❌ Tries to run yarn in nginx container
      }
    }
  }
}
```

### After (Fixed)
```json
// railpack.json  
{
  "services": {
    "frontend": {
      "deploy": {
        // ✅ No startCommand - uses Dockerfile CMD
      }
    }
  }
}

// railway.json (new)
{
  "build": {
    "builder": "DOCKERFILE"  // ✅ Explicit Docker deployment
  }
}
```

### Dockerfile Verification
```dockerfile
# Production stage uses nginx (correct)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
CMD ["nginx", "-g", "daemon off;"]  # ✅ nginx, not yarn
```

## Validation Results

✅ **Docker Build**: Frontend builds successfully with proper nginx production stage  
✅ **Container Startup**: nginx starts correctly with no yarn dependency  
✅ **Health Check**: `/health` endpoint responds with 200 OK  
✅ **Configuration**: No conflicting files remain  
✅ **Validation Script**: All deployment checks pass  

## Prevention

The updated `scripts/validate-deployment.sh` now detects this type of configuration conflict:

```bash
✅ railway.json valid, using builder: DOCKERFILE
✅ Frontend deployment config clean (no yarn startCommand conflict)  
✅ Frontend Dockerfile properly configured for nginx
```

## Deployment Process

Railway will now:
1. Use Docker builder (railway.json specifies DOCKERFILE)
2. Build frontend using node:20-alpine (build stage)
3. Copy built files to nginx:alpine (production stage)  
4. Start nginx server (Dockerfile CMD)
5. ❌ **Never try to run yarn in production container**

This fix resolves the "executable mismatch" issue permanently.