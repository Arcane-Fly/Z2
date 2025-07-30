# Contributing to Z2 AI Workforce Platform

We're excited that you're interested in contributing to Z2! This guide will help you get started with contributing to our AI workforce platform.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Coding Standards](#coding-standards)
- [Contribution Workflow](#contribution-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [team@z2.ai](mailto:team@z2.ai).

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - For backend development
- **Node.js 18+** - For frontend development  
- **PostgreSQL 14+** - For database operations
- **Redis 6+** - For caching and sessions
- **Git** - For version control
- **Docker** (optional) - For containerized development

### Development Environment Setup

#### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/Z2.git
cd Z2

# Add upstream remote
git remote add upstream https://github.com/Arcane-Fly/Z2.git
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Poetry (Python dependency manager)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
poetry run alembic upgrade head

# Start the backend server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the development server
npm run dev
```

#### 4. Database Setup

**Option A: Local PostgreSQL**
```bash
# Create database
createdb z2_dev

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://username:password@localhost/z2_dev
```

**Option B: Docker**
```bash
# Start services with Docker Compose
docker-compose up postgres redis -d
```

#### 5. Verify Setup

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:5173  
- API Documentation: http://localhost:8000/docs

## Coding Standards

### Python (Backend)

We use strict coding standards to ensure code quality and consistency:

**Formatting and Linting:**
- **Black** - Code formatting (line length: 88)
- **Ruff** - Fast Python linter  
- **MyPy** - Static type checking
- **Bandit** - Security linting

**Run all checks:**
```bash
cd backend

# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy .

# Security scanning
poetry run bandit -r app/
```

**Code Style Guidelines:**
- Follow PEP 8 standards
- Use type hints for all functions and methods
- Write docstrings for public functions using Google style
- Prefer async/await for I/O operations
- Use Pydantic models for data validation
- Keep functions focused and under 50 lines when possible

**Example:**
```python
from typing import List, Optional
from pydantic import BaseModel


class AgentCreate(BaseModel):
    """Model for creating a new agent."""
    name: str
    description: Optional[str] = None
    agent_type: str
    capabilities: List[str]


async def create_agent(
    agent_data: AgentCreate,
    user_id: str,
    db: AsyncSession
) -> Agent:
    """
    Create a new agent.
    
    Args:
        agent_data: Agent creation data
        user_id: ID of the user creating the agent
        db: Database session
        
    Returns:
        Created agent instance
        
    Raises:
        ValueError: If agent data is invalid
    """
    # Implementation here
    pass
```

### TypeScript/React (Frontend)

**Formatting and Linting:**
- **ESLint** - Code linting with TypeScript rules
- **Prettier** - Code formatting
- **TypeScript** - Static type checking

**Run all checks:**
```bash
cd frontend

# Lint and fix
npm run lint:fix

# Format code
npm run format

# Type checking
npm run type-check
```

**Code Style Guidelines:**
- Use TypeScript for all new code
- Follow React best practices and hooks patterns
- Use functional components with hooks
- Prefer const assertions and strict typing
- Use meaningful component and variable names
- Keep components focused and under 200 lines

**Example:**
```typescript
interface AgentCardProps {
  agent: Agent;
  onEdit: (agent: Agent) => void;
  onDelete: (agentId: string) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ 
  agent, 
  onEdit, 
  onDelete 
}) => {
  const handleEdit = useCallback(() => {
    onEdit(agent);
  }, [agent, onEdit]);

  return (
    <div className="agent-card">
      <h3>{agent.name}</h3>
      <p>{agent.description}</p>
      <button onClick={handleEdit}>Edit</button>
    </div>
  );
};
```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```
feat(agents): add multi-agent collaboration support

fix(auth): resolve JWT token expiration issue

docs(api): update authentication endpoint documentation

test(workflows): add integration tests for workflow execution
```

### Branch Naming Convention

Use descriptive branch names that follow this pattern:

```
<type>/<description>
```

**Types:**
- `feature/` - New features
- `fix/` - Bug fixes  
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test-related changes

**Examples:**
```
feature/multi-agent-orchestration
fix/workflow-execution-timeout
docs/api-reference-update
refactor/auth-service-cleanup
test/integration-test-suite
```

## Contribution Workflow

### 1. Create an Issue

Before starting work, create or find an existing issue that describes:
- The problem you're solving
- The proposed solution
- Any design considerations

### 2. Set Up Your Branch

```bash
# Sync with upstream
git checkout main
git pull upstream main

# Create your feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Write your code following our coding standards
- Add or update tests as needed
- Update documentation for any API changes
- Run the full test suite

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with conventional message
git commit -m "feat(component): add new feature description"
```

### 5. Submit a Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Testing Guidelines

### Backend Testing

**Test Structure:**
```
backend/tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for API endpoints
├── e2e/           # End-to-end tests
└── conftest.py    # Shared test configuration
```

**Running Tests:**
```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test categories
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m e2e
```

**Writing Tests:**
```python
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_agent():
    """Test agent creation endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agents",
            json={
                "name": "Test Agent",
                "agent_type": "researcher",
                "capabilities": ["search", "analyze"]
            }
        )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test Agent"
```

### Frontend Testing

**Test Structure:**
```
frontend/src/
├── __tests__/          # Component tests
├── components/
│   └── __tests__/      # Component-specific tests
└── test-utils.tsx      # Shared test utilities
```

**Running Tests:**
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e
```

**Writing Tests:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentCard } from '../AgentCard';

const mockAgent = {
  id: '1',
  name: 'Test Agent',
  description: 'Test description',
  type: 'researcher'
};

describe('AgentCard', () => {
  it('displays agent information', () => {
    const onEdit = jest.fn();
    const onDelete = jest.fn();
    
    render(
      <AgentCard 
        agent={mockAgent} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });
});
```

## Documentation

### Code Documentation

- **Python**: Use Google-style docstrings
- **TypeScript**: Use JSDoc comments for complex functions
- **API**: Update OpenAPI specs for endpoint changes

### Documentation Files

- Update relevant `.md` files for feature changes
- Add examples for new API endpoints
- Include screenshots for UI changes
- Keep architecture diagrams current

### Documentation Testing

```bash
# Check markdown formatting
cd frontend && npm run lint:toml

# Validate documentation links (if tool available)
# markdown-link-check docs/**/*.md
```

## Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce the bug
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, browser, Python/Node versions
6. **Logs**: Relevant error messages or logs
7. **Screenshots**: For UI issues

Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Feature Requests

For feature requests, include:

1. **Problem**: What problem does this solve?
2. **Solution**: Proposed solution or feature
3. **Alternatives**: Alternative solutions considered
4. **Use Cases**: How would this be used?
5. **Implementation**: Technical considerations (optional)

Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages follow convention

### PR Description

Use our [PR template](.github/PULL_REQUEST_TEMPLATE.md) and include:

- **Description**: What does this PR do?
- **Type**: Feature, fix, docs, etc.
- **Testing**: How was this tested?
- **Screenshots**: For UI changes
- **Breaking Changes**: Any breaking changes
- **Related Issues**: Link to related issues

### Review Process

1. **Automated Checks**: CI/CD must pass
2. **Code Review**: At least one maintainer review
3. **Testing**: Manual testing if needed
4. **Documentation**: Docs review for significant changes
5. **Approval**: Maintainer approval required
6. **Merge**: Squash and merge preferred

### Review Guidelines

**For Reviewers:**
- Review for functionality, style, and maintainability
- Test the changes locally if needed
- Provide constructive feedback
- Approve when satisfied with quality

**For Authors:**
- Respond to feedback promptly
- Make requested changes
- Mark conversations as resolved
- Rebase if needed to keep history clean

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Email**: [team@z2.ai](mailto:team@z2.ai) for sensitive issues

### Getting Help

1. Check existing documentation
2. Search GitHub issues and discussions
3. Ask in GitHub Discussions
4. Attend community calls (when available)

### Recognition

We value all contributions! Contributors will be:
- Listed in our [CHANGELOG.md](CHANGELOG.md)
- Mentioned in release notes
- Invited to our contributors' Discord (when available)

## Development Tips

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### IDE Setup

**VS Code Extensions:**
- Python
- Pylance  
- Black Formatter
- Ruff
- TypeScript and JavaScript
- ESLint
- Prettier

**PyCharm/IntelliJ:**
- Enable Python type checking
- Configure Black as formatter
- Install Ruff plugin

### Debugging

**Backend:**
```bash
# Debug mode
poetry run uvicorn app.main:app --reload --log-level debug

# With debugger
poetry run python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
# Debug mode
npm run dev

# Debug in VS Code with Chrome debugger
```

### Performance Testing

```bash
# Backend load testing
cd load-tests
python run_load_test.py

# Frontend performance
npm run test:e2e -- --project=performance
```

## Questions?

If you have questions not covered in this guide:

1. Check our [documentation](docs/)
2. Search [GitHub Issues](https://github.com/Arcane-Fly/Z2/issues)
3. Ask in [GitHub Discussions](https://github.com/Arcane-Fly/Z2/discussions)
4. Email us at [team@z2.ai](mailto:team@z2.ai)

Thank you for contributing to Z2! 🚀