# Railway Configuration Reference

## TOML Syntax Rules

Railway uses TOML (Tom's Obvious, Minimal Language) format for configuration files. Here are the key syntax rules:

### Basic Syntax
- Use `key = "value"` format (not `key: "value"` like YAML/JSON)
- Section headers: `[section]`
- Nested sections: `[section.subsection]`
- Arrays: `array = ["item1", "item2"]`
- Booleans: `enabled = true` or `enabled = false`
- Numbers: `port = 8080`

### Common Mistakes
❌ **Wrong (YAML-style)**:
```yaml
services:
  backend:
    source: backend
    variables:
      DEBUG: false
```

✅ **Correct (TOML)**:
```toml
[services.backend]
source = "backend"

[services.backend.variables]
DEBUG = false
```

## Validation Commands

### Local Validation
```bash
# Using Python built-in TOML parser
python3 scripts/validate-toml.py railway.toml

# Using npm script (from frontend directory)
npm run lint:toml
```

### Pre-commit Hook
The repository includes a `check-toml` hook in `.pre-commit-config.yaml` that validates TOML syntax before commits.

## Railway TOML Structure

### Single Service Configuration
```toml
[build]
builder = "nixpacks"
buildCommand = "echo building!"

[deploy]
startCommand = "echo starting!"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "never"

[environments.production]
NODE_ENV = "production"
DEBUG = "false"
```

### Multi-Service Configuration
For multi-service deployments, each service should have its own railway.toml or be deployed as separate Railway services.

## Troubleshooting

### Common TOML Errors
1. **"keys cannot contain : character"** - Using YAML syntax instead of TOML
2. **"Expected '=' after a key"** - Missing equals sign in key-value pairs
3. **"Duplicate key"** - Having multiple sections with the same name

### Fix Process
1. Backup the original file: `cp railway.toml railway.toml.backup`
2. Convert YAML-style syntax to TOML
3. Validate with: `python3 scripts/validate-toml.py railway.toml`
4. Test deployment