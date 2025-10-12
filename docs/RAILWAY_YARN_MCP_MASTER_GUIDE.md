# Railway + Yarn 4.9.2+ + MCP/A2A Master Implementation Guide

## Overview

This document describes Z2's implementation of the Railway + Yarn 4.9.2+ + MCP/A2A Master Cheat Sheet standards. It ensures consistent, production-ready deployments following best practices for:

- **Railway**: Railpack-based deployments with proper build configuration
- **Yarn 4.9.2+**: Modern package management with workspaces and constraints
- **MCP/A2A**: Integration patterns for Model Context Protocol and Agent-to-Agent communication

## Core Principles

### 1. Single Build System Rule

**Critical**: Railway honors build configs in this priority order:
```
Dockerfile > railpack.json > railway.json/toml > Nixpacks
```

Z2 uses **railpack.json exclusively**. All competing configurations (Dockerfile, railway.toml, nixpacks.toml, Procfile) are removed to prevent build plan conflicts.

### 2. Railpack Configuration Structure

All railpack.json files follow the standard structure per the master cheat sheet:

```json
{
  "version": "1",
  "metadata": { "name": "service-name" },
  "build": {
    "provider": "node|python",
    "steps": {
      "install": { "commands": ["..."] },
      "build": { "commands": ["..."] }
    }
  },
  "deploy": {
    "startCommand": "...",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### 3. Port Binding & Health Checks

**Requirements**:
- Listen on `process.env.PORT` (never hardcode ports)
- Bind to `0.0.0.0` (never `localhost`)
- Implement health endpoints returning 200 status
- Configure health checks in railpack.json

**Backend Example** (Python/FastAPI):
```python
from app.core.config import settings

# In app/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Server start (via uvicorn)
# uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Frontend Example** (Node/Express):
```javascript
const PORT = process.env.PORT || 4173;
const HOST = '0.0.0.0';

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

app.listen(PORT, HOST, () => {
  console.log(`Server running on ${HOST}:${PORT}`);
});
```

## Z2 Implementation Details

### Workspace Structure

Z2 is configured as a Yarn 4.9.2+ monorepo:

```
Z2/
├── package.json           # Root workspace configuration
├── railpack.json          # Root railpack config
├── constraints.pro        # Yarn workspace constraints
├── .yarnrc.yml           # Yarn configuration
├── backend/
│   ├── railpack.json     # Backend-specific railpack
│   └── pyproject.toml    # Python dependencies (Poetry)
└── frontend/
    ├── railpack.json     # Frontend-specific railpack
    └── package.json      # Frontend dependencies
```

### Railpack Configurations

#### Root (railpack.json)
- Provider: Node (for workspace-level operations)
- Uses Yarn 4.9.2 with `--frozen-lockfile`
- Health check: `/api/health`
- Restart policy: ON_FAILURE (3 retries)

#### Backend (backend/railpack.json)
- Provider: Python
- Poetry 1.8.5 for dependency management
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health`
- Restart policy: ON_FAILURE (3 retries)

#### Frontend (frontend/railpack.json)
- Provider: Node
- Yarn 4.9.2 with `--frozen-lockfile`
- Start command: `yarn start` (runs Express server)
- Health check: `/health`
- Restart policy: ON_FAILURE (3 retries)

### Yarn Configuration

**Package Manager**: Yarn 4.9.2 (enforced via Corepack)

**Installation**:
```bash
corepack enable
corepack prepare yarn@4.9.2 --activate
yarn install --frozen-lockfile
```

**Key Settings** (.yarnrc.yml):
```yaml
enableGlobalCache: true          # Use global cache
nmMode: hardlinks-local          # Use hardlinks for faster installs
nodeLinker: node-modules         # Use node_modules (not PnP)
enableImmutableInstalls: false   # Allow updates in development
```

**Constraints** (constraints.pro):
- Enforces Node.js 20+ across all workspaces
- Enforces Yarn 4.9.2+ across all workspaces
- Ensures `workspace:*` protocol for internal dependencies
- Maintains consistent dependency versions
- Enforces MIT license for public packages

**Commands**:
```bash
# Check workspace constraints
yarn constraints

# Auto-fix constraint violations
yarn constraints --fix

# List all workspaces
yarn workspaces list

# Build all workspaces
yarn workspaces foreach -At run build

# Security audit
yarn npm audit --all
```

### Vite Configuration (Frontend)

Railway-optimized settings in `vite.config.ts`:

```typescript
export default defineConfig({
  base: './',                    // Relative base for deployment
  build: {
    cssCodeSplit: false,         // Bundle CSS predictably (Railway optimization)
    outDir: 'dist'
  },
  server: {
    host: '0.0.0.0',            // Bind to all interfaces
    port: Number(process.env.PORT) || 5173
  },
  preview: {
    host: '0.0.0.0',            // Bind to all interfaces
    port: Number(process.env.PORT) || 4173
  }
})
```

## Service Communication

### Internal Service URLs
```bash
# Backend to Frontend (internal)
http://${{frontend.RAILWAY_PRIVATE_DOMAIN}}

# Frontend to Backend (internal)
http://${{backend.RAILWAY_PRIVATE_DOMAIN}}
```

### Public Service URLs
```bash
# Public backend URL
https://${{backend.RAILWAY_PUBLIC_DOMAIN}}

# Public frontend URL
https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
```

**Important**: Don't reference another service's `PORT` directly. Use Railway domain variables.

## MCP/A2A Integration

### TypeScript (Yarn)

Install MCP SDK:
```bash
yarn add @modelcontextprotocol/sdk
```

Install A2A Protocol:
```bash
yarn add a2a-protocol
```

**Never use npm/npx** - always use Yarn:
- ✅ `yarn add package-name`
- ✅ `yarn dlx command`
- ❌ `npm install package-name`
- ❌ `npx command`

### Python (pip)

Install MCP:
```bash
pip install mcp
```

Install A2A:
```bash
pip install python-a2a
```

## Deployment Checklist

Before deploying to Railway, verify:

- [ ] Only railpack.json files exist (no Dockerfile, railway.toml, etc.)
- [ ] All railpack.json files are valid JSON (`jq '.' railpack.json`)
- [ ] All services use `process.env.PORT` or `$PORT`
- [ ] All services bind to `0.0.0.0` (not localhost)
- [ ] Health endpoints return 200 status
- [ ] Health check paths configured in railpack.json
- [ ] CORS origins use Railway domain variables (not localhost)
- [ ] WebSocket connections use `wss://` on HTTPS pages
- [ ] Yarn constraints pass: `yarn constraints`
- [ ] Security audit clean: `yarn npm audit --all`

## Validation Scripts

Z2 includes several validation scripts:

```bash
# Comprehensive Railpack validation
bash scripts/railway-railpack-validation.sh

# Railway deployment validation
bash scripts/railway-deployment-validation.sh

# Config validation (Python)
python3 scripts/validate_config.py

# Yarn constraints check
yarn constraints
```

## Troubleshooting

### "Application failed to respond"
- Verify binding to `0.0.0.0` (not localhost)
- Check `PORT` environment variable usage
- Ensure health endpoint is accessible
- Review Railway logs for startup errors

### "Unable to generate build plan"
- Remove competing build configurations (Dockerfile, etc.)
- Ensure only railpack.json exists
- Validate JSON syntax: `jq '.' railpack.json`

### Build failures
- Check Railway build logs
- Verify all dependencies are specified
- For Yarn: ensure `--frozen-lockfile` is used
- For Python: verify Poetry version (1.8.5)

### Health check timeouts
- Increase `healthCheckTimeout` in railpack.json
- Verify health endpoint responds within 5 minutes
- Check if service needs more startup time

## References

- [Railway Documentation](https://docs.railway.app/)
- [Railpack Schema](https://schema.railpack.com)
- [Yarn 4 Documentation](https://yarnpkg.com/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [A2A Protocol](https://a2a-protocol.org/)

## Consistency Matrix

| Area | Use | Don't Use |
|------|-----|-----------|
| Package manager (JS/TS) | Yarn 4.9.2+ via Corepack; `yarn dlx` | `npm`, `npx` |
| Internal deps | `workspace:*` | version literals |
| A2A TS install | `yarn add a2a-protocol` | `npm install a2a-protocol` |
| MCP TS install | `yarn add @modelcontextprotocol/sdk` | `npm install @modelcontextprotocol/sdk` |
| Python deps | `pip install ...` | (n/a) |
| Railway config | **railpack.json** (singular) | multiple competing configs |
| Ports/Bind | `process.env.PORT` + `0.0.0.0` | hardcoded port / `localhost` |
| Service URLs | Railway domains (public/private) | raw ports / IPs |
| Health checks | `/api/health` + deploy config | none |

## Local Development

### Setup
```bash
# Enable Corepack and Yarn
corepack enable
corepack prepare yarn@4.9.2 --activate

# Install dependencies
yarn install

# Check constraints
yarn constraints --fix
```

### Running Services

**Backend**:
```bash
cd backend
poetry install
PORT=8000 poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend**:
```bash
cd frontend
yarn dev  # Development mode with Vite
# OR
yarn build && PORT=4173 yarn start  # Production mode with Express
```

### Testing Health Endpoints

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:4173/health
curl http://localhost:4173/api/health
```

## Production Deployment

Railway automatically deploys from the main branch when:
1. Code is pushed to GitHub
2. Railpack configurations are valid
3. Build succeeds
4. Health checks pass

Monitor deployments via:
- Railway Dashboard
- Railway CLI: `railway logs`
- Health endpoints: `curl https://your-domain.railway.app/health`

## Updates and Maintenance

### Updating Dependencies

**Yarn workspaces**:
```bash
yarn upgrade-interactive
yarn constraints --fix
yarn npm audit --all
```

**Python (Poetry)**:
```bash
cd backend
poetry update
poetry lock
```

### Version Bumps

When updating Node.js, Python, or Yarn versions:
1. Update railpack.json `packages` section
2. Update package.json `engines` section
3. Update constraints.pro if needed
4. Test locally before deploying
5. Update this documentation

---

**Last Updated**: 2025-10-12  
**Master Cheat Sheet Version**: 1.0  
**Z2 Implementation Status**: ✅ Compliant
