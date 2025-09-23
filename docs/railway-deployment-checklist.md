# Railway Deployment Checklist

## Pre-Deployment Verification

### ✅ Configuration Files Created
- [x] `frontend/railway.json` - Explicit Railway configuration for frontend
- [x] `backend/railway.json` - Explicit Railway configuration for backend  
- [x] `frontend/nixpacks.toml` - Nixpacks fallback for frontend
- [x] `backend/nixpacks.toml` - Nixpacks fallback for backend
- [x] `frontend/Procfile` - Simple start command for frontend
- [x] `backend/Procfile` - Simple start command for backend
- [x] `docs/railway-environment-variables.md` - Environment variable documentation

### ✅ Validation Scripts
- [x] `scripts/validate-railway-deployment.sh` - Validates all Railway configurations
- [x] `scripts/test-railway-build.sh` - Simulates Railway build process
- [x] `scripts/validate_railway_fixes.py` - Validates existing fixes (already present)

### ✅ Configuration Hierarchy
Railway will automatically detect and use configurations in this order:
1. **Railpack** (primary) - Existing `railpack.json` files
2. **Railway.json** (explicit) - New Railway-specific configurations  
3. **Nixpacks.toml** (advanced) - Fallback for complex build requirements
4. **Procfile** (simple) - Basic start command definition

## Deployment Steps

### 1. Environment Variables Setup
Set these in Railway dashboard before deployment:

#### Required (Security)
```bash
JWT_SECRET_KEY=<generate-secure-random-string>
```

#### Automatic (Railway provides)
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
PORT=${{PORT}}
RAILWAY_ENVIRONMENT=${{RAILWAY_ENVIRONMENT}}
```

#### Optional (Pre-configured defaults)
```bash
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
NODE_ENV=production
PYTHON_VERSION=3.11
```

### 2. Service Creation in Railway

#### Backend Service
1. Create new service in Railway
2. Connect to GitHub repository
3. Set root directory to `backend/`
4. Railway will auto-detect configurations
5. Set environment variables
6. Deploy

#### Frontend Service  
1. Create new service in Railway
2. Connect to GitHub repository
3. Set root directory to `frontend/`
4. Railway will auto-detect configurations
5. Set environment variables
6. Deploy

### 3. Post-Deployment Verification

#### Health Checks
- Backend: `https://<backend-url>/health`
- Backend (detailed): `https://<backend-url>/health/ready`
- Frontend: Service should respond on root URL

#### Logs Monitoring
- Check Railway deployment logs for "Using Railpack" or "Using Nixpacks"
- Verify successful dependency installation
- Confirm service startup without errors

#### API Integration
- Verify frontend can communicate with backend
- Test API endpoints functionality
- Confirm WebSocket connections (if used)

## Troubleshooting Guide

### Frontend Issues

#### Yarn Hash Mismatch (Resolved)
✅ **Solution Applied**: Yarn 4.9.2 consistency + checksumBehavior: update

#### Build Failures
- Check yarn.lock is committed
- Verify .yarnrc.yml configuration
- Ensure NODE_ENV=production is set

### Backend Issues

#### Start Command Not Found (Resolved)
✅ **Solution Applied**: Multiple fallback configurations

#### Dependency Installation Failures
- Verify poetry.lock is committed
- Check Python version compatibility (3.11-3.12)
- Ensure poetry.toml configuration is correct

### General Railway Issues

#### Service Detection Problems
- Multiple configuration files provide fallbacks
- Railway.json explicitly specifies NIXPACKS builder
- Procfile ensures start command is always available

#### Environment Variable Issues
- Use Railway's variable reference syntax: `${{SERVICE.VARIABLE}}`
- Verify JWT_SECRET_KEY is set and secure
- Check DATABASE_URL is properly referenced

## Success Indicators

### ✅ Deployment Successful When:
- [ ] Frontend service starts and serves on assigned port
- [ ] Backend service starts and responds to health checks
- [ ] Database connection established successfully
- [ ] No critical errors in deployment logs
- [ ] Services can communicate with each other
- [ ] API endpoints return expected responses

### ✅ Build Successful When:
- [ ] Dependencies install without conflicts
- [ ] Build process completes without errors
- [ ] Start commands execute successfully
- [ ] Health endpoints respond correctly
- [ ] No security vulnerabilities reported

## Rollback Plan

If deployment fails:
1. Check Railway deployment logs for specific errors
2. Verify environment variables are correctly set
3. Use Railway's rollback feature to previous working deployment
4. Test configurations locally using validation scripts
5. Fix issues and redeploy

## Support Resources

- Railway Documentation: https://docs.railway.app
- Repository Issues: https://github.com/Arcane-Fly/Z2/issues
- Configuration Validation: Run `./scripts/validate-railway-deployment.sh`
- Build Testing: Run `./scripts/test-railway-build.sh`