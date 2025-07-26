# Z2 Roadmap

## Overview

**Vision**: Provide a multi-agent AI platform that orchestrates diverse LLMs to deliver complex tasks with security, compliance and rich user experiences.

**Current status**: The repository contains a foundational backend and frontend skeleton with CI and linting. The model registry and basic agent are implemented, and initial A2A/MCP scaffolding exists, but most core functionality (CRUD endpoints, authentication, database persistence, workflow orchestration, frontend UI) remains unimplemented【201073661165678†L13-L43】【833688497470012†L11-L87】.

This roadmap outlines sequential phases required to build a production-ready platform.

## Phase 1: Foundation & Setup (Completed)

- Project structure for backend and frontend established.
- Pre‑commit hooks, linting, formatting and CI pipeline configured.
- Example environment variables and Sentry integration stubs added【839993457885332†L24-L110】.

## Phase 2: Core API & Database Integration

Goal: Provide fully functional CRUD endpoints for users, agents, models and workflows.

Tasks:
- Connect SQLAlchemy async database and create migrations.
- Implement registration, login and token-based auth endpoints in `auth.py`.
- Implement CRUD endpoints for users, agents and workflows using FastAPI and database models【201073661165678†L13-L43】【833688497470012†L11-L87】.
- Add query and filtering capabilities for listing resources.
- Add validation and error handling.

## Phase 3: LLM & Model Integration

Goal: Provide dynamic model routing across LLM providers with cost/latency management.

Tasks:
- Implement `OpenAIProvider`, `AnthropicProvider` and other provider clients using API keys defined in the config【839993457885332†L24-L110】.
- Extend the model registry to support dynamic capabilities and cost metadata.
- Implement actual calls to selected models in `BasicAIAgent` and remove mock responses【205455321805940†L19-L183】.
- Add caching to reduce cost and latency.

## Phase 4: Agent & Orchestration

Goal: Build multi‑agent orchestration and agent capabilities.

Tasks:
- Complete implementation of dynamic prompt generation and context summarisation in `die.py`【824516705327776†L15-L80】.
- Finalise `maof.py` to handle multi‑agent workflows, agent roles and concurrency.
- Implement runtime workflow execution and state transitions.
- Add event loop and error handling.

## Phase 5: A2A & MCP Protocol Compliance

Goal: Provide fully compliant Agent‑to‑Agent (A2A) and Model Context Protocol (MCP) services.

Tasks:
- Implement capability negotiation, session initiation, resource/tool registry and dynamic loading in `mcp.py`【213792883447280†L81-L146】.
- Implement progress and cancellation flows and streaming responses.
- Persist consent requests, grants and audit logs to the database in `consent.py`【345694937747215†L69-L109】.
- Finalise handshake negotiation and messaging flows in `a2a.py`【106274038081774†L20-L155】.

## Phase 6: Authentication & Authorization

Goal: Provide secure access control and role‑based permissions.

Tasks:
- Add JWT‑based authentication using FastAPI plugins or custom solution.
- Integrate user roles and permissions (admin, user, agent).
- Protect all endpoints with appropriate permissions.
- Implement OAuth integration if required.

## Phase 7: Frontend Application

Goal: Build a responsive UI to manage agents, workflows and monitor sessions.

Tasks:
- Design user interfaces for dashboard, agents, models, workflows and MCP sessions.
- Implement React components that call backend APIs.
- Add forms for creation and editing, progress indicators and notifications.
- Apply consistent styling with the Deep Blue Neon theme.
- Add state management (Redux or Context) and routing.

## Phase 8: Observability & Operations

Goal: Ensure the system can be monitored and operated at scale.

Tasks:
- Integrate structured logging and metrics collection (e.g., Prometheus).
- Connect Sentry for error tracking and alerts.
- Provide health and readiness endpoints and configuration options【910174124011722†L44-L146】.
- Add deployment documentation for container orchestration (Docker, Kubernetes).

## Phase 9: Testing & Quality Assurance

Goal: Achieve high test coverage and reliability.

Tasks:
- Write unit tests for core modules (agents, models, API endpoints).
- Add integration tests for workflows, database interactions and A2A sessions.
- Add end‑to‑end tests for the frontend using Cypress or Playwright.
- Configure test runs in CI and enforce coverage thresholds.

## Phase 10: Documentation & Community

Goal: Provide clear documentation and guidelines for contributors and users.

Tasks:
- Update README with quickstart instructions, architecture diagrams and usage examples.
- Generate API reference documentation with Swagger/Redoc.
- Add `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` files.
- Write protocol specifications for A2A and MCP.
