# CORS Configuration Fix

## Overview
Fixed Railway deployment failure caused by CORS_ORIGINS environment variable parsing error in Pydantic Settings v2.

## Problem
The Z2 FastAPI backend was failing to start on Railway with the error:
```
pydantic_settings.exceptions.SettingsError: error parsing value for field "cors_origins" from source "EnvSettingsSource"
```

This occurred because:
- Railway environment variables are often set as comma-separated strings
- Pydantic Settings v2 expects JSON format for `List[str]` fields by default
- The original configuration lacked a field validator to handle multiple input formats

## Solution
Added a robust field validator to `app/core/config.py` that handles multiple CORS origins input formats:

### Supported Formats:
1. **JSON Array** (Railway default): `["https://frontend.com","http://localhost:3000"]`
2. **Comma-separated**: `https://frontend.com,http://localhost:3000`
3. **Comma with spaces**: `https://frontend.com, http://localhost:3000`
4. **Single origin**: `https://frontend.com`
5. **Empty values**: Falls back to development defaults

### Code Changes:
1. **Updated field type and validator** in `Settings` class
2. **Added `cors_origins_list` property** for consistent list access
3. **Updated references** in `app/main.py` and `app/core/security.py`

### Example Usage:
```python
# Environment variable can be set as:
CORS_ORIGINS="https://frontend.com,http://localhost:3000"
# or
CORS_ORIGINS='["https://frontend.com","http://localhost:3000"]'

# Both formats work correctly:
from app.core.config import settings
print(settings.cors_origins_list)  # ['https://frontend.com', 'http://localhost:3000']
```

## Testing
- Comprehensive tests validate all input formats
- Application integration tests ensure FastAPI starts correctly
- All edge cases handled (empty arrays, malformed JSON, etc.)

## Validation Script
Added `backend/scripts/validate_env.py` to prevent future deployment issues:
```bash
python scripts/validate_env.py
```

This script validates:
- CORS_ORIGINS format (JSON or comma-separated)
- Database URL format
- Required production environment variables

## Railway Configuration
The `railpack.json` already contains the correct format:
```json
"CORS_ORIGINS": "[\"https://${{services.frontend.RAILWAY_PUBLIC_DOMAIN}}\"]"
```

This now works correctly with the updated field validator.

## Benefits
- ✅ Fixes Railway deployment failures
- ✅ Maintains backward compatibility
- ✅ Supports multiple configuration formats
- ✅ Includes comprehensive validation
- ✅ Prevents future configuration issues