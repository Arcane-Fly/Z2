Okay, let's establish the foundational standards for Z2 based on the requirements and the provided documentation.

---

### Edit your tech stack

**File:** `~/.agent-os/standards/tech-stack.md`

```markdown
# Z2 Tech Stack

This document defines the preferred technologies, frameworks, and services for building Z2 to production standard.

## Core Application Framework

*   **Primary Backend Framework:** Python (FastAPI)
    *   Chosen for its asynchronous capabilities, speed, ease of development, and strong ecosystem for AI/ML integration.
*   **Primary Frontend Framework:** React (with TypeScript)
    *   Standard for building interactive user interfaces, with a strong component-based architecture. TypeScript adds type safety.
*   **Multi-Agent Orchestration:** CrewAI or AutoGen (TBD based on evaluation for dynamic prompt capabilities and adaptability)
    *   These frameworks align with the need for dynamic, orchestrated AI workforces.

## Language Model Integration

*   **Primary LLM Provider:** OpenAI (GPT-4.1 series)
    *   For complex reasoning, adaptability, and dynamic prompt generation.
*   **Cost-Effective/High-Volume Tasks:** Groq (Llama 3.3 70B) or OpenAI (GPT-4.1-mini)
    *   Groq for ultra-fast inference where speed is critical. GPT-4.1-mini for balance of cost/speed/performance.
*   **Specialized Tasks:**
    *   **Real-time Search/Citations:** Perplexity AI (`llama-3.1-sonar-large-128k-online`)
    *   **Safety/Complex Analysis:** Anthropic Claude 3.5 Sonnet
    *   **Multimodal (if needed):** Google Gemini 2.5 Flash/Pro
*   **API Abstraction:** Standardized SDKs (`openai`, `groq`, `anthropic`, `google-genai`, `perplexityai`) for direct integration. Potentially use a unified interface layer.

## Data Management

*   **Primary Database:** PostgreSQL
    *   Robust, reliable, supports complex queries and relationships, good for structured agent state, user data, and logs.
*   **Vector Store (for RAG, if needed):** Chroma or Qdrant
    *   Standard choices for integrating retrieval-augmented generation capabilities.
*   **Cache:** Redis
    *   For session management, caching frequent LLM responses or computations.
*   **File Storage:** AWS S3 (or equivalent like Railway Volume)
    *   For storing user uploads, agent configurations, etc.

## Infrastructure & Hosting

*   **Hosting Platform:** Railway.com
    *   As specified. Offers good integration with modern stacks and simplifies deployment.
*   **Containerization:** Docker
    *   For consistent environments across development, staging, and production.
*   **Orchestration (if needed at scale):** Railway's built-in capabilities or Kubernetes (managed service).
*   **Monitoring & Logging:** Railway's built-in tools + Sentry (for error tracking) + potentially a dedicated APM tool.
*   **CI/CD:** Railway's built-in Git deployment or GitHub Actions integrated with Railway.

## Observability & Agent Management

*   **Agent Workflow Definition:** YAML or JSON Schema (for defining agent teams, roles, and interactions).
*   **Observability Layer:** Built-in logging/tracing within the orchestration framework (e.g., AgentFlow's traces) + custom dashboards (if needed).

## Security & Compliance

*   **Authentication:** JWT (JSON Web Tokens) or OAuth 2.0
*   **API Security:** Input validation, rate limiting, WAF (Web Application Firewall).
*   **Data Encryption:** At rest (provided by Railway/Postgres) and in transit (TLS).
*   **Secrets Management:** Railway Environment Variables / HashiCorp Vault (if complexity demands).

## Development & Utilities

*   **Package Management:** Poetry (Python), npm/yarn/pnpm (Node.js)
*   **Linting:** Ruff (Python), ESLint (JavaScript/TypeScript)
*   **Formatting:** Black (Python), Prettier (JavaScript/TypeScript)
*   **Testing:** Pytest (Python), Jest/Vitest (JavaScript)

```

---

### Edit your code style

**File:** `~/.agent-os/standards/code-style.md`

