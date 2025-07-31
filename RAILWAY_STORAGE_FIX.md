# Railway Storage Configuration Quick Setup Guide

Based on the analysis of your Z2 backend repository, here are the **exact steps** to fix your Railway volume mount path issue:

## 🔍 Issue Identified

Your current configuration uses `/app/storage` but this path is not accessible in your Railway environment. Our diagnostic found that `/opt/app/storage` is the optimal working path.

## 🚀 Quick Fix Steps

### 1. Update Railway Volume Configuration

In your Railway dashboard:

1. Go to your **backend service** settings
2. Navigate to **Variables** section
3. Add/update this environment variable:
   ```
   STORAGE_PATH=/opt/app/storage
   ```

4. Navigate to **Volumes** section  
5. Update your volume mount path to:
   ```
   Mount Path: /opt/app/storage
   ```

### 2. Redeploy Your Service

After making the changes above:
1. Click **Deploy** in Railway dashboard
2. Wait for deployment to complete

### 3. Verify the Fix

Once deployed, test these endpoints:

```bash
# Check storage configuration
curl https://your-app.railway.app/api/v1/debug/storage

# Test storage operations  
curl -X POST https://your-app.railway.app/api/v1/debug/test-storage

# Check overall health
curl https://your-app.railway.app/health
```

## 🔧 Alternative Solutions

If `/opt/app/storage` doesn't work, try these alternatives **in order**:

### Option 2: Use `/data` mount path
```bash
# Railway Volume Mount Path: /data
# Environment Variable: STORAGE_PATH=/data
```

### Option 3: Use `/tmp/storage` (temporary fallback)
```bash
# Railway Volume Mount Path: /tmp/storage  
# Environment Variable: STORAGE_PATH=/tmp/storage
```

### Option 4: Use root `/storage`
```bash
# Railway Volume Mount Path: /storage
# Environment Variable: STORAGE_PATH=/storage
```

## 📊 Current Configuration Status

✅ **Working Paths Found**: `/opt/app/storage`, `/tmp/storage`  
❌ **Current Path**: `/app/storage` (not accessible)  
🎯 **Recommended**: Use `/opt/app/storage` as volume mount path

## 🔍 Debug Tools Available

Your Z2 backend now includes built-in diagnostic tools:

```bash
# Run storage diagnostic script
python backend/scripts/storage_diagnostic.py

# API endpoints for debugging
GET /api/v1/debug/storage          # Storage configuration analysis
GET /api/v1/debug/environment      # Environment variables
POST /api/v1/debug/test-storage    # Test storage operations
```

## 📝 Configuration Files Updated

The following files have been enhanced with Railway compatibility:

- `backend/app/api/v1/endpoints/debug.py` - New debug endpoints
- `backend/app/core/storage_config.py` - Enhanced storage configuration  
- `backend/scripts/storage_diagnostic.py` - Diagnostic script
- `docs/RAILWAY_STORAGE_TROUBLESHOOTING.md` - Comprehensive guide
- `railpack.json` - Updated with alternative path documentation

## ✨ What's New

1. **Automatic Path Detection**: Backend now auto-detects working storage paths
2. **Debug Endpoints**: Real-time storage diagnostics via API
3. **Diagnostic Script**: Standalone script for troubleshooting
4. **Comprehensive Documentation**: Step-by-step troubleshooting guide

## 🆘 Still Having Issues?

If the above solutions don't work:

1. Check Railway logs for specific error messages
2. Use the diagnostic script: `python backend/scripts/storage_diagnostic.py`
3. Test the debug endpoints to see real-time status
4. Review the full troubleshooting guide: `docs/RAILWAY_STORAGE_TROUBLESHOOTING.md`

---

**Expected Result**: After following step 1-3, your storage should work correctly and file operations should succeed. The debug endpoints will show "✅ Current configuration is working correctly".