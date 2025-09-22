# Builder-Agnostic Deployment Guide

## Overview

This guide documents the builder-agnostic patterns implemented in Z2 to ensure successful deployments across different build systems (Railpack, Nixpacks, Docker, etc.) without relying on builder-specific environment variables.

## Problem Solved

**Issue**: Build failures due to undefined `$NIXPACKS_PATH` environment variable and builder-specific path dependencies.

**Solution**: Implement builder-agnostic executable resolution and path handling.

## Key Principles

### 1. Standard PATH Resolution
✅ **Use**: `python`, `pip`, `node`, `npm`, `yarn`
❌ **Avoid**: `$NIXPACKS_PATH/bin/python`, explicit PATH exports

### 2. Fallback Installation Patterns
✅ **Use**: `pip install --user poetry || pip install poetry`
❌ **Avoid**: Hardcoded installation paths

### 3. Builder Detection (When Needed)
```bash
# Only when absolutely necessary
if [ -n "${NIXPACKS_PATH:-}" ]; then
    # Nixpacks-specific handling
elif [ -n "${RAILWAY_ENVIRONMENT:-}" ]; then
    # Railway-specific handling
else
    # Standard/Local handling
fi
```

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