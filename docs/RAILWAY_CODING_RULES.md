# Railway Deployment Master Cheat Sheet - Coding Assistant Rules

This document provides the comprehensive rules and standards that must be enforced for all Railway deployments in the Z2 platform, based on the Railway Deployment Master Cheat Sheet.

## 🔴 CRITICAL DEPLOYMENT STANDARDS

### 1. Railway Build System (MUST ENFORCE)

**✅ ALWAYS use railpack.json** as the primary build configuration
- Remove ALL competing build files when using railpack.json
- Railway Build Priority: Dockerfile > railpack.json > railway.json/toml > Nixpacks
- **Competing files to REMOVE**: `Dockerfile`, `railway.toml`, `nixpacks.toml`, `Procfile`

**✅ Correct railpack.json Template:**
```json
{
  "version": "1",
  "metadata": {
    "name": "service-name"
  },
  "build": {
    "provider": "node",  // or "python" 
    "steps": {
      "install": {
        "commands": ["yarn install --frozen-lockfile"]
      },
      "build": {
        "commands": ["yarn build"]
      }
    }
  },
  "deploy": {
    "startCommand": "yarn start",
    "healthCheckPath": "/api/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### 2. PORT Binding (CRITICAL)

**✅ NEVER hardcode ports** - always use `process.env.PORT` or `os.getenv("PORT")`
**✅ ALWAYS bind to 0.0.0.0** not localhost or 127.0.0.1

#### Node.js/TypeScript:
```javascript
// ✅ CORRECT
const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';
app.listen(PORT, HOST, () => {
  console.log(`Server running on ${HOST}:${PORT}`);
});

// ❌ WRONG
app.listen(3000);  // Hardcoded port
app.listen(PORT, 'localhost');  // Wrong host
```

#### Python:
```python
# ✅ CORRECT
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

# ❌ WRONG  
app.run(host="127.0.0.1", port=5000)  # Wrong host and hardcoded port
```

### 3. Health Check Implementation (REQUIRED)

**✅ Include health check endpoint** at `/api/health` returning 200 status
**✅ Configure in railpack.json:**
```json
{
  "deploy": {
    "healthCheckPath": "/api/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

#### Express.js Health Endpoint:
```javascript
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});
```

#### Python Flask/FastAPI Health Endpoint:
```python
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

### 4. Railway Reference Variables (CORRECT SYNTAX)

**✅ Reference domains not ports** in Railway variables
**✅ Use RAILWAY_PUBLIC_DOMAIN for external access:**
```bash
BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
INTERNAL_API=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}
```

**❌ WRONG - Cannot reference PORT:**
```bash
BACKEND_URL=${{backend.PORT}}  # This doesn't work
```

### 5. Theme/CSS Loading (Frontend)

**✅ Apply theme BEFORE React renders** to prevent flash of unstyled content
```javascript
// src/main.tsx - BEFORE React renders
document.documentElement.className = localStorage.getItem('theme') || 'dark';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
```

**✅ Proper CSS Import Order in src/index.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

.dark {
  color-scheme: dark;
}

/* Custom styles AFTER Tailwind */
```

### 6. Vite Configuration for Railway

```javascript
// vite.config.ts
export default defineConfig({
  base: './',  // Relative paths for Railway
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    cssCodeSplit: false  // Ensure CSS is bundled
  }
});
```

## 🔍 VALIDATION REQUIREMENTS

### Pre-Deployment Validation Checklist

Before any Railway deployment, run this validation:

```bash
# 1. Check for conflicting build configs
ls -la | grep -E "(Dockerfile|railway\.toml|nixpacks\.toml|Procfile)"

# 2. Validate railpack.json syntax
cat railpack.json | jq '.' > /dev/null && echo "✅ Valid JSON"

# 3. Verify PORT usage in code
grep -r "process.env.PORT\|PORT.*os.getenv" . | grep -v node_modules

# 4. Check host binding
grep -r "0\.0\.0\.0\|localhost\|127\.0\.0\.1" . | grep -E "(listen|HOST|host)"

# 5. Verify health endpoint exists
grep -r "/health\|/api/health" . | grep -v node_modules

# 6. Test build locally (if applicable)
yarn build && PORT=3000 yarn start
```

### Git Hook for Automatic Validation

The repository includes a pre-push hook that validates:
- JSON syntax in railpack.json files
- Absence of competing build configurations
- This runs automatically before pushing to Railway

## 🚀 DEPLOYMENT COMMANDS

### Quick Fix Commands

```bash
# Force Railpack rebuild
railway up --force

# Clear Railway build cache
railway run --service <service-name> railway cache:clear

# Debug environment variables
railway run env | grep -E "(PORT|HOST|RAILWAY)"

# Test health endpoint
railway run curl http://localhost:$PORT/api/health
```

## 📋 ENFORCEMENT CHECKLIST

When reviewing or creating Railway deployments, verify:

- [ ] Only railpack.json exists (no Dockerfile, railway.toml, nixpacks.toml, Procfile)
- [ ] All services bind to `0.0.0.0` host and use `process.env.PORT`
- [ ] Health check endpoints return 200 status and are configured in railpack.json
- [ ] Railway reference variables use `RAILWAY_PUBLIC_DOMAIN` not `PORT`
- [ ] Frontend themes are applied before React renders
- [ ] CSS is properly ordered (Tailwind base/components/utilities first)
- [ ] Git pre-push hook validates configuration before deployment
- [ ] Local testing confirms PORT and HOST environment variables work correctly

## 🔧 TROUBLESHOOTING

### Common Railway Deployment Errors

**Error: "No start command could be found"**
- **Fix**: Ensure only railpack.json exists, remove competing build files

**Error: "Application failed to respond"**
- **Fix**: Check host binding is `0.0.0.0` not `localhost`, verify PORT usage

**Error: "Health check failed"**
- **Fix**: Ensure health endpoint returns 200 status, check railpack.json health config

**Error: "Build system conflicts"**
- **Fix**: Remove all Dockerfile, railway.toml, nixpacks.toml, Procfile files

**Error: "Reference variable does not resolve"**
- **Fix**: Use `${{service.RAILWAY_PUBLIC_DOMAIN}}` not `${{service.PORT}}`

---

*This document enforces the Railway Deployment Master Cheat Sheet standards to prevent recurring deployment issues. All Z2 platform Railway deployments MUST follow these rules.*