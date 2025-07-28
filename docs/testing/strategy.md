# Z2 Platform Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the Z2 AI Workforce Platform, designed to ensure reliability, maintainability, and confidence in our system through rigorous quality assurance practices.

## Testing Philosophy

Our testing approach follows the testing pyramid principle:
- **Unit Tests** (70%): Fast, isolated tests for individual components
- **Integration Tests** (20%): Tests for component interactions and API flows  
- **End-to-End Tests** (10%): Full user workflow validation

## Testing Levels

### 1. Unit Testing

#### Backend Unit Tests
- **Location**: `backend/tests/`
- **Framework**: pytest with pytest-asyncio
- **Coverage Target**: 80%+
- **Test Categories**:
  - Database models and business logic
  - Service layer functionality
  - Utility functions and helpers
  - Agent orchestration components
  - Protocol implementations (MCP, A2A)

#### Frontend Unit Tests  
- **Location**: `frontend/src/__tests__/`
- **Framework**: Vitest with React Testing Library
- **Coverage Target**: 80%+
- **Test Categories**:
  - React component rendering and behavior
  - Hook functionality
  - Utility functions
  - Form validation logic
  - State management

#### Running Unit Tests

**Backend:**
```bash
cd backend
poetry run pytest tests/ -m "unit"
poetry run pytest tests/ --cov=app --cov-report=html
```

**Frontend:**
```bash
cd frontend
npm run test
npm run test:coverage
npm run test:watch  # for development
```

### 2. Integration Testing

#### Backend Integration Tests
- **Purpose**: Test full API flows and database interactions
- **Test Scenarios**:
  - User registration and authentication workflows
  - CRUD operations with real database connections
  - Workflow execution with agent coordination
  - A2A/MCP protocol negotiations
  - Consent management flows

#### Frontend Integration Tests
- **Purpose**: Test component interactions and data flow
- **Test Scenarios**:
  - Form submissions with API calls
  - Navigation and routing
  - Authentication flows
  - Real-time updates and WebSocket connections

#### Running Integration Tests

```bash
# Backend - requires test database
cd backend
poetry run pytest tests/ -m "integration"

# Frontend - with mock API
cd frontend
npm run test -- --run integration
```

### 3. End-to-End Testing

#### E2E Framework
- **Tool**: Playwright
- **Location**: `frontend/e2e/`
- **Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile**: iOS Safari, Android Chrome

#### E2E Test Scenarios
- **Authentication Flow**: Registration, login, logout
- **Agent Management**: Create, configure, deploy agents
- **Workflow Creation**: Visual workflow builder usage
- **Model Selection**: LLM provider configuration
- **User Roles**: Different user type workflows
- **Error Handling**: Network failures, validation errors

#### Running E2E Tests

```bash
cd frontend
npm run test:e2e
npm run test:e2e:ui  # interactive mode
npx playwright test --headed  # see browser
```

### 4. Performance Testing

#### Load Testing
- **Tool**: Locust
- **Location**: `load-tests/`
- **Scenarios**:
  - Concurrent user sessions
  - API endpoint stress testing
  - Workflow execution under load
  - Database performance testing

#### Running Load Tests

```bash
cd load-tests
./run-load-test.sh --host http://localhost:8000 --users 50 --time 5m
```

## Quality Assurance Tools

### Static Analysis

#### Backend (Python)
- **Linting**: Ruff for code style and error detection
- **Type Checking**: MyPy for static type analysis
- **Security**: Bandit for security vulnerability scanning
- **Formatting**: Black for consistent code formatting

```bash
cd backend
poetry run ruff check .
poetry run ruff format .
poetry run mypy app/
poetry run bandit -r app/
```

#### Frontend (TypeScript)
- **Linting**: ESLint with TypeScript rules
- **Type Checking**: TypeScript compiler
- **Formatting**: Prettier for consistent formatting
- **Accessibility**: ESLint jsx-a11y plugin

```bash
cd frontend
npm run lint
npm run lint:fix
npm run type-check
npm run format
```

### Security Testing

#### Vulnerability Scanning
- **Dependencies**: Safety (Python), npm audit (Node.js)
- **Code Security**: Bandit, Semgrep
- **Container Security**: Docker Scout, Trivy
- **API Security**: Custom security test suite

#### Running Security Tests

```bash
# Python dependencies
cd backend
poetry run safety check

# Node.js dependencies  
cd frontend
npm audit

# Security-focused test suite
cd backend
poetry run pytest tests/ -m "security"
```

### Accessibility Testing

#### Automated A11y Testing
- **Tool**: axe-core integrated with tests
- **Standards**: WCAG 2.1 AA compliance
- **Integration**: Playwright + axe, Jest + axe

```bash
cd frontend
npm run test -- --testNamePattern="accessibility"
npx playwright test --grep="a11y"
```

## Test Data Management

### Test Databases
- **Backend**: SQLite for unit tests, PostgreSQL for integration
- **Isolation**: Each test gets a fresh database state
- **Fixtures**: Comprehensive test data factories
- **Cleanup**: Automatic teardown after test completion

### Mock Services
- **External APIs**: LLM providers, third-party services
- **WebSockets**: Real-time communication testing
- **File Systems**: Upload/download functionality
- **Network Conditions**: Timeout and failure scenarios

## Continuous Integration

### GitHub Actions Workflows
- **Backend Pipeline**: Test → Lint → Security → Build
- **Frontend Pipeline**: Test → Lint → A11y → Build
- **E2E Pipeline**: Build → Deploy → Test → Report
- **Performance Pipeline**: Load test on main branch changes

### Test Reporting
- **Coverage Reports**: HTML, XML, JSON formats
- **Test Results**: JUnit XML for CI integration
- **Performance Metrics**: Response times, throughput
- **Security Reports**: Vulnerability scan results

## Test Environment Setup

### Local Development

#### Prerequisites
```bash
# Backend
cd backend
poetry install
poetry shell

# Frontend
cd frontend
npm install

# E2E Tests
npx playwright install
```

#### Environment Variables
```bash
# Backend testing
export TEST_DATABASE_URL="postgresql://user:pass@localhost/z2_test"
export REDIS_URL="redis://localhost:6379/1"
export SECRET_KEY="test-secret-key"

# Frontend testing
export VITE_API_URL="http://localhost:8000"
```

### CI/CD Environment
- **Database**: PostgreSQL and Redis services
- **Parallelization**: Tests run in parallel workers
- **Caching**: Dependencies and build artifacts cached
- **Artifacts**: Test reports and coverage data stored

## Best Practices

### Writing Good Tests

#### Backend Tests
```python
# Good: Descriptive test name
def test_user_registration_creates_user_with_hashed_password():
    # Given: valid user data
    user_data = {"username": "test", "password": "secure123!"}
    
    # When: registering user
    result = register_user(user_data)
    
    # Then: user created with hashed password
    assert result.username == "test"
    assert result.password != "secure123!"
    assert verify_password("secure123!", result.password)
```

#### Frontend Tests
```typescript
// Good: Test behavior, not implementation
test('submits form when valid data is entered', async () => {
  render(<LoginForm onSuccess={mockOnSuccess} />)
  
  await user.type(screen.getByLabelText(/username/i), 'testuser')
  await user.type(screen.getByLabelText(/password/i), 'password123')
  await user.click(screen.getByRole('button', { name: /sign in/i }))
  
  await waitFor(() => {
    expect(mockOnSuccess).toHaveBeenCalled()
  })
})
```

### Test Organization
- **Arrange-Act-Assert**: Clear test structure
- **Single Responsibility**: One assertion per test
- **Independent Tests**: No dependencies between tests
- **Meaningful Names**: Test names describe the scenario
- **Fast Feedback**: Quick test execution for rapid development

### Coverage Guidelines
- **Line Coverage**: Minimum 80% for new code
- **Branch Coverage**: Critical paths must be tested
- **Exclusions**: Generated code, external libraries
- **Quality over Quantity**: Meaningful tests over coverage numbers

## Debugging Failed Tests

### Common Issues
1. **Database State**: Tests affecting each other
2. **Async Operations**: Race conditions in async tests
3. **Mock Configuration**: Incorrect mock setup
4. **Environment Differences**: Local vs CI environment

### Debugging Tools
```bash
# Run specific test with verbose output
poetry run pytest tests/test_auth.py::test_login -v -s

# Debug with pdb
poetry run pytest tests/test_auth.py::test_login --pdb

# Frontend debugging
npm run test -- --reporter=verbose LoginForm.test.tsx
```

## Contributing Guidelines

### Before Submitting
1. Run full test suite locally
2. Ensure coverage requirements met
3. Update tests for new features
4. Add security tests for sensitive changes
5. Document complex test scenarios

### Test Review Checklist
- [ ] Tests cover happy path and edge cases
- [ ] Error conditions properly tested
- [ ] Security implications considered
- [ ] Performance impact assessed
- [ ] Documentation updated

## Metrics and Monitoring

### Test Metrics
- **Test Execution Time**: Track and optimize slow tests
- **Flaky Test Detection**: Identify unreliable tests
- **Coverage Trends**: Monitor coverage over time
- **Failure Rates**: Track test stability

### Quality Gates
- **Pre-merge**: All tests must pass
- **Coverage**: Minimum thresholds enforced
- **Security**: No high-severity vulnerabilities
- **Performance**: No significant regressions

---

For questions about testing practices or to contribute improvements to this strategy, please reach out to the development team or create an issue in our repository.