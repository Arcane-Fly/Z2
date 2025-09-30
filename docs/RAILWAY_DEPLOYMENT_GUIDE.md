# Railway Deployment Guide for Z2 Platform

## 🚀 Configuration Status

The Z2 platform is now optimally configured for Railway deployment using **railpack.json only**. All competing build configurations have been removed to prevent conflicts.

## 📋 Build System Configuration

### ✅ Current Setup (Railpack Only)
- **Root**: `railpack.json` (monorepo entry point)
- **Frontend**: `frontend/railpack.json` (Node.js 22 + Yarn 4+)
- **Backend**: `backend/railpack.json` (Python 3.11 + uvicorn)

### ❌ Removed Configurations
All competing build files have been removed to ensure Railway uses railpack.json:
- Railway + Yarn 4.9.2+ + MCP/A2A deployment only
- Single railpack.json configuration per service
- No competing build system configurations

## 🔧 Railway Environment Variables

Set these environment variables in your Railway dashboard:

### Required Security Variables
```bash
# JWT Authentication (REQUIRED)
JWT_SECRET_KEY=your-secure-jwt-secret-key-here

# Database (Auto-provided by Railway PostgreSQL service)
DATABASE_URL=${Postgres.DATABASE_URL}
```

### Optional Configuration Variables
```bash
# JWT Token Expiration (Optional - has defaults)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Setup (Optional)
DEFAULT_ADMIN_PASSWORD=your-secure-admin-password

# API Configuration (Optional)
CORS_ORIGINS=https://your-domain.com
LOG_LEVEL=INFO
```

## 🏗️ Service Start Commands

### Frontend Service
```bash
yarn start
```
- Serves built React application from `dist/` directory
- Uses `serve` package for production static file serving
- Automatically detects Railway `$PORT` variable

### Backend Service  
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
- Starts FastAPI application with uvicorn ASGI server
- Binds to all interfaces (0.0.0.0) for Railway compatibility
- Uses Railway-provided `$PORT` environment variable

### Root Service (Monorepo)
```bash
python run_server.py
```
- Starts backend server from repository root
- Automatically changes to backend directory and imports FastAPI app
- Handles both development and production configurations

## 🏥 Health Check Endpoints

Railway will use these endpoints to verify service health:

### Backend Health Checks
- **Simple**: `GET /health` (recommended for Railway)
- **Detailed**: `GET /api/v1/health/detailed`
- **Liveness**: `GET /health/live`
- **Readiness**: `GET /health/ready`

### Frontend Health Check
- **Root**: `GET /` (serves React application)
- **Static Assets**: All built files available under `/assets/`

## 🔒 Security Best Practices

### ✅ Secure Configuration
1. **JWT secrets** read from Railway environment variables
2. **No hardcoded secrets** in configuration files
3. **Database URL** provided by Railway PostgreSQL service
4. **CORS origins** configurable via environment variables

### ✅ Environment Variable Usage
```python
# Backend security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-for-development")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```

## 🧪 Validation Commands

Run these commands to verify your deployment configuration:

### Test Railpack Configuration
```bash
bash scripts/test-railpack-config.sh
```

### Validate JSON Syntax
```bash
python -m json.tool railpack.json
python -m json.tool frontend/railpack.json  
python -m json.tool backend/railpack.json
```

### Check Railway + Yarn 4.9.2+ Configuration
```bash
# Verify railpack.json files are valid
python -m json.tool railpack.json
python -m json.tool frontend/railpack.json  
python -m json.tool backend/railpack.json
```

## 🚨 Troubleshooting

### If Railway Configuration Issues

1. **Check Railway Dashboard**: Ensure explicit build/start commands are set in service settings
2. **Clear Build Cache**: Force a clean rebuild in Railway dashboard  
3. **Verify Configuration**: Ensure `railpack.json` files exist and are valid JSON

### If Start Commands Fail

1. **Backend**: Verify `uvicorn` is installed and `app.main:app` exists
2. **Frontend**: Verify `yarn build` succeeded and `dist/` directory exists
3. **Environment**: Check that `$PORT` variable is available

### If Health Checks Fail

1. **Backend**: Test `curl http://localhost:8000/health` locally
2. **Frontend**: Verify static files are served correctly
3. **Database**: Ensure PostgreSQL service is linked in Railway

## 📈 Expected Deployment Flow

1. **Railway detects** `railpack.json` configurations
2. **Uses explicit build/start commands** from service settings
3. **Installs dependencies** using Yarn 4.9.2+ and Poetry
4. **Executes start commands** with proper port binding (0.0.0.0:$PORT)
5. **Monitors health** using configured endpoints (/health)
6. **✅ Deployment succeeds** with Railway + Yarn 4.9.2+ + MCP/A2A stack

---

**Status**: ✅ **READY FOR DEPLOYMENT**

The Z2 platform is now optimally configured for Railway with clean railpack-only setup, secure environment variable handling, and proper health monitoring.