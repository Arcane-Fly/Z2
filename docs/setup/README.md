# Z2 AI Workforce Platform - Setup Guide

This comprehensive guide will help you set up the Z2 AI Workforce Platform for development and production deployment. Z2 is an enterprise-grade AI platform with dynamic multi-agent orchestration, designed to serve both developers ("Architects") and non-developers ("Operators").

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Required Software
- **Python 3.11 or higher** - [Download](https://python.org/downloads/)
- **Node.js 18 or higher** - [Download](https://nodejs.org/download/)
- **Git** - [Download](https://git-scm.com/downloads)

### For Local Development
- **PostgreSQL 14+** - [Download](https://postgresql.org/download/) OR use Docker
- **Redis 6+** - [Download](https://redis.io/download/) OR use Docker

### For Containerized Development (Recommended)
- **Docker** - [Download](https://docker.com/get-started/)
- **Docker Compose** - Usually included with Docker

## 🚀 Quick Start with Docker (Recommended)

The fastest way to get Z2 running is with Docker Compose. This method automatically sets up all services including databases.

```bash
# 1. Clone the repository
git clone https://github.com/Arcane-Fly/Z2.git
cd Z2

# 2. Copy environment configuration files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Edit your environment files (see Environment Configuration section)
# At minimum, add your LLM API keys to backend/.env

# 4. Start all services
docker-compose up -d

# 5. Wait for services to be healthy (about 30-60 seconds)
docker-compose ps

# 6. Access the application
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

## 🔧 Development Setup (Local)

For active development, you may prefer running services locally for better debugging and faster iteration.

### 1. Automated Setup Script

We provide an automated setup script that handles most of the configuration:

```bash
# Clone and run setup
git clone https://github.com/Arcane-Fly/Z2.git
cd Z2
./scripts/setup.sh
```

The script will:
- Install Poetry for Python dependency management
- Install backend dependencies
- Install frontend dependencies
- Create environment files from examples
- Set up pre-commit hooks
- Start required services with Docker

### 2. Manual Setup

If you prefer manual setup or the automated script encounters issues:

#### Step 1: Backend Setup

```bash
cd backend

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -
# On Windows: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Install Python dependencies
poetry install

# Copy and configure environment
cp .env.example .env
# Edit .env file with your configuration (see Environment Configuration section)

# Install pre-commit hooks
poetry run pre-commit install
```

#### Step 2: Frontend Setup

```bash
cd ../frontend

# Install Node.js dependencies
npm install

# Copy and configure environment
cp .env.example .env
# Edit .env file with your configuration
```

#### Step 3: Database Setup

Choose one of the following options:

**Option A: Docker (Recommended for Development)**
```bash
# Start PostgreSQL and Redis with Docker
docker-compose up postgres redis -d

# Wait for services to be healthy
docker-compose ps
```

**Option B: Local Installation**
```bash
# Install PostgreSQL and Redis locally (varies by OS)

# Create database
createdb z2

# Update DATABASE_URL in backend/.env
# DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/z2

# Start Redis
redis-server
```

#### Step 4: Start Development Services

```bash
# Terminal 1: Start backend
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## ⚙️ Environment Configuration

### Backend Environment Variables

The backend requires several environment variables for proper operation. Copy `backend/.env.example` to `backend/.env` and configure:

#### Required LLM Provider API Keys
```bash
# Get these from the respective provider dashboards
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here          # Optional but recommended
GOOGLE_API_KEY=your_google_key_here      # Optional
PERPLEXITY_API_KEY=your_perplexity_key   # Optional
```

#### Database Configuration
```bash
# For Docker setup
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/z2
REDIS_URL=redis://localhost:6379/0

# For custom setup
DATABASE_URL=postgresql+asyncpg://your_user:your_pass@your_host:5432/z2
```

#### Security Settings
```bash
# Generate a secure secret key (32+ character random string)
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### Frontend Environment Variables

Copy `frontend/.env.example` to `frontend/.env` and configure:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags (enable/disable features during development)
VITE_ENABLE_DEBUG=true
VITE_ENABLE_AGENT_BUILDER=true
VITE_ENABLE_WORKFLOW_DESIGNER=true
```

## 🔑 LLM Provider Setup

Z2 integrates with multiple LLM providers for maximum flexibility and cost optimization. You'll need API keys from at least one provider to use the AI features.

### Required: OpenAI
- **Why**: Primary model provider with GPT-4o series and o-series reasoning models
- **Get API Key**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Models Used**: gpt-4o, gpt-4o-mini, o1, o3-mini, dall-e-3, whisper-1
- **Cost**: Varies by model, see [OpenAI Pricing](https://openai.com/pricing)

### Recommended: Additional Providers

1. **Anthropic Claude**
   - **Why**: Superior reasoning capabilities, longer context windows
   - **Get API Key**: [console.anthropic.com](https://console.anthropic.com/)
   - **Models Used**: claude-3-5-sonnet, claude-3-haiku
   
2. **Groq**
   - **Why**: Ultra-fast inference speeds (280+ tokens/second)
   - **Get API Key**: [console.groq.com/keys](https://console.groq.com/keys)
   - **Models Used**: llama-3.1-70b, mixtral-8x7b

3. **Google AI**
   - **Why**: Multimodal capabilities, 1M+ token context
   - **Get API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Models Used**: gemini-2.5-pro, gemini-2.5-flash

4. **Perplexity AI**
   - **Why**: Real-time web search with citations
   - **Get API Key**: [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
   - **Models Used**: llama-3.1-sonar-large-128k-online

> **Note**: You don't need ALL API keys to get started. Z2's Model Integration Layer (MIL) will automatically route requests to available providers.

## ✅ Verification & Testing

Once everything is running, verify your setup:

### 1. Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "0.1.0", "components": {...}}
```

### 2. API Documentation
Visit http://localhost:8000/docs to explore the interactive API documentation (Swagger UI).

### 3. Frontend Application
Visit http://localhost:3000 to access the Z2 web interface.

### 4. Run Tests
```bash
# Backend tests
cd backend
poetry run pytest

# Frontend tests (if available)
cd frontend
npm run test
```

## 🔨 Development Workflow

### Running Tests
```bash
# Backend tests with coverage
cd backend
poetry run pytest --cov=app --cov-report=html

# Frontend linting and type checking
cd frontend
npm run lint
npm run type-check
```

### Code Quality
```bash
# Backend formatting and linting
cd backend
poetry run black .
poetry run ruff check .

# Frontend formatting and linting
cd frontend
npm run format
npm run lint:fix
```

### Database Migrations
```bash
# Generate new migration
cd backend
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
poetry run alembic upgrade head

# Revert last migration
poetry run alembic downgrade -1
```

## 🚢 Production Deployment

### Railway.app (Recommended)

Z2 is optimized for deployment on Railway.app with minimal configuration:

1. **Connect Repository**: Link your GitHub repository to Railway
2. **Set Environment Variables**: Configure all required variables in Railway dashboard
3. **Deploy**: Railway automatically deploys from your main branch

#### Railway Environment Variables
```bash
# Database (automatically set by Railway)
DATABASE_URL=${Postgres.DATABASE_URL}
REDIS_URL=${Redis.REDIS_URL}

# LLM Provider Keys (set these manually)
OPENAI_API_KEY=your_production_key
ANTHROPIC_API_KEY=your_production_key
# ... other keys

# Security
SECRET_KEY=your_production_secret_key
DEBUG=false
LOG_LEVEL=INFO

# Frontend
VITE_API_BASE_URL=https://${backend.RAILWAY_PUBLIC_DOMAIN}
VITE_ENABLE_DEBUG=false
```

### Other Deployment Options

#### Docker Deployment
```bash
# Build and push to registry
docker build -f Dockerfile.backend -t your-registry/z2-backend .
docker build -f Dockerfile.frontend -t your-registry/z2-frontend .
docker push your-registry/z2-backend
docker push your-registry/z2-frontend

# Deploy to your container platform
```

#### Traditional VPS/Cloud Deployment
```bash
# Backend
cd backend
poetry build
poetry export -f requirements.txt --output requirements.txt
# Deploy requirements.txt and built package to server

# Frontend
cd frontend
npm run build
# Deploy dist/ folder to static hosting/CDN
```

## 🐛 Troubleshooting

### Common Issues

#### "Database Connection Error"
```bash
# Check if PostgreSQL is running
docker-compose ps postgres
# OR
pg_isready -h localhost -p 5432

# Verify DATABASE_URL format
# postgresql+asyncpg://user:password@host:port/database
```

#### "Redis Connection Error"
```bash
# Check if Redis is running
docker-compose ps redis
# OR
redis-cli ping

# Should return "PONG"
```

#### "LLM API Errors"
```bash
# Check API keys are set correctly
poetry run python -c "import os; print(os.getenv('OPENAI_API_KEY', 'NOT_SET'))"

# Verify API keys are valid (test with curl)
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### "Frontend Build Errors"
```bash
# Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check TypeScript configuration
npm run type-check
```

#### "Port Already in Use"
```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill   # Backend
lsof -ti:3000 | xargs kill   # Frontend

# Or change ports in environment files
```

#### "Permission Denied (Poetry)"
```bash
# Fix Poetry path
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Restart shell or source bashrc
source ~/.bashrc
```

### Performance Issues

#### Slow Agent Responses
1. Check which models are being used (prefer faster models for simple tasks)
2. Verify network connectivity to LLM providers
3. Check rate limits aren't being exceeded
4. Monitor token usage in backend logs

#### High Memory Usage
1. Reduce concurrent agent limits in backend/.env
2. Implement agent result caching
3. Check for memory leaks in long-running workflows

### Getting Help

- **Documentation**: Check the [full documentation](../README.md)
- **API Reference**: Visit http://localhost:8000/docs when running
- **GitHub Issues**: [Open an issue](https://github.com/Arcane-Fly/Z2/issues)
- **Discord Community**: Join our [Discord server](https://discord.gg/z2-ai)

## 📚 Next Steps

After successful setup, explore:

- **[User Guide](../guides/user-guide.md)** - Learn how to use Z2 as an Operator
- **[Developer Guide](../guides/developer-guide.md)** - Learn how to extend Z2 as an Architect  
- **[API Reference](../api/)** - Detailed API documentation
- **[Agent Framework Guide](../guides/agent-framework.md)** - Understanding DIE, MIL, and MAOF
- **[Examples](../../examples/)** - Sample workflows and integrations

## 🔄 Keeping Up to Date

```bash
# Pull latest changes
git pull origin main

# Update backend dependencies
cd backend
poetry install

# Update frontend dependencies
cd frontend
npm install

# Run database migrations
cd backend
poetry run alembic upgrade head

# Restart services
docker-compose restart  # If using Docker
# OR restart your local services
```

---

*This setup guide is maintained to reflect the current state of the Z2 platform. Last updated: 2024-12-19*