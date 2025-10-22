# Railway Z2B Backend Configuration Guide

## Required Railway Dashboard Settings

To deploy the Z2B backend service successfully, you **MUST** configure the following settings in the Railway dashboard:

### 1. Service Settings Configuration

Navigate to your Z2B service in Railway and configure:

#### Root Directory
```
backend
```
**Critical**: This tells Railway to use the `backend` directory as the root for builds and deployments.

#### Start Command
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
**Critical**: This overrides any default start command detection and ensures uvicorn is used.

#### Health Check Path
```
/health
```

#### Health Check Timeout
```
300
```

### 2. How to Configure in Railway Dashboard

1. Go to Railway Dashboard: https://railway.app/project/359de66a-b9de-486c-8fb4-c56fda52344f
2. Select the **Z2B** service
3. Click on **Settings** tab
4. Under **Service** section:
   - Set **Root Directory**: `backend`
   - Set **Custom Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Deploy** section:
   - Set **Health Check Path**: `/health`
   - Set **Health Check Timeout**: `300`
6. Click **Save Changes**
7. Trigger a new deployment

### 3. Verification

After configuring and redeploying:

1. **Build Logs** should show:
   ```
   ✓ Python dependencies installed
   ✓ Poetry configuration complete
   ```

2. **Deploy Logs** should show:
   ```
   Starting Container
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

3. **Health Check** should succeed:
   ```
   [1/1] Healthcheck succeeded!
   ```

### 4. Common Issues

#### Issue: "yarn: command not found"
**Solution**: Root Directory is not set to `backend` in Railway dashboard. Update the setting.

#### Issue: Health check fails
**Solution**: Ensure the start command includes `--host 0.0.0.0 --port $PORT` and the service is listening on the Railway-provided PORT environment variable.

## Configuration Files

This directory includes multiple configuration files for Railway:

- `railway.toml` - Railway-specific configuration
- `nixpacks.toml` - Nixpacks build configuration
- `Procfile` - Process/start command definition
- `railpack.json` - Railpack build configuration

Railway will automatically detect these files when the **Root Directory** is set correctly.

## Environment Variables

Required environment variables should be set in Railway dashboard:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- Additional API keys as needed

## Support

If deployment still fails after following this guide:
1. Check Railway build logs for specific errors
2. Verify all environment variables are set
3. Contact Railway support with Service ID: `169631f2-0f90-466d-89b8-a67f240a18b5`