```markdown
# Z2 Code Style Guide

This document outlines the coding conventions and style preferences for Z2 to ensure consistency and readability.

## Python

*   **Indentation:** 4 spaces (no tabs).
*   **Line Length:** 88 characters (default Black limit, allows for ~10% buffer before 100 chars).
*   **Naming Conventions:**
    *   Variables, functions, methods: `snake_case`
    *   Classes, Exceptions: `PascalCase`
    *   Constants: `UPPER_SNAKE_CASE`
    *   Modules, Packages: `snake_case`
*   **String Quotes:** Double quotes (`"`) preferred, single quotes (`'`) acceptable for short strings or internal quoting.
*   **Type Hints:** Mandatory for function signatures and complex variables.
*   **Docstrings:** Follow Google Python Style Guide format or NumPy style. Required for modules, classes, and public functions.
*   **Imports:**
    *   Standard library first, then third-party, then local imports.
    *   Alphabetized within each group.
    *   Use explicit imports (`from module import specific_function`) when possible.
    *   Avoid wildcard imports (`from module import *`).
*   **Comments:** Use sparingly; code should be self-explanatory. Comments explain *why*, not *what*.
*   **Formatting Tool:** Black (enforced via pre-commit hook or CI).
*   **Linter:** Ruff (configured for performance and common Python standards).

## JavaScript / TypeScript (React)

*   **Indentation:** 2 spaces (standard for JS/TS).
*   **Semicolons:** No (rely on ASI - Automatic Semicolon Insertion, common in modern JS).
*   **Naming Conventions:**
    *   Variables, functions: `camelCase`
    *   React Components: `PascalCase`
    *   Constants: `UPPER_SNAKE_CASE` or `camelCase` (context dependent, prefer `UPPER_SNAKE_CASE` for truly global constants).
    *   Interfaces/Types (TS): `PascalCase` (e.g., `interface UserSettings {}`).
*   **Quotes:** Double quotes (`"`), unless single quotes avoid escaping.
*   **File Extensions:** `.tsx` for files with JSX, `.ts` otherwise.
*   **Component Structure:** Functional components with hooks preferred over class components.
*   **Formatting Tool:** Prettier (enforced via pre-commit hook or CI). Configuration via `.prettierrc`.
*   **Linter:** ESLint (configured for React and TypeScript best practices). Configuration via `.eslintrc`.

## General File Organization

*   **Backend (FastAPI):**
    *   `app/`
        *   `main.py` (app instantiation)
        *   `api/` (API routes)
        *   `core/` (core logic, config, security)
        *   `models/` (database models)
        *   `schemas/` (Pydantic models for request/response)
        *   `database/` (database connection/session logic)
        *   `agents/` (Agent definitions, orchestration logic)
        *   `utils/` (utility functions)
        *   `tests/`
*   **Frontend (React):**
    *   `src/`
        *   `components/` (UI components)
        *   `pages/` (Page-level components/routing)
        *   `services/` (API client logic)
        *   `hooks/` (Custom React hooks)
        *   `types/` (TypeScript types/interfaces)
        *   `utils/` (Utility functions)
        *   `assets/` (Images, styles, etc.)
        *   `App.tsx`, `main.tsx`

```

---

### Edit your best practices

**File:** `~/.agent-os/standards/best-practices.md`

```markdown
# Z2 Best Practices

This document outlines the core principles and practices for developing Z2, focusing on quality, performance, and security.

## Development Philosophy

*   **User Intent Understanding:** Prioritize designing prompts, agent workflows, and UI interactions that accurately capture and translate user goals into executable plans. Invest in robust intent parsing.
*   **Adaptability at All Costs:** Build systems that can dynamically adjust workflows, select appropriate models/tools, and handle unexpected inputs gracefully to achieve the user's ultimate objective.
*   **Observability First:** Instrument agents and core components from the beginning. Log decisions, tool calls, state changes, and performance metrics to enable debugging and optimization.
*   **Modularity & Reusability:** Design agents, prompts, and components to be modular and reusable across different workflows or contexts.

## Testing

