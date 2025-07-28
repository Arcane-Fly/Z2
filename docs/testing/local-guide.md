# Running Tests Locally - Z2 Platform

This guide helps you set up and run the complete test suite for the Z2 platform on your local development environment.

## Quick Start

### Prerequisites
- Python 3.11+ with Poetry
- Node.js 18+ with npm
- PostgreSQL 14+ (for integration tests)
- Redis 6+ (for integration tests)

### Setup Commands
```bash
# Clone and navigate to repository
git clone https://github.com/Arcane-Fly/Z2.git
cd Z2

# Backend setup
cd backend
poetry install
poetry shell

# Frontend setup
cd ../frontend
npm install

# Install Playwright browsers
npx playwright install
```

## Backend Testing

### Environment Setup
```bash
# Create test environment file
cd backend
cp .env.example .env.test

# Edit .env.test with test database settings:
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/z2_test
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=test-secret-key-for-local-development
DEBUG=true
```

### Database Setup
```bash
# Create test database
createdb z2_test

# Run migrations (if needed)
poetry run alembic upgrade head
```

### Running Backend Tests

#### All Tests
```bash
cd backend
poetry run pytest
```

#### Test Categories
```bash
# Unit tests only
poetry run pytest -m "unit"

# Integration tests only  
poetry run pytest -m "integration"

# Security tests only
poetry run pytest -m "security"

# Specific test file
poetry run pytest tests/test_auth.py

# Specific test function
poetry run pytest tests/test_auth.py::test_user_registration
```

#### With Coverage
```bash
# Generate coverage report
poetry run pytest --cov=app --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

#### Parallel Execution
```bash
# Run tests in parallel (faster)
poetry run pytest -n auto
```

#### Debugging Tests
```bash
# Verbose output
poetry run pytest -v -s

# Stop on first failure
poetry run pytest -x

# Debug with pdb
poetry run pytest --pdb

# Run only failed tests from last run
poetry run pytest --lf
```

## Frontend Testing

### Running Frontend Tests

#### All Tests
```bash
cd frontend
npm run test
```

#### Test Categories
```bash
# Run tests once (CI mode)
npm run test -- --run

# Watch mode for development
npm run test:watch

# With coverage
npm run test:coverage

# Specific test file
npm run test -- LoginForm.test.tsx

# Test pattern matching
npm run test -- --testNamePattern="authentication"
```

#### UI Mode (Interactive)
```bash
# Open Vitest UI
npm run test:ui
```

## End-to-End Testing

### Prerequisites
```bash
# Ensure both backend and frontend are running
cd backend
poetry run uvicorn app.main:app --reload &

cd ../frontend  
npm run dev &
```

### Running E2E Tests

#### All E2E Tests
```bash
cd frontend
npm run test:e2e
```

#### Interactive Mode
```bash
# Open Playwright UI
npm run test:e2e:ui

# Run with browser visible
npx playwright test --headed

# Debug mode
npx playwright test --debug
```

#### Specific Browser
```bash
# Chrome only
npx playwright test --project=chromium

# Firefox only
npx playwright test --project=firefox

# Mobile testing
npx playwright test --project="Mobile Chrome"
```

#### Test Reports
```bash
# Generate and open HTML report
npx playwright show-report
```

## Load Testing

### Setup
```bash
cd load-tests
pip install -r requirements.txt
```

### Running Load Tests
```bash
# Basic load test
./run-load-test.sh --host http://localhost:8000 --users 10 --time 2m

# With specific test type
./run-load-test.sh --host http://localhost:8000 --users 20 --time 5m --test-type api

# Headless mode
./run-load-test.sh --host http://localhost:8000 --users 5 --time 1m --headless

# With CSV output
./run-load-test.sh --host http://localhost:8000 --users 10 --time 2m --csv results
```

## Code Quality Checks

### Backend Quality Checks
```bash
cd backend

# Linting
poetry run ruff check .
poetry run ruff format --check .

# Type checking
poetry run mypy app/

# Security scanning
poetry run bandit -r app/
poetry run safety check

# All quality checks
poetry run ruff check . && poetry run mypy app/ && poetry run bandit -r app/
```

### Frontend Quality Checks
```bash
cd frontend

# Linting
npm run lint
npm run format:check

# Type checking
npm run type-check

# All quality checks
npm run lint && npm run type-check && npm run format:check
```

## Accessibility Testing

### Manual A11y Testing
```bash
cd frontend

# Run accessibility tests
npm run test -- --testNamePattern="accessibility"

# E2E accessibility tests
npx playwright test --grep="a11y"
```

### Browser Extensions
- Install axe DevTools browser extension
- Use WAVE Web Accessibility Evaluator
- Test with screen readers (VoiceOver, NVDA)

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check if test database exists
psql -h localhost -p 5432 -l | grep z2_test

# Reset test database
dropdb z2_test && createdb z2_test
```

#### Redis Connection Errors
```bash
# Check if Redis is running
redis-cli ping

# Start Redis (macOS with Homebrew)
brew services start redis

# Start Redis (Linux)
sudo systemctl start redis
```

#### Poetry/Node Dependency Issues
```bash
# Backend: Clear cache and reinstall
cd backend
poetry cache clear pypi --all
rm poetry.lock
poetry install

# Frontend: Clear cache and reinstall  
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Port Conflicts
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process using port
kill -9 $(lsof -t -i:8000)

# Use different port
poetry run uvicorn app.main:app --port 8001
```

### Test-Specific Issues

#### Tests Hanging
- Check for unclosed database connections
- Ensure async tests use proper await
- Check for infinite loops in test code

#### Flaky Tests
- Add proper wait conditions
- Use deterministic test data
- Isolate external dependencies

#### Memory Issues
- Run tests in smaller batches
- Check for memory leaks in test setup
- Use pytest-xdist for parallel execution

## Performance Tips

### Faster Test Execution

#### Backend
```bash
# Use SQLite for unit tests (faster)
export TEST_DATABASE_URL="sqlite+aiosqlite:///./test.db"

# Parallel execution
poetry run pytest -n auto

# Skip slow tests during development
poetry run pytest -m "not slow"
```

#### Frontend
```bash
# Disable coverage during development
npm run test -- --coverage=false

# Run specific test suites
npm run test -- src/components/__tests__
```

### Test Data Optimization
- Use factories for test data generation
- Cache expensive setup operations
- Use minimal test data sets

## IDE Integration

### VS Code
- Install Python Test Explorer extension
- Install Jest Test Explorer extension
- Configure test discovery in settings.json

### PyCharm
- Configure pytest as test runner
- Set up test coverage integration
- Configure database connections for testing

## CI/CD Integration

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Local CI Simulation
```bash
# Run the same checks as CI
cd backend
poetry run ruff check . && \
poetry run mypy app/ && \
poetry run pytest --cov=app

cd ../frontend
npm run lint && \
npm run type-check && \
npm run test -- --run && \
npm run build
```

## Reporting Issues

If you encounter issues with tests:

1. Check this troubleshooting guide first
2. Search existing GitHub issues
3. Create a new issue with:
   - Operating system and versions
   - Full error messages
   - Steps to reproduce
   - Expected vs actual behavior

## Contributing Test Improvements

When adding new tests:

1. Follow the testing strategy guidelines
2. Ensure tests are isolated and deterministic
3. Add appropriate test markers (unit, integration, etc.)
4. Update documentation if needed
5. Test your changes locally before submitting PR

---

For more detailed testing information, see the [Testing Strategy](strategy.md) document.