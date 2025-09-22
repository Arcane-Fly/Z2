# Railway Railpack-Only Deployment Guide

## Overview

This guide documents the Railpack-only deployment configuration implemented in Z2 to ensure reliable Railway deployments following the official Railway/Railpack best practices.

## Railway Build Priority & Critical Rule

Railway checks build configurations in this priority order:
1. **Dockerfile** (if exists)
2. **railpack.json** (if exists) 
3. **railway.json/railway.toml**
4. **Nixpacks** (auto-detection fallback)

**⚠️ Critical Rule**: Choose ONE build system. For Railpack deployment, competing configurations MUST be removed:
```bash
# Remove competing configs to ensure Railpack is used
rm Dockerfile railway.toml nixpacks.toml Procfile
```

## Problem Solved

**Issue**: Build failures due to competing build configurations and Railway defaulting to Docker/Nixpacks instead of Railpack.

**Solution**: Implement Railpack-only configuration following Railway's official guidelines.

## Key Principles

### 1. Railpack-Only Configuration
✅ **Use**: Only `railpack.json` files for build configuration
❌ **Remove**: `Dockerfile`, `railway.toml`, `nixpacks.toml`, `Procfile`

### 2. Railway Requirements Compliance
✅ **Use**: `--host 0.0.0.0` and `--port $PORT` in start commands
❌ **Avoid**: Hardcoded ports or localhost binding

### 3. Health Check Implementation
✅ **Required**: Health endpoint that returns 200 status
✅ **Recommended**: `/api/health` or `/health` endpoint

## Implementation Details

### Configuration Files

#### Root railpack.json
- Removed explicit `export PATH="$HOME/.local/bin:$PATH"` from install commands
- Uses `pip install --user poetry || pip install poetry` for robust Poetry installation
- Start commands rely on standard PATH resolution

#### Backend Procfile
- Simplified from: `export PATH="$HOME/.local/bin:$PATH" && ...`
- Simplified to: `{ poetry run uvicorn ... || python -m uvicorn ...; }`

### Utility Scripts

#### scripts/find-executable.sh
Builder-agnostic executable finder that:
- Tries `command -v` first (works in most environments)
- Falls back to common installation paths
- Provides detailed error messages when executables are missing

#### scripts/diagnose-build-env.sh
Environment diagnostic tool that:
- Detects current builder type
- Lists available executables and their locations
- Identifies problematic path references
- Provides builder-specific recommendations

## Testing & Validation

### Pre-deployment Checks
```bash
# Run diagnostic
./scripts/diagnose-build-env.sh

# Test executable resolution
./scripts/find-executable.sh python3 true
./scripts/find-executable.sh poetry true
```

### Build Success Indicators
- ✅ No "undefined variable" errors in build logs
- ✅ All required executables found during build
- ✅ No explicit PATH exports in configuration files
- ✅ Build completes successfully across different builders

## Environment Compatibility Matrix

| Builder | Python | Poetry | Node | Package Manager | Notes |
|---------|--------|--------|------|-----------------|-------|
| Railpack | `python3` | `poetry` | `node` | `npm`/`yarn` | Auto-detected in PATH |
| Nixpacks | `python3` | `poetry` | `node` | `npm`/`yarn` | Standard system paths |
| Docker | `/usr/local/bin/python3` | `poetry` | `/usr/local/bin/node` | `npm` | Container paths |
| Local | System paths | User/system install | System paths | System install | Development environment |

## Migration Checklist

When updating build configurations:

- [ ] Remove any `$NIXPACKS_PATH` references
- [ ] Remove explicit `export PATH` statements where possible
- [ ] Use `--user` flag for pip installations when appropriate
- [ ] Test with multiple builders (Railpack, Nixpacks)
- [ ] Run diagnostic script to verify no problematic patterns
- [ ] Update documentation

## Troubleshooting

### Common Issues

1. **Poetry not found**: Usually resolved by `pip install --user poetry`
2. **Python not found**: Check if `python3` vs `python` is available
3. **Build timeout**: May need to increase timeout for dependency installation

### Debug Commands
```bash
# Check executable availability
which python3
which poetry
which node

# Test Poetry installation
pip install --user poetry
poetry --version

# Run full diagnostic
./scripts/diagnose-build-env.sh
```

## Best Practices

1. **Always test locally** before deploying
2. **Use fallback patterns** for executable detection
3. **Avoid hardcoded paths** in configuration files
4. **Document any builder-specific requirements**
5. **Use diagnostic tools** to verify build environment
6. **Keep configurations simple** and builder-agnostic

## Related Documentation

- [Railway Railpack Documentation](https://docs.railway.com/reference/railpack)
- [Nixpacks Documentation](https://nixpacks.com/docs)
- [Z2 Deployment Architecture](./DEPLOYMENT_ARCHITECTURE.md)
- [Railway Configuration Fix](./railway-configuration-fix.md)