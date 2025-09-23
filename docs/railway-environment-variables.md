# Railway Environment Variables Configuration

## Required Environment Variables

Set these environment variables in your Railway service dashboard before deployment:

### Security (Required)
```bash
JWT_SECRET_KEY=your-secure-jwt-secret-key-here
```

### Optional (with defaults)
```bash
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Database (Auto-configured by Railway)
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

## Frontend Environment Variables

### Production (Railway)
```bash
NODE_ENV=production
VITE_API_BASE_URL=https://${{services.backend.RAILWAY_PUBLIC_DOMAIN}}
VITE_WS_BASE_URL=wss://${{services.backend.RAILWAY_PUBLIC_DOMAIN}}
```

### Build optimization
```bash
YARN_CACHE_FOLDER=/tmp/.yarn-cache
COREPACK_ENABLE_STRICT=0
```

## Backend Environment Variables

### Runtime
```bash
PYTHON_VERSION=3.11
PORT=8000
PYTHONUNBUFFERED=1
```

### Application
```bash
APP_NAME="Z2 AI Workforce Platform"
APP_VERSION="0.1.0"
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1
```

## How to Set in Railway

1. **Via Railway CLI:**
```bash
railway variables set JWT_SECRET_KEY=your-secret-key
railway variables set NODE_ENV=production
```

2. **Via Railway Dashboard:**
   - Go to your service settings
   - Click "Variables" tab
   - Add key-value pairs

3. **Via railway.json:**
   - Variables are already configured in the Railway configuration files
   - Railway will automatically set these when you deploy

## Variable References

Railway supports variable references between services:
- `${{services.backend.RAILWAY_PUBLIC_DOMAIN}}` - Backend service URL
- `${{Postgres.DATABASE_URL}}` - PostgreSQL database connection string
- `${{Redis.REDIS_URL}}` - Redis connection string (if added)

## Security Notes

- Never commit actual secrets to git
- Use Railway's secure environment variable storage
- JWT_SECRET_KEY should be a cryptographically secure random string
- In production, ensure HTTPS is enforced for all API calls