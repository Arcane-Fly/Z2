# Railway Backend Configuration Validator

## Purpose

This script validates that the Z2 backend is properly configured for Railway deployment using Railpack.

## Usage

```bash
./scripts/validate-railway-backend.sh
```

## What It Checks

1. ✓ `backend/railpack.json` exists
2. ✓ `railpack.json` has valid JSON syntax
3. ✓ Provider is set to "python"
4. ✓ Start command uses `uvicorn`
5. ✓ Start command uses `$PORT` variable
6. ✓ Start command binds to `0.0.0.0`
7. ✓ Health check path is set to `/health`
8. ✓ No competing configuration files (Dockerfile, railway.toml, etc.)
9. ✓ Health check endpoint is implemented in code
10. ✓ `pyproject.toml` exists

## Exit Codes

- `0`: All checks passed
- `1`: One or more checks failed

## Important Note

This script validates the **code configuration** only. The Railway service itself must also be properly configured:

- **Root Directory**: `backend`
- **Builder**: Railpack (auto-detect)

See `docs/RAILWAY_BACKEND_FIX.md` for complete Railway service configuration instructions.

## Example Output

```
================================
Railway Backend Validator
================================

1. Checking backend/railpack.json exists...
✓ backend/railpack.json found

2. Validating backend/railpack.json syntax...
✓ Valid JSON syntax

3. Checking railpack.json provider...
✓ Provider is 'python'

...

================================
Validation Summary
================================
✓ All checks passed!

Backend code configuration is correct.

IMPORTANT: The Railway service itself must be configured with:
  - Root Directory: backend
  - Builder: Railpack (auto-detect)

See docs/RAILWAY_BACKEND_FIX.md for instructions.
```

## Related Documentation

- [RAILWAY_BACKEND_FIX.md](../docs/RAILWAY_BACKEND_FIX.md) - Complete fix instructions
- [RAILWAY_SERVICE_STATUS.md](../RAILWAY_SERVICE_STATUS.md) - Current status
- [RAILWAY_DEPLOYMENT_GUIDE.md](../docs/RAILWAY_DEPLOYMENT_GUIDE.md) - General deployment guide
