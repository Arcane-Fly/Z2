# Z2: AI Workforce Platform

Z2 is a next-generation AI platform that delivers dynamic, goal-oriented artificial intelligence through sophisticated multi-agent orchestration. Built for both technical developers and business operators, Z2 transforms how organizations interact with AI by providing adaptive, contextual, and highly scalable AI workflows.

## 🚀 Key Features

### Dynamic Intelligence Engine (DIE)
- **Adaptive Contextual Flows**: Maintains rich context throughout long, complex interactions
- **Dynamic Prompt Generation**: Real-time prompt assembly based on task, context, and target LLM
- **Structured Prompt Engineering**: Cost-efficient, standardized RTF (Role-Task-Format) prompting

### Multi-Agent Orchestration Framework (MAOF)
- **Specialized Agent Teams**: Deploy coordinated teams of AI agents with distinct roles
- **Workflow Orchestration**: Visual, low-code design canvas for complex workflows
- **Collaborative Reasoning**: Multi-agent debate protocols for enhanced accuracy

### Model Integration Layer (MIL)
- **Universal LLM Support**: Seamless integration with OpenAI, Anthropic, Groq, Google, Perplexity
- **Dynamic Model Routing**: Intelligent selection of optimal models based on task requirements
- **Cost Optimization**: Hybrid strategies balancing performance and economic efficiency

### A2A Protocol Support
- **Agent-to-Agent Communication**: Standards-compliant A2A protocol implementation
- **Skill Negotiation**: Dynamic skill discovery and task delegation between agents
- **Real-time Streaming**: WebSocket-based communication for live collaboration

### MCP Protocol Integration
- **Model Context Protocol**: Full MCP server and client implementation
- **Tool Discovery**: Expose and discover AI tools across the platform
- **Resource Management**: Structured access to data and computational resources
- **JSON Schema Contracts**: Formal API contracts for predictable interoperability and validation

### Contract-Based Architecture
- **Validated Interfaces**: JSON Schema contracts for all MCP server operations
- **Early Error Detection**: Request/response validation at API boundaries
- **Self-Documenting**: Schema-driven API documentation and examples
- **Safe Upgrades**: Schema diffing for breaking change detection

## 👥 Dual User Experience

### For Developers ("Architects")
- **Python & JavaScript SDKs**: Full programmatic control
- **CLI Tools**: Command-line interface for scripting and automation
- **Advanced UI**: Visual workflow designer with comprehensive observability
- **Production Controls**: Detailed monitoring, debugging, and performance optimization

### For Business Users ("Operators")
- **Intuitive Portal**: Simple, task-oriented web interface
- **Template Library**: Pre-built solutions for common business tasks
- **Automated Workflows**: One-click deployment of complex AI processes
- **No-Code Setup**: Connect data sources and configure tasks without programming

## 🏗️ Architecture

Z2 follows a modular, cloud-native architecture designed for enterprise-scale deployment:

```
┌─────────────────┐    ┌─────────────────┐
│  Developer Hub  │    │ Non-Dev Portal  │
│  (SDK/CLI/UI)   │    │   (Web App)     │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │    Z2 Core Engine    │
          │  ┌─────┐ ┌─────┐     │
          │  │ DIE │ │MAOF │     │
          │  └─────┘ └─────┘     │
          │       ┌─────┐        │
          │       │ MIL │        │
          │       └─────┘        │
          └──────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼───┐      ┌─────▼─────┐    ┌─────▼─────┐
│ LLMs  │      │Enterprise │    │ Identity  │
│(Multi)│      │   Data    │    │ Provider  │
└───────┘      └───────────┘    └───────────┘
```

## 🛠️ Technology Stack

- **Backend**: Python (FastAPI), PostgreSQL, Redis
- **Frontend**: React + TypeScript
- **AI/ML**: CrewAI, AutoGen, LangChain
- **Infrastructure**: Railway.com, Docker
- **LLM Providers**: OpenAI, Anthropic, Groq, Google, Perplexity

## 🚦 Getting Started

### Current Implementation Status

Z2 is actively developed with significant functionality already implemented:

- **✅ Backend API**: FastAPI application with 50+ endpoints, authentication, database models
- **✅ Protocol Support**: Full A2A and MCP protocol implementations with database persistence
- **✅ Model Integration**: 28+ AI models across 6 providers (OpenAI, Anthropic, Groq, Google AI, Perplexity, xAI) with intelligent routing
- **✅ Frontend Application**: React + TypeScript dashboard with complete agent/workflow management, working modals, and real-time monitoring
- **✅ Real-time Features**: WebSocket integration, live monitoring, and progress tracking
- **🔄 Active Development**: Completing authentication integration and production optimizations

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Arcane-Fly/Z2.git
   cd Z2
   ```

2. **Backend setup**
   ```bash
   cd backend
   pip install poetry
   poetry install
   poetry run uvicorn app.main:app --reload
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

### Railway Deployment

Z2 is optimized for one-click deployment on Railway.com:

1. **Connect to Railway**
   ```bash
   npm install -g @railway/cli
   railway login
   railway link
   ```

2. **Deploy services**
   ```bash
   railway up
   ```

3. **Set environment variables**
   ```bash
   railway variables set OPENAI_API_KEY=your-key
   railway variables set ANTHROPIC_API_KEY=your-key
   # Add other required API keys
   ```

The `railway.toml` configuration automatically sets up:
- Backend API service with PostgreSQL and Redis
- Frontend static site with optimized builds
- Environment-specific configurations
- Health checks and monitoring

See [Setup Guide](docs/setup.md) for detailed installation instructions.

## 📋 Core Principles

- **Adaptability**: Dynamic adjustment to evolving interactions and context
- **Scalability**: Efficient operation under variable workloads
- **Security**: Multi-layered safeguards and compliance-by-design
- **User-Centricity**: Tailored experiences for technical and non-technical users
- **Reliability**: 99.99% uptime with self-healing mechanisms
- **Efficiency**: Optimized for performance and cost-effectiveness

## 🔒 Security & Compliance

Z2 is built with enterprise security in mind:

- **Standards Compliance**: NIST AI RMF, ISO/IEC 42001, UNESCO Ethics
- **Adaptive Safeguards**: AI guardrails against jailbreaking and prompt injection
- **Data Protection**: End-to-end encryption and PII safeguards
- **Audit Trails**: Complete traceability of all AI decisions and data flows

## 📊 Observability

- **Real-time Dashboards**: Monitor agent performance, costs, and system health
- **Chain-of-Thought Tracing**: Debug and optimize agent reasoning processes
- **Performance Analytics**: Latency, throughput, and accuracy metrics
- **Cost Tracking**: Token usage and model costs by agent and workflow

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](docs/)
- [API Reference](docs/api/)
- [Examples](examples/)
- [Community](https://github.com/Arcane-Fly/Z2/discussions)

---

Built with ❤️ for the future of AI-human collaboration.