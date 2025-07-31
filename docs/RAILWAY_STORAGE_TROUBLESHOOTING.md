# Railway Volume Mount Path Troubleshooting Guide

This guide helps resolve Railway volume mount issues for the Z2 AI Workforce Platform backend.

## Current Configuration Analysis

The Z2 backend is properly configured for Railway deployment with the following storage setup:

### ✅ Current Storage Configuration
- **Storage Path**: `/app/storage`
- **Volume Mount**: `/app/storage` 
- **Docker WORKDIR**: `/app`
- **Permissions**: Correctly set for `appuser`

### Configuration Files
1. **railpack.json** - Lines 40-48 configure volume mount
2. **Dockerfile.backend** - Line 34 creates storage directory
3. **app/core/config.py** - Line 133 sets default storage path

## Common Railway Volume Mount Issues & Solutions

### 1. Volume Mount Path Alternatives to Try

If `/app/storage` is not working, try these alternatives in Railway dashboard:

| Mount Path | Use Case | Configuration |
|------------|----------|---------------|
| `/data` | Simple absolute path | Simplest option |
| `/opt/app/storage` | Common Docker pattern | Alternative Docker setup |
| `/workspace/storage` | Railway working directory | Railway's default workdir |
| `/storage` | Root-level storage | Direct mount |

### 2. Railway Service Configuration

Update your Railway service volume configuration:

1. Go to your service in Railway dashboard
2. Navigate to **Settings** → **Volumes**
3. Update the mount path to one of the alternatives above
4. Redeploy the service

### 3. Environment Variable Override

You can override the storage path via environment variable in Railway:

```bash
STORAGE_PATH=/data
# or
STORAGE_PATH=/workspace/storage
# or  
STORAGE_PATH=/opt/app/storage
```

### 4. Docker Configuration Alternatives

If the current Docker setup isn't working, try these Dockerfile modifications:

#### Option A: Simple Data Directory
```dockerfile
# Create data directory instead of app/storage
RUN mkdir -p /data && chown -R appuser:appuser /data
ENV STORAGE_PATH=/data
```

#### Option B: Workspace Directory
```dockerfile
# Use Railway's workspace directory
RUN mkdir -p /workspace/storage && chown -R appuser:appuser /workspace/storage
ENV STORAGE_PATH=/workspace/storage
```

### 5. Debugging Steps

Use the built-in storage debugging endpoint to test your configuration:

```bash
# Test storage configuration
curl https://your-railway-app.railway.app/api/v1/debug/storage

# Check health status
curl https://your-railway-app.railway.app/health
```

## Quick Fix Checklist

Try these solutions in order:

- [ ] **Option 1**: Change Railway volume mount to `/data`
- [ ] **Option 2**: Set environment variable `STORAGE_PATH=/data`
- [ ] **Option 3**: Change Railway volume mount to `/workspace/storage`  
- [ ] **Option 4**: Set environment variable `STORAGE_PATH=/workspace/storage`
- [ ] **Option 5**: Change Railway volume mount to `/opt/app/storage`
- [ ] **Option 6**: Use the root storage path `/storage`

## Verification Steps

After making changes:

1. **Check Railway Logs**: Look for storage-related errors
2. **Test Storage Endpoint**: Use the debug endpoint to verify storage
3. **Monitor Health Check**: Ensure `/health` returns healthy status
4. **Test File Operations**: Verify file upload/download works

## Advanced Debugging

### Check Current Storage Configuration
Access your Railway service logs and look for:

```
Storage path: /app/storage
Storage type: local
Max file size: 10MB
Path exists: False  # ← This indicates the issue
```

### Test Storage Access
Use Railway's console access to test directory creation:

```bash
# Check if storage directory exists
ls -la /app/storage

# Check permissions
stat /app/storage

# Test write access
touch /app/storage/test.txt
```

## Railway-Specific Considerations

### Volume Persistence
- Railway volumes persist data across deployments
- Ensure volume name matches between services if shared
- Check Railway dashboard for volume status

### Resource Limits
- Verify your Railway plan supports volumes
- Check volume size limits for your plan
- Monitor storage usage in Railway dashboard

### Deployment Context
- Railway may use different base paths than Docker
- Working directory might differ from Docker WORKDIR
- Environment variables override Docker ENV settings

## Still Having Issues?

If none of the above solutions work:

1. **Check Railway Status**: Visit Railway status page for known issues
2. **Review Service Logs**: Look for detailed error messages in Railway logs
3. **Test Locally**: Run the Docker container locally to verify configuration
4. **Contact Support**: Use Railway's support channels with your service ID

## Best Practices for Future Deployments

1. **Use Absolute Paths**: Always use absolute paths for volume mounts
2. **Test Configurations**: Verify storage setup in staging before production
3. **Monitor Storage**: Set up alerts for storage issues
4. **Document Changes**: Keep track of working configurations
5. **Use Health Checks**: Implement storage verification in health endpoints

---

## Additional Resources

- [Railway Volume Documentation](https://docs.railway.app/deploy/volumes)
- [Docker Storage Best Practices](https://docs.docker.com/storage/)
- [Z2 Backend Configuration Guide](./DEPLOYMENT.md)