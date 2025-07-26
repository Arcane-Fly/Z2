"""
Multi-Agent Orchestration Framework (MAOF) Core Module

The MAOF handles agent definition, workflow orchestration, collaborative reasoning,
and goal-oriented task execution as specified in the Z2 requirements.
"""

import asyncio
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.agents.die import ContextualMemory, DynamicIntelligenceEngine
from app.agents.mil import LLMRequest, ModelIntegrationLayer, RoutingPolicy

logger = structlog.get_logger(__name__)


class AgentRole(Enum):
    """Predefined agent roles for specialization."""

    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    CODER = "coder"
    REVIEWER = "reviewer"
    PLANNER = "planner"
    EXECUTOR = "executor"
    COORDINATOR = "coordinator"
    VALIDATOR = "validator"


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class WorkflowStatus(Enum):
    """Workflow execution status."""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STOPPING = "stopping"


@dataclass
class Tool:
    """Definition of a tool that agents can use."""

    name: str
    description: str
    function: Callable
    parameters: dict[str, Any]
    required_permissions: list[str] = field(default_factory=list)


@dataclass
class AgentDefinition:
    """Complete definition of an AI agent."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    role: AgentRole = AgentRole.EXECUTOR
    description: str = ""
    system_prompt: str = ""

    # Capabilities and configuration
    tools: list[Tool] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    knowledge_domains: list[str] = field(default_factory=list)

    # Model preferences
    preferred_models: list[str] = field(default_factory=list)
    model_routing_policy: Optional[RoutingPolicy] = None

    # Behavior settings
    temperature: float = 0.7
    max_tokens: int = 4096
    max_iterations: int = 10
    timeout_seconds: int = 300

    # Collaboration settings
    can_delegate: bool = True
    can_request_help: bool = True
    trust_level: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "tools": [tool.name for tool in self.tools],
            "skills": self.skills,
            "knowledge_domains": self.knowledge_domains,
            "preferred_models": self.preferred_models,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_iterations": self.max_iterations,
            "timeout_seconds": self.timeout_seconds,
            "can_delegate": self.can_delegate,
            "can_request_help": self.can_request_help,
            "trust_level": self.trust_level,
        }


@dataclass
class Task:
    """Individual task within a workflow."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    assigned_agent: Optional[UUID] = None
    dependencies: list[UUID] = field(default_factory=list)

    # Task configuration
    input_data: dict[str, Any] = field(default_factory=dict)
    expected_output: dict[str, Any] = field(default_factory=dict)
    success_criteria: list[str] = field(default_factory=list)

    # Execution state
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    output_data: dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    # Performance metrics
    tokens_used: int = 0
    cost_usd: float = 0.0
    iterations: int = 0

    # Cancellation support
    _cancel_event: Optional[asyncio.Event] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize internal state."""
        self._cancel_event = asyncio.Event()

    def request_cancellation(self):
        """Request task cancellation."""
        if self._cancel_event:
            self._cancel_event.set()
        self.status = TaskStatus.CANCELLED

    def is_cancellation_requested(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancel_event and self._cancel_event.is_set()

    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries and self.status == TaskStatus.FAILED


@dataclass
class WorkflowDefinition:
    """Complete workflow definition with agent team and execution graph."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    goal: str = ""

    # Team composition
    agents: list[AgentDefinition] = field(default_factory=list)
    coordinator_agent: Optional[UUID] = None

    # Task graph
    tasks: list[Task] = field(default_factory=list)
    task_dependencies: dict[UUID, list[UUID]] = field(default_factory=dict)

    # Execution configuration
    max_duration_seconds: int = 3600
    max_cost_usd: float = 10.0
    require_human_approval: bool = False

    # Collaboration rules
    debate_enabled: bool = False
    consensus_threshold: float = 0.7
    max_debate_rounds: int = 3

    # State management
    status: WorkflowStatus = WorkflowStatus.DRAFT
    current_tasks: list[UUID] = field(default_factory=list)
    completed_tasks: list[UUID] = field(default_factory=list)
    failed_tasks: list[UUID] = field(default_factory=list)
    cancelled_tasks: list[UUID] = field(default_factory=list)

    # Execution metadata
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0

    # Cancellation support
    _stop_event: Optional[asyncio.Event] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize internal state."""
        self._stop_event = asyncio.Event()

    def request_stop(self):
        """Request workflow stop."""
        if self._stop_event:
            self._stop_event.set()
        self.status = WorkflowStatus.STOPPING

    def is_stop_requested(self) -> bool:
        """Check if stop has been requested."""
        return self._stop_event and self._stop_event.is_set()

    def get_task_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None


class Agent:
    """Runtime agent instance with execution capabilities."""

    def __init__(
        self,
        definition: AgentDefinition,
        die: DynamicIntelligenceEngine,
        mil: ModelIntegrationLayer,
    ):
        self.definition = definition
        self.die = die
        self.mil = mil
        self.memory = ContextualMemory(short_term={}, long_term={}, summary={})
        self.execution_history: list[dict[str, Any]] = []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def execute_task(self, task: Task, context: dict[str, Any]) -> dict[str, Any]:
        """Execute a specific task with retry logic."""
        logger.info(
            "Starting task execution",
            agent=self.definition.name,
            task=task.name,
            task_id=str(task.id),
            retry_count=task.retry_count,
        )

        # Check for cancellation before starting
        if task.is_cancellation_requested():
            task.status = TaskStatus.CANCELLED
            raise asyncio.CancelledError(f"Task {task.name} was cancelled")

        start_time = time.time()
        task.start_time = start_time
        task.status = TaskStatus.IN_PROGRESS

        try:
            # Generate contextual prompt for the task
            prompt = self._generate_task_prompt(task, context)

            # Create LLM request
            request = LLMRequest(
                prompt=prompt,
                max_tokens=self.definition.max_tokens,
                temperature=self.definition.temperature,
            )

            # Use routing policy if defined
            policy = self.definition.model_routing_policy

            # Generate response with timeout
            response = await asyncio.wait_for(
                self.mil.generate_response(request, policy),
                timeout=self.definition.timeout_seconds
            )

            # Check for cancellation after LLM call
            if task.is_cancellation_requested():
                task.status = TaskStatus.CANCELLED
                raise asyncio.CancelledError(f"Task {task.name} was cancelled")

            # Process and validate response
            result = self._process_response(response, task)

            # Update task state
            task.end_time = time.time()
            task.status = TaskStatus.COMPLETED
            task.output_data = result
            task.tokens_used = response.tokens_used
            task.cost_usd = response.cost_usd
            task.iterations = task.retry_count + 1

            # Update agent memory
            self._update_memory(task, response, result)

            logger.info(
                "Completed task execution",
                agent=self.definition.name,
                task=task.name,
                duration=task.end_time - task.start_time,
                tokens=task.tokens_used,
                cost=task.cost_usd,
                retry_count=task.retry_count,
            )

            return result

        except asyncio.CancelledError:
            task.end_time = time.time()
            task.status = TaskStatus.CANCELLED
            logger.info(
                "Task execution cancelled",
                agent=self.definition.name,
                task=task.name,
            )
            raise

        except asyncio.TimeoutError:
            task.end_time = time.time()
            task.status = TaskStatus.FAILED
            task.error_message = f"Task execution timed out after {self.definition.timeout_seconds}s"
            
            logger.error(
                "Task execution timed out",
                agent=self.definition.name,
                task=task.name,
                timeout=self.definition.timeout_seconds,
            )
            raise

        except Exception as e:
            task.end_time = time.time()
            task.retry_count += 1
            
            if task.can_retry():
                task.status = TaskStatus.RETRYING
                logger.warning(
                    "Task execution failed, retrying",
                    agent=self.definition.name,
                    task=task.name,
                    error=str(e),
                    retry_count=task.retry_count,
                    max_retries=task.max_retries,
                )
                raise  # Let tenacity handle the retry
            else:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                logger.error(
                    "Task execution failed permanently",
                    agent=self.definition.name,
                    task=task.name,
                    error=str(e),
                    retry_count=task.retry_count,
                )
                raise

    def _generate_task_prompt(self, task: Task, context: dict[str, Any]) -> str:
        """Generate a contextual prompt for the task."""

        # Prepare input data with safe formatting
        input_data_str = ""
        if task.input_data:
            try:
                # Try to format with context variables, fall back to safe representation
                formatted_input = {}
                for key, value in task.input_data.items():
                    if isinstance(value, str) and "{" in value and "}" in value:
                        # Try to format with context, fall back to removing braces
                        try:
                            formatted_input[key] = value.format(**context)
                        except (KeyError, ValueError):
                            # Remove template braces for safe representation
                            formatted_input[key] = value.replace("{", "").replace("}", "")
                    else:
                        formatted_input[key] = value
                input_data_str = json.dumps(formatted_input, indent=2)
            except Exception:
                input_data_str = json.dumps(task.input_data, indent=2, default=str)

        # Use DIE to generate dynamic prompt
        template_variables = {
            "agent_role": self.definition.role.value,
            "task_description": task.description,
            "input_data": input_data_str,
            "expected_output": json.dumps(task.expected_output, indent=2),
            "success_criteria": "\n".join(
                f"- {criteria}" for criteria in task.success_criteria
            ),
            "context": json.dumps(context, indent=2),
            "output_format": "JSON",
        }

        # Select appropriate template based on agent role
        template_name = self._get_template_for_role(self.definition.role)

        # Determine target model
        target_model = self._select_model()

        return self.die.generate_contextual_prompt(
            template_name=template_name,
            variables=template_variables,
            agent_role=self.definition.role.value,
            target_model=target_model,
        )

    def _get_template_for_role(self, role: AgentRole) -> str:
        """Get appropriate prompt template for agent role."""
        role_templates = {
            AgentRole.RESEARCHER: "research",
            AgentRole.CODER: "code",
            AgentRole.WRITER: "general",
            AgentRole.ANALYST: "general",
            AgentRole.REVIEWER: "general",
            AgentRole.PLANNER: "general",
            AgentRole.EXECUTOR: "general",
            AgentRole.COORDINATOR: "general",
            AgentRole.VALIDATOR: "general",
        }

        return role_templates.get(role, "general")

    def _select_model(self) -> str:
        """Select appropriate model for this agent."""
        if self.definition.preferred_models:
            return self.definition.preferred_models[0]

        # Default model selection based on role
        role_models = {
            AgentRole.RESEARCHER: "openai/gpt-4.1",
            AgentRole.CODER: "openai/gpt-4.1",
            AgentRole.ANALYST: "openai/gpt-4.1-mini",
            AgentRole.WRITER: "openai/gpt-4.1-mini",
            AgentRole.REVIEWER: "anthropic/claude-3.5-sonnet",
            AgentRole.PLANNER: "openai/gpt-4.1",
            AgentRole.EXECUTOR: "groq/llama-3.3-70b-versatile",
            AgentRole.COORDINATOR: "openai/gpt-4.1",
            AgentRole.VALIDATOR: "anthropic/claude-3.5-sonnet",
        }

        return role_models.get(self.definition.role, "openai/gpt-4.1-mini")

    def _process_response(self, response, task: Task) -> dict[str, Any]:
        """Process and validate LLM response."""
        try:
            # Try to parse as JSON first
            if response.content.strip().startswith("{"):
                result = json.loads(response.content)
            else:
                # Wrap text response in result structure
                result = {
                    "output": response.content,
                    "success": True,
                    "metadata": {
                        "model_used": response.model_used,
                        "tokens_used": response.tokens_used,
                        "latency_ms": response.latency_ms,
                    },
                }

            return result

        except json.JSONDecodeError:
            # Fallback to text response
            return {
                "output": response.content,
                "success": True,
                "format": "text",
                "metadata": {
                    "model_used": response.model_used,
                    "tokens_used": response.tokens_used,
                    "latency_ms": response.latency_ms,
                },
            }

    def _update_memory(self, task: Task, response, result: dict[str, Any]) -> None:
        """Update agent's contextual memory."""

        # Update execution history
        execution_record = {
            "task_id": str(task.id),
            "task_name": task.name,
            "timestamp": time.time(),
            "input": task.input_data,
            "output": result,
            "success": task.status == TaskStatus.COMPLETED,
            "tokens_used": response.tokens_used,
            "cost_usd": response.cost_usd,
            "model_used": response.model_used,
        }

        self.execution_history.append(execution_record)

        # Update DIE contextual flow
        self.die.update_interaction_context(
            user_input=task.description,
            agent_response=response.content,
            metadata={
                "timestamp": time.time(),
                "success": task.status == TaskStatus.COMPLETED,
                "tokens_used": response.tokens_used,
                "model_used": response.model_used,
                "agent_role": self.definition.role.value,
            },
        )


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflow execution."""

    def __init__(self, die: DynamicIntelligenceEngine, mil: ModelIntegrationLayer):
        self.die = die
        self.mil = mil
        self.active_workflows: dict[UUID, WorkflowDefinition] = {}
        self.agent_pool: dict[UUID, Agent] = {}
        self.task_futures: dict[UUID, asyncio.Task] = {}
        self._orchestration_lock = asyncio.Lock()

    async def execute_workflow(self, workflow: WorkflowDefinition) -> dict[str, Any]:
        """Execute a complete workflow with multiple agents."""

        logger.info(
            "Starting workflow execution",
            workflow=workflow.name,
            workflow_id=str(workflow.id),
            agents=len(workflow.agents),
            tasks=len(workflow.tasks),
        )

        async with self._orchestration_lock:
            workflow.status = WorkflowStatus.RUNNING
            workflow.start_time = time.time()
            self.active_workflows[workflow.id] = workflow

        try:
            # Initialize agents
            self._initialize_workflow_agents(workflow)

            # Execute workflow with enhanced coordination
            result = await self._execute_workflow_with_coordination(workflow)

            # Finalize workflow
            workflow.status = WorkflowStatus.COMPLETED
            workflow.end_time = time.time()

            logger.info(
                "Completed workflow execution",
                workflow=workflow.name,
                duration=workflow.end_time - workflow.start_time,
                total_tokens=workflow.total_tokens_used,
                total_cost=workflow.total_cost_usd,
                completed_tasks=len(workflow.completed_tasks),
                failed_tasks=len(workflow.failed_tasks),
                cancelled_tasks=len(workflow.cancelled_tasks),
            )

            return result

        except asyncio.CancelledError:
            await self._handle_workflow_cancellation(workflow)
            raise

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.end_time = time.time()

            logger.error(
                "Workflow execution failed",
                workflow=workflow.name,
                error=str(e),
                duration=workflow.end_time - workflow.start_time if workflow.end_time else None,
            )

            # Cancel any running tasks
            await self._cancel_workflow_tasks(workflow)
            raise

        finally:
            # Cleanup
            await self._cleanup_workflow(workflow)

    async def _execute_workflow_with_coordination(
        self, workflow: WorkflowDefinition
    ) -> dict[str, Any]:
        """Execute workflow with enhanced coordination and event loop."""
        
        # Build task execution plan
        execution_plan = self._build_execution_plan(workflow)
        
        # Shared context for all tasks
        workflow_context = {
            "workflow_id": str(workflow.id),
            "workflow_goal": workflow.goal,
            "start_time": workflow.start_time,
            "agents": {str(agent.id): agent.name for agent in workflow.agents},
        }

        # Event loop for coordinated execution
        completed_tasks = set()
        failed_tasks = set()
        cancelled_tasks = set()
        
        while execution_plan and not workflow.is_stop_requested():
            # Check for cost and time limits
            if await self._check_workflow_limits(workflow):
                break

            # Get ready tasks for this iteration
            ready_tasks = self._get_ready_tasks_from_plan(
                execution_plan, completed_tasks, failed_tasks
            )

            if not ready_tasks and not self.task_futures:
                # No tasks ready and none running - check for deadlock
                if execution_plan:
                    logger.error(
                        "Workflow deadlock detected",
                        workflow=workflow.name,
                        remaining_tasks=len(execution_plan),
                    )
                    break
                else:
                    # All tasks completed
                    break

            # Start ready tasks
            await self._start_ready_tasks(ready_tasks, workflow, workflow_context)

            # Wait for task completion or timeout
            await self._coordinate_task_execution(workflow)

            # Process completed tasks
            completed_this_round, failed_this_round, cancelled_this_round = (
                await self._process_completed_tasks(workflow)
            )

            completed_tasks.update(completed_this_round)
            failed_tasks.update(failed_this_round)
            cancelled_tasks.update(cancelled_this_round)

            # Remove completed/failed tasks from execution plan
            execution_plan = [
                task for task in execution_plan 
                if task.id not in (completed_tasks | failed_tasks | cancelled_tasks)
            ]

            # Short delay to prevent busy loop
            await asyncio.sleep(0.1)

        # Wait for any remaining tasks to finish
        if self.task_futures:
            await self._wait_for_remaining_tasks(workflow)

        # Collect final results
        return self._collect_workflow_results(workflow)

    def _build_execution_plan(self, workflow: WorkflowDefinition) -> list[Task]:
        """Build task execution plan based on dependencies."""
        # Start with all tasks
        execution_plan = workflow.tasks.copy()
        
        # Sort by dependencies (tasks with fewer dependencies first)
        def dependency_count(task):
            return len(task.dependencies)
        
        execution_plan.sort(key=dependency_count)
        return execution_plan

    def _get_ready_tasks_from_plan(
        self, execution_plan: list[Task], completed: set, failed: set
    ) -> list[Task]:
        """Get tasks that are ready to execute."""
        ready = []
        
        for task in execution_plan:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are satisfied
                dependencies_satisfied = all(
                    dep_id in completed for dep_id in task.dependencies
                )
                
                # Check if any dependency failed
                dependencies_failed = any(
                    dep_id in failed for dep_id in task.dependencies
                )
                
                if dependencies_satisfied and not dependencies_failed:
                    ready.append(task)
        
        return ready

    async def _start_ready_tasks(
        self, ready_tasks: list[Task], workflow: WorkflowDefinition, context: dict[str, Any]
    ) -> None:
        """Start execution of ready tasks."""
        for task in ready_tasks:
            if task.id not in self.task_futures:
                # Create task execution coroutine
                task_coro = self._execute_task_with_tracking(task, workflow, context)
                
                # Schedule task execution
                future = asyncio.create_task(task_coro)
                self.task_futures[task.id] = future
                workflow.current_tasks.append(task.id)
                
                logger.debug(
                    "Started task execution",
                    task=task.name,
                    workflow=workflow.name,
                    dependencies=len(task.dependencies),
                )

    async def _coordinate_task_execution(self, workflow: WorkflowDefinition) -> None:
        """Coordinate running tasks with intelligent waiting."""
        if not self.task_futures:
            return

        # Wait for at least one task to complete or a timeout
        try:
            done, pending = await asyncio.wait(
                self.task_futures.values(),
                timeout=1.0,  # Check every second
                return_when=asyncio.FIRST_COMPLETED
            )
        except Exception as e:
            logger.error(
                "Error in task coordination",
                workflow=workflow.name,
                error=str(e),
            )

    async def _process_completed_tasks(
        self, workflow: WorkflowDefinition
    ) -> tuple[set[UUID], set[UUID], set[UUID]]:
        """Process completed tasks and update workflow state."""
        completed = set()
        failed = set()
        cancelled = set()

        # Check all task futures
        finished_task_ids = []
        
        for task_id, future in self.task_futures.items():
            if future.done():
                finished_task_ids.append(task_id)
                task = workflow.get_task_by_id(task_id)
                
                if task:
                    try:
                        # Get the result (this will raise if the task failed)
                        await future
                        
                        if task.status == TaskStatus.COMPLETED:
                            completed.add(task_id)
                            workflow.completed_tasks.append(task_id)
                        elif task.status == TaskStatus.CANCELLED:
                            cancelled.add(task_id)
                            workflow.cancelled_tasks.append(task_id)
                        else:
                            failed.add(task_id)
                            workflow.failed_tasks.append(task_id)
                            
                    except asyncio.CancelledError:
                        cancelled.add(task_id)
                        workflow.cancelled_tasks.append(task_id)
                        task.status = TaskStatus.CANCELLED
                        
                    except Exception as e:
                        failed.add(task_id)
                        workflow.failed_tasks.append(task_id)
                        task.status = TaskStatus.FAILED
                        task.error_message = str(e)
                        
                        logger.error(
                            "Task failed during execution",
                            task=task.name,
                            workflow=workflow.name,
                            error=str(e),
                        )

        # Remove finished tasks from tracking
        for task_id in finished_task_ids:
            if task_id in self.task_futures:
                del self.task_futures[task_id]
            if task_id in workflow.current_tasks:
                workflow.current_tasks.remove(task_id)

        return completed, failed, cancelled

    async def _check_workflow_limits(self, workflow: WorkflowDefinition) -> bool:
        """Check if workflow has exceeded time or cost limits."""
        if not workflow.start_time:
            return False

        # Check time limit
        elapsed = time.time() - workflow.start_time
        if elapsed > workflow.max_duration_seconds:
            logger.warning(
                "Workflow exceeded time limit",
                workflow=workflow.name,
                elapsed=elapsed,
                limit=workflow.max_duration_seconds,
            )
            workflow.request_stop()
            return True

        # Check cost limit - be more aggressive about stopping
        if workflow.total_cost_usd >= workflow.max_cost_usd:
            logger.warning(
                "Workflow exceeded cost limit",
                workflow=workflow.name,
                cost=workflow.total_cost_usd,
                limit=workflow.max_cost_usd,
            )
            workflow.request_stop()
            return True

        return False

    async def _cancel_workflow_tasks(self, workflow: WorkflowDefinition) -> None:
        """Cancel all running tasks in the workflow."""
        # Cancel all task futures
        for task_id, future in self.task_futures.items():
            if not future.done():
                future.cancel()

        # Request cancellation for all tasks
        for task in workflow.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.RETRYING]:
                task.request_cancellation()

        # Wait for cancellations to complete
        if self.task_futures:
            await asyncio.gather(*self.task_futures.values(), return_exceptions=True)

    async def _handle_workflow_cancellation(self, workflow: WorkflowDefinition) -> None:
        """Handle workflow cancellation gracefully."""
        workflow.status = WorkflowStatus.CANCELLED
        workflow.end_time = time.time()
        
        await self._cancel_workflow_tasks(workflow)
        
        logger.info(
            "Workflow cancelled",
            workflow=workflow.name,
            duration=workflow.end_time - workflow.start_time if workflow.start_time else None,
        )

    async def _wait_for_remaining_tasks(self, workflow: WorkflowDefinition) -> None:
        """Wait for any remaining tasks to finish."""
        if self.task_futures:
            logger.debug(
                "Waiting for remaining tasks",
                workflow=workflow.name,
                remaining=len(self.task_futures),
            )
            
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.task_futures.values(), return_exceptions=True),
                    timeout=30.0  # 30 second grace period
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "Timeout waiting for remaining tasks",
                    workflow=workflow.name,
                )
                # Force cancel remaining tasks
                for future in self.task_futures.values():
                    if not future.done():
                        future.cancel()

    async def _cleanup_workflow(self, workflow: WorkflowDefinition) -> None:
        """Clean up workflow resources."""
        # Remove from active workflows
        if workflow.id in self.active_workflows:
            del self.active_workflows[workflow.id]

        # Clean up agent pool entries for this workflow
        workflow_agent_ids = {agent.id for agent in workflow.agents}
        for agent_id in list(self.agent_pool.keys()):
            if agent_id in workflow_agent_ids:
                del self.agent_pool[agent_id]

        # Clear task futures
        self.task_futures.clear()

    def _collect_workflow_results(self, workflow: WorkflowDefinition) -> dict[str, Any]:
        """Collect and format workflow execution results."""
        results = {}
        
        for task in workflow.tasks:
            if task.status == TaskStatus.COMPLETED:
                results[task.name] = task.output_data

        return {
            "status": "completed" if not workflow.failed_tasks else "partial_failure",
            "completed_tasks": len(workflow.completed_tasks),
            "failed_tasks": len(workflow.failed_tasks),
            "cancelled_tasks": len(workflow.cancelled_tasks),
            "total_tokens": workflow.total_tokens_used,
            "total_cost": workflow.total_cost_usd,
            "execution_time": (workflow.end_time - workflow.start_time) if workflow.end_time and workflow.start_time else None,
            "results": results,
        }

    def _initialize_workflow_agents(self, workflow: WorkflowDefinition) -> None:
        """Initialize all agents for the workflow."""

        for agent_def in workflow.agents:
            agent = Agent(agent_def, self.die, self.mil)
            self.agent_pool[agent_def.id] = agent

            logger.debug(
                "Initialized agent",
                agent=agent_def.name,
                role=agent_def.role.value,
                agent_id=str(agent_def.id),
            )

    async def _execute_task_with_tracking(
        self,
        task: Task,
        workflow: WorkflowDefinition,
        context: dict[str, Any],
    ) -> None:
        """Execute a task and update workflow tracking."""

        try:
            # Get assigned agent
            if not task.assigned_agent:
                task.assigned_agent = self._auto_assign_agent(task, workflow)

            agent = self.agent_pool[task.assigned_agent]

            # Execute task with enhanced error handling
            result = await agent.execute_task(task, context)

            # Update workflow metrics
            workflow.total_tokens_used += task.tokens_used
            workflow.total_cost_usd += task.cost_usd

            # Log successful completion
            logger.info(
                "Task completed successfully",
                task=task.name,
                workflow=workflow.name,
                tokens=task.tokens_used,
                cost=task.cost_usd,
                duration=task.end_time - task.start_time if task.end_time and task.start_time else None,
            )

        except asyncio.CancelledError:
            logger.info(
                "Task execution cancelled",
                task=task.name,
                workflow=workflow.name,
            )
            task.status = TaskStatus.CANCELLED
            raise

        except Exception as e:
            logger.error(
                "Task execution failed in workflow",
                task=task.name,
                workflow=workflow.name,
                error=str(e),
                retry_count=task.retry_count,
            )
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            raise

    def _get_ready_tasks(self, tasks: list[Task]) -> list[UUID]:
        """Get tasks that are ready to execute (dependencies satisfied)."""

        completed_task_ids = {
            task.id for task in tasks if task.status == TaskStatus.COMPLETED
        }

        ready = []
        for task in tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                dependencies_satisfied = all(
                    dep_id in completed_task_ids for dep_id in task.dependencies
                )

                if dependencies_satisfied:
                    ready.append(task.id)

        return ready

    def _auto_assign_agent(self, task: Task, workflow: WorkflowDefinition) -> UUID:
        """Automatically assign the best agent for a task."""

        available_agents = workflow.agents

        if not available_agents:
            raise ValueError("No agents available for task assignment")

        # Enhanced assignment logic based on agent capabilities
        best_agent = None
        best_score = -1

        for agent in available_agents:
            score = self._calculate_agent_task_score(agent, task)
            if score > best_score:
                best_score = score
                best_agent = agent

        if best_agent:
            logger.debug(
                "Assigned task to agent",
                task=task.name,
                agent=best_agent.name,
                role=best_agent.role.value,
                score=best_score,
            )
            return best_agent.id

        # Fallback to first available agent
        return available_agents[0].id

    def _calculate_agent_task_score(self, agent: AgentDefinition, task: Task) -> float:
        """Calculate how well an agent matches a task."""
        score = 0.0

        # Base score from trust level
        score += agent.trust_level * 0.3

        # Score based on role matching (simple keyword matching)
        task_lower = (task.name + " " + task.description).lower()
        role_keywords = {
            AgentRole.RESEARCHER: ["research", "analyze", "investigate", "find", "gather"],
            AgentRole.CODER: ["code", "implement", "develop", "program", "script"],
            AgentRole.WRITER: ["write", "document", "report", "explain", "summarize"],
            AgentRole.ANALYST: ["analyze", "evaluate", "assess", "review", "examine"],
            AgentRole.REVIEWER: ["review", "check", "validate", "verify", "audit"],
            AgentRole.PLANNER: ["plan", "design", "strategy", "organize", "structure"],
            AgentRole.EXECUTOR: ["execute", "run", "perform", "do", "complete"],
            AgentRole.COORDINATOR: ["coordinate", "manage", "organize", "lead"],
            AgentRole.VALIDATOR: ["validate", "test", "verify", "confirm", "check"],
        }

        keywords = role_keywords.get(agent.role, [])
        for keyword in keywords:
            if keyword in task_lower:
                score += 0.2

        # Score based on skills matching
        for skill in agent.skills:
            if skill.lower() in task_lower:
                score += 0.1

        # Score based on knowledge domains
        for domain in agent.knowledge_domains:
            if domain.lower() in task_lower:
                score += 0.15

        return score


class MultiAgentOrchestrationFramework:
    """Main MAOF class that coordinates all orchestration components."""

    def __init__(self):
        self.die = DynamicIntelligenceEngine()
        self.mil = ModelIntegrationLayer()
        self.orchestrator = WorkflowOrchestrator(self.die, self.mil)
        self.workflow_templates: dict[str, WorkflowDefinition] = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """Initialize default workflow templates."""

        # Research and Analysis Workflow
        research_workflow = self._create_research_workflow_template()
        self.workflow_templates["research_analysis"] = research_workflow

        # Code Development Workflow
        code_workflow = self._create_code_development_template()
        self.workflow_templates["code_development"] = code_workflow

        logger.info(
            "Initialized default workflow templates", count=len(self.workflow_templates)
        )

    def _create_research_workflow_template(self) -> WorkflowDefinition:
        """Create a research and analysis workflow template."""

        # Define agents
        researcher = AgentDefinition(
            name="Research Specialist",
            role=AgentRole.RESEARCHER,
            description="Gathers and analyzes information from various sources",
            system_prompt="You are a research specialist. Gather comprehensive information and provide detailed analysis.",
            skills=["web_search", "data_analysis", "source_verification"],
            knowledge_domains=[
                "general_knowledge",
                "current_events",
                "academic_research",
            ],
        )

        analyst = AgentDefinition(
            name="Data Analyst",
            role=AgentRole.ANALYST,
            description="Analyzes data and extracts insights",
            system_prompt="You are a data analyst. Process information and extract meaningful insights.",
            skills=[
                "statistical_analysis",
                "pattern_recognition",
                "insight_generation",
            ],
        )

        writer = AgentDefinition(
            name="Report Writer",
            role=AgentRole.WRITER,
            description="Creates comprehensive reports and summaries",
            system_prompt="You are a report writer. Create clear, structured, and comprehensive reports.",
            skills=["technical_writing", "report_formatting", "summarization"],
        )

        # Define tasks
        research_task = Task(
            name="Initial Research",
            description="Conduct comprehensive research on the given topic",
            input_data={"research_topic": "{research_topic}"},
            expected_output={
                "research_findings": "dict",
                "sources": "list",
                "key_insights": "list",
            },
            success_criteria=[
                "Multiple reliable sources identified",
                "Key findings clearly documented",
            ],
        )

        analysis_task = Task(
            name="Data Analysis",
            description="Analyze research findings and extract insights",
            dependencies=[research_task.id],
            expected_output={
                "analysis": "dict",
                "trends": "list",
                "recommendations": "list",
            },
            success_criteria=["Patterns identified", "Actionable insights provided"],
        )

        report_task = Task(
            name="Report Generation",
            description="Generate comprehensive final report",
            dependencies=[analysis_task.id],
            expected_output={"report": "string", "executive_summary": "string"},
            success_criteria=["Report is comprehensive", "Executive summary is clear"],
        )

        # Assign agents to tasks
        research_task.assigned_agent = researcher.id
        analysis_task.assigned_agent = analyst.id
        report_task.assigned_agent = writer.id

        return WorkflowDefinition(
            name="Research and Analysis Workflow",
            description="Comprehensive research, analysis, and reporting workflow",
            goal="Conduct thorough research and provide actionable insights",
            agents=[researcher, analyst, writer],
            tasks=[research_task, analysis_task, report_task],
            coordinator_agent=analyst.id,
            debate_enabled=True,
            max_duration_seconds=1800,  # 30 minutes
            max_cost_usd=5.0,
        )

    def _create_code_development_template(self) -> WorkflowDefinition:
        """Create a code development workflow template."""

        # Define agents
        planner = AgentDefinition(
            name="Technical Planner",
            role=AgentRole.PLANNER,
            description="Creates technical plans and architecture designs",
            system_prompt="You are a technical planner. Create detailed technical plans and architecture designs.",
            skills=["system_design", "architecture_planning", "requirement_analysis"],
        )

        coder = AgentDefinition(
            name="Software Developer",
            role=AgentRole.CODER,
            description="Implements code based on specifications",
            system_prompt="You are a software developer. Write clean, efficient, and well-documented code.",
            skills=["programming", "algorithm_implementation", "code_optimization"],
            preferred_models=["openai/gpt-4.1"],  # Better for code generation
        )

        reviewer = AgentDefinition(
            name="Code Reviewer",
            role=AgentRole.REVIEWER,
            description="Reviews code for quality and best practices",
            system_prompt="You are a code reviewer. Ensure code quality, security, and best practices.",
            skills=["code_review", "security_analysis", "performance_optimization"],
        )

        # Define tasks
        planning_task = Task(
            name="Technical Planning",
            description="Create technical plan and architecture",
            input_data={"requirements": "{code_requirements}"},
            expected_output={
                "plan": "dict",
                "architecture": "dict",
                "requirements": "list",
            },
        )

        implementation_task = Task(
            name="Code Implementation",
            description="Implement the planned solution",
            dependencies=[planning_task.id],
            input_data={"programming_language": "{programming_language}"},
            expected_output={
                "code": "string",
                "documentation": "string",
                "tests": "string",
            },
        )

        review_task = Task(
            name="Code Review",
            description="Review and validate the implementation",
            dependencies=[implementation_task.id],
            expected_output={"review": "dict", "issues": "list", "approved": "boolean"},
        )

        # Assign agents
        planning_task.assigned_agent = planner.id
        implementation_task.assigned_agent = coder.id
        review_task.assigned_agent = reviewer.id

        return WorkflowDefinition(
            name="Code Development Workflow",
            description="Complete code development with planning and review",
            goal="Develop high-quality, reviewed code solution",
            agents=[planner, coder, reviewer],
            tasks=[planning_task, implementation_task, review_task],
            coordinator_agent=planner.id,
            max_duration_seconds=3600,  # 1 hour
            max_cost_usd=8.0,
        )

    async def execute_goal_oriented_workflow(
        self,
        goal: str,
        template_name: Optional[str] = None,
        custom_agents: Optional[list[AgentDefinition]] = None,
        input_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Execute a goal-oriented workflow."""

        # Select or create workflow
        if template_name and template_name in self.workflow_templates:
            workflow = self.workflow_templates[template_name]
            workflow.goal = goal  # Update goal
            
            # Update task input data if provided
            if input_data:
                for task in workflow.tasks:
                    # Merge provided input data with task input data
                    task.input_data.update(input_data)
        else:
            # Create dynamic workflow based on goal
            workflow = await self._create_dynamic_workflow(goal, custom_agents, input_data)

        # Execute workflow
        return await self.orchestrator.execute_workflow(workflow)

    async def _create_dynamic_workflow(
        self,
        goal: str,
        custom_agents: Optional[list[AgentDefinition]] = None,
        input_data: Optional[dict[str, Any]] = None,
    ) -> WorkflowDefinition:
        """Create a dynamic workflow based on goal analysis."""

        # TODO: Implement intelligent workflow creation based on goal analysis
        # For now, use a simple default workflow

        if custom_agents:
            agents = custom_agents
        else:
            # Create default multi-purpose agent team
            agents = [
                AgentDefinition(
                    name="Goal Planner",
                    role=AgentRole.PLANNER,
                    description="Plans how to achieve the specified goal",
                ),
                AgentDefinition(
                    name="Task Executor",
                    role=AgentRole.EXECUTOR,
                    description="Executes planned tasks to achieve the goal",
                ),
                AgentDefinition(
                    name="Result Validator",
                    role=AgentRole.VALIDATOR,
                    description="Validates that the goal has been achieved",
                ),
            ]

        # Create simple sequential tasks
        plan_task = Task(
            name="Goal Planning",
            description=f"Create a plan to achieve: {goal}",
            assigned_agent=agents[0].id,
            input_data=input_data or {"goal": goal},
        )

        execute_task = Task(
            name="Goal Execution",
            description="Execute the planned approach",
            dependencies=[plan_task.id],
            assigned_agent=agents[1].id,
            input_data=input_data or {"goal": goal},
        )

        validate_task = Task(
            name="Goal Validation",
            description="Validate that the goal has been achieved",
            dependencies=[execute_task.id],
            assigned_agent=agents[2].id,
            input_data=input_data or {"goal": goal},
        )

        return WorkflowDefinition(
            name="Dynamic Goal-Oriented Workflow",
            description=f"Dynamic workflow to achieve: {goal}",
            goal=goal,
            agents=agents,
            tasks=[plan_task, execute_task, validate_task],
            max_duration_seconds=1800,
            max_cost_usd=10.0,
        )