*   **Philosophy:** A balanced approach combining unit testing for core logic, integration testing for API endpoints and agent interactions, and end-to-end testing for critical user journeys.
*   **Unit Testing:** Pytest (Python), Jest/Vitest (JS). Aim for high coverage on business logic and core agent functions.
*   **Integration Testing:** Test interactions between services (e.g., backend API calling LLMs, database interactions, agent tool usage).
*   **Agent Testing:** Specific tests for agent workflows, including simulating various inputs and verifying goal completion or appropriate fallbacks.
*   **Prompt Testing:** Dedicated evaluation of prompts for accuracy, robustness, and potential failure modes. Consider using frameworks like Agenta for systematic prompt testing.

## Performance vs. Readability

*   **Readability is King:** Prioritize code clarity and maintainability. Complex optimizations should only be introduced if performance profiling identifies a clear bottleneck.
*   **Asynchronous Operations:** Leverage FastAPI's async capabilities and concurrent processing for I/O-bound tasks (like LLM calls) to improve responsiveness.
*   **Efficient Prompting:** Use shorter, structured prompts where possible (like Cluely) for cost/latency efficiency without sacrificing quality. Employ techniques like Few-Shot learning contextually.
*   **Caching:** Implement intelligent caching (e.g., Redis) for expensive computations or frequent LLM responses that are unlikely to change rapidly.
*   **Model Selection:** Dynamically choose models based on task complexity/cost requirements (e.g., GPT-4.1-mini for simple tasks, Claude 3.5 Sonnet for complex analysis).

## Security

*   **Input Sanitization:** Validate and sanitize all user inputs rigorously to prevent injection attacks (prompt injection, SQL injection, XSS).
*   **API Security:** Implement authentication (JWT/OAuth), enforce rate limiting, and use secure headers.
*   **LLM Security:**
    *   Employ guardrails and filters to prevent jailbreaking, toxic content generation, and PII leakage.
    *   Be cautious with user data sent to LLMs; consider scrubbing or anonymization where necessary.
    *   Monitor for adversarial prompts.
*   **Data Protection:** Encrypt sensitive data at rest and in transit. Minimize the collection and retention of PII.
*   **Secrets Management:** Never hardcode API keys or secrets. Use environment variables managed securely by the platform (Railway).
*   **Compliance Awareness:** Be mindful of standards like GDPR, ISO/IEC 42001, and NIST AI RMF during design and implementation.

## Deployment & Operations

*   **Infrastructure as Code:** Define deployment configurations declaratively (Dockerfile, Railway config).
*   **Continuous Integration/Deployment:** Automate testing and deployment pipelines.
*   **Monitoring & Alerting:** Set up monitoring for application health, LLM API usage/costs, error rates, and performance metrics. Configure alerts for anomalies.
*   **Scalability Planning:** Design stateless components where possible. Plan for horizontal scaling of the application and agent workers.

```

---

With these standards defined, we can now proceed with planning the product.

@plan-product
I want to build Z2: An intuitive, highly adaptable, and orchestrated AI workforce platform. It allows users (developers and non-developers) to define goals, and the system dynamically plans, selects appropriate models/tools (swarming, teams, orchestrated workflows), and executes tasks autonomously to completion.
Key features:
1.  Dynamic Prompt Generation & Adaptation: System automatically crafts and refines prompts based on context and goal progress.
2.  Multi-Agent Orchestration: Create, manage, and deploy swarms/teams of specialized AI agents (researcher, writer, coder, planner, executor) that collaborate.
3.  Goal-Oriented Execution: Users define a high-level goal, the system breaks it down, plans actions, executes via agents, and adapts the plan as needed until the goal is met or clarified.
4.  Intuitive UX: Point-and-shoot interface for non-developers; powerful configuration for developers. System deeply understands user intent.
5.  Broad Model Integration: Seamlessly integrates with top LLMs (OpenAI, Anthropic, Google, Groq, Perplexity) via standardized APIs.
6.  Observability & Control: Real-time dashboards showing agent activity, decisions, resource usage. Allow user intervention/steering.
Target users: Developers needing rapid AI prototyping/deployment and anyone wanting an autonomous AI workforce.
Tech stack: Use the standards defined in `~/.agent-os/standards/tech-stack.md`. Primary hosting on Railway.com. Leverage the API documentation from https://ai1docs.abacusai.app/ for integrations.
