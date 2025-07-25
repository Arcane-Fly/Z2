# Z2 Setup Guide

This guide will help you set up the Z2 AI Workforce Platform for development and production.

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 14+ (or Docker)
- Redis 6+ (or Docker)
- Git

## Quick Start with Docker

The fastest way to get Z2 running is with Docker Compose:

```bash
# Clone the repository
git clone https://github.com/Arcane-Fly/Z2.git
cd Z2

# Start all services
docker-compose up -d

# The application will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## Development Setup

### 1. Automated Setup

Run the setup script for automatic configuration:

```bash
./scripts/setup.sh
```

### 2. Manual Setup

If you prefer manual setup or the script fails:

#### Backend Setup

```bash
cd backend

# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
# At minimum, set your LLM API keys:
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# etc.

# Start the development server
poetry run uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env

# Start the development server
npm run dev
```

#### Database Setup

You can either use Docker or install PostgreSQL locally:

**Option A: Docker (Recommended)**
```bash
docker-compose up postgres redis -d
```

**Option B: Local Installation**
```bash
# Create database
createdb z2

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/z2
```

## Environment Configuration

### Backend Environment Variables

Key environment variables you need to configure:

```bash
# LLM Provider API Keys (Required for AI functionality)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_key
PERPLEXITY_API_KEY=your_perplexity_key

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/z2
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this
```

### Frontend Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_DEBUG=true
```

## API Keys Setup

Z2 integrates with multiple LLM providers. You'll need API keys from:

1. **OpenAI**: Get your API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. **Anthropic**: Get your API key from [console.anthropic.com](https://console.anthropic.com/)
3. **Groq**: Get your API key from [console.groq.com](https://console.groq.com/keys)
4. **Google**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
5. **Perplexity**: Get your API key from [perplexity.ai](https://www.perplexity.ai/settings/api)

> **Note**: You don't need ALL API keys to get started. Z2 will work with whatever providers you configure.

## Verification

Once everything is running, verify your setup:

1. **Backend Health Check**: Visit http://localhost:8000/health
2. **API Documentation**: Visit http://localhost:8000/docs
3. **Frontend**: Visit http://localhost:3000
4. **Database Connection**: Check backend logs for successful database connection

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
poetry run pytest

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Backend linting and formatting
cd backend
poetry run ruff check .
poetry run black .

# Frontend linting and formatting
cd frontend
npm run lint
npm run format
```

### Database Migrations

```bash
cd backend
poetry run alembic revision --autogenerate -m "Description of changes"
poetry run alembic upgrade head
```

## Production Deployment

### Railway.app (Recommended)

1. **Connect your GitHub repository** to Railway
2. **Set environment variables** in Railway dashboard
3. **Deploy**: Railway will automatically deploy from your main branch

### Manual Deployment

1. **Build the application**:
   ```bash
   # Backend
   cd backend
   poetry build

   # Frontend
   cd frontend
   npm run build
   ```

2. **Deploy to your hosting provider** of choice

## Troubleshooting

### Common Issues

**Database Connection Error**
- Ensure PostgreSQL is running
- Check DATABASE_URL format
- Verify database exists

**API Key Errors**
- Check that API keys are properly set in .env
- Verify API keys are valid and have sufficient credits
- Check for trailing spaces in environment variables

**Port Already in Use**
- Change ports in .env files
- Kill existing processes: `lsof -ti:8000 | xargs kill`

**Module Not Found Errors**
- Reinstall dependencies: `poetry install` or `npm install`
- Check Python/Node versions

### Getting Help

- Check the [API Documentation](../api/)
- Review [Development Guides](../guides/)
- Open an issue on GitHub
- Join our [Discord Community](https://discord.gg/z2-ai)

## Next Steps

After setup, check out:

- [User Guide](../guides/user-guide.md) - Learn how to use Z2
- [Developer Guide](../guides/developer-guide.md) - Learn how to extend Z2
- [API Reference](../api/) - Detailed API documentation
- [Examples](../../examples/) - Sample workflows and integrations