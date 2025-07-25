"""
Multi-Agent Orchestration Framework (MAOF) Core Module

The MAOF handles agent definition, workflow orchestration, collaborative reasoning,
and goal-oriented task execution as specified in the Z2 requirements.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
import asyncio
import json
import time
from uuid import UUID, uuid4
import structlog

from app.agents.die import DynamicIntelligenceEngine, ContextualMemory
from app.agents.mil import ModelIntegrationLayer, LLMRequest, RoutingPolicy


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


class WorkflowStatus(Enum):
    """Workflow execution status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Tool:
    """Definition of a tool that agents can use."""
    
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    required_permissions: List[str] = field(default_factory=list)


@dataclass
class AgentDefinition:
    """Complete definition of an AI agent."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    role: AgentRole = AgentRole.EXECUTOR
    description: str = ""
    system_prompt: str = ""
    
    # Capabilities and configuration
    tools: List[Tool] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    knowledge_domains: List[str] = field(default_factory=list)
    
    # Model preferences
    preferred_models: List[str] = field(default_factory=list)
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
    
    def to_dict(self) -> Dict[str, Any]:
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
    dependencies: List[UUID] = field(default_factory=list)
    
    # Task configuration
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    
    # Execution state
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Performance metrics
    tokens_used: int = 0
    cost_usd: float = 0.0
    iterations: int = 0


@dataclass
class WorkflowDefinition:
    """Complete workflow definition with agent team and execution graph."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    goal: str = ""
    
    # Team composition
    agents: List[AgentDefinition] = field(default_factory=list)
    coordinator_agent: Optional[UUID] = None
    
    # Task graph
    tasks: List[Task] = field(default_factory=list)
    task_dependencies: Dict[UUID, List[UUID]] = field(default_factory=dict)
    
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
    current_tasks: List[UUID] = field(default_factory=list)
    completed_tasks: List[UUID] = field(default_factory=list)
    failed_tasks: List[UUID] = field(default_factory=list)
    
    # Execution metadata
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0


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
        self.memory = ContextualMemory(
            short_term={},
            long_term={},
            summary={}
        )
        self.execution_history: List[Dict[str, Any]] = []
    
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task."""
        logger.info(
            "Starting task execution",
            agent=self.definition.name,
            task=task.name,
            task_id=str(task.id),
        )
        
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
            
            # Generate response
            response = await self.mil.generate_response(request, policy)
            
            # Process and validate response
            result = self._process_response(response, task)
            
            # Update task state
            task.end_time = time.time()
            task.status = TaskStatus.COMPLETED
            task.output_data = result
            task.tokens_used = response.tokens_used
            task.cost_usd = response.cost_usd
            task.iterations = 1  # Simple case for now
            
            # Update agent memory
            self._update_memory(task, response, result)
            
            logger.info(
                "Completed task execution",
                agent=self.definition.name,
                task=task.name,
                duration=task.end_time - task.start_time,
                tokens=task.tokens_used,
                cost=task.cost_usd,
            )
            
            return result
            
        except Exception as e:
            task.end_time = time.time()
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            
            logger.error(
                "Task execution failed",
                agent=self.definition.name,
                task=task.name,
                error=str(e),
            )
            
            raise
    
    def _generate_task_prompt(self, task: Task, context: Dict[str, Any]) -> str:
        """Generate a contextual prompt for the task."""
        
        # Use DIE to generate dynamic prompt
        template_variables = {
            "agent_role": self.definition.role.value,
            "task_description": task.description,
            "input_data": json.dumps(task.input_data, indent=2),
            "expected_output": json.dumps(task.expected_output, indent=2),
            "success_criteria": "\n".join(f"- {criteria}" for criteria in task.success_criteria),
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
    
    def _process_response(self, response, task: Task) -> Dict[str, Any]:
        """Process and validate LLM response."""
        try:
            # Try to parse as JSON first
            if response.content.strip().startswith('{'):
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
                    }
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
                }
            }
    
    def _update_memory(self, task: Task, response, result: Dict[str, Any]) -> None:
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
            }
        )


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflow execution."""
    
    def __init__(self, die: DynamicIntelligenceEngine, mil: ModelIntegrationLayer):
        self.die = die
        self.mil = mil
        self.active_workflows: Dict[UUID, WorkflowDefinition] = {}
        self.agent_pool: Dict[UUID, Agent] = {}
    
    async def execute_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Execute a complete workflow with multiple agents."""
        
        logger.info(
            "Starting workflow execution",
            workflow=workflow.name,
            workflow_id=str(workflow.id),
            agents=len(workflow.agents),
            tasks=len(workflow.tasks),
        )
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.start_time = time.time()
        self.active_workflows[workflow.id] = workflow
        
        try:
            # Initialize agents
            self._initialize_workflow_agents(workflow)
            
            # Execute workflow
            result = await self._execute_workflow_graph(workflow)
            
            # Finalize workflow
            workflow.status = WorkflowStatus.COMPLETED
            workflow.end_time = time.time()
            
            logger.info(
                "Completed workflow execution",
                workflow=workflow.name,
                duration=workflow.end_time - workflow.start_time,
                total_tokens=workflow.total_tokens_used,
                total_cost=workflow.total_cost_usd,
            )
            
            return result
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.end_time = time.time()
            
            logger.error(
                "Workflow execution failed",
                workflow=workflow.name,
                error=str(e),
            )
            
            raise
        
        finally:
            # Cleanup
            if workflow.id in self.active_workflows:
                del self.active_workflows[workflow.id]
    
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
    
    async def _execute_workflow_graph(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Execute the workflow task graph."""
        
        # Build dependency graph
        task_map = {task.id: task for task in workflow.tasks}
        ready_tasks = self._get_ready_tasks(workflow.tasks)
        
        # Shared context for all tasks
        workflow_context = {
            "workflow_id": str(workflow.id),
            "workflow_goal": workflow.goal,
            "start_time": workflow.start_time,
        }
        
        # Execute tasks in dependency order
        while ready_tasks or workflow.current_tasks:
            # Start ready tasks
            for task_id in ready_tasks:
                if task_id not in workflow.current_tasks:
                    asyncio.create_task(
                        self._execute_task_with_tracking(task_map[task_id], workflow, workflow_context)
                    )
                    workflow.current_tasks.append(task_id)
            
            # Wait for any task to complete
            if workflow.current_tasks:
                await asyncio.sleep(0.1)  # Short polling interval
            
            # Update ready tasks
            ready_tasks = self._get_ready_tasks(
                [t for t in workflow.tasks if t.status == TaskStatus.PENDING]
            )
            
            # Check for completion
            if not ready_tasks and not workflow.current_tasks:
                break
        
        # Collect results
        results = {}
        for task in workflow.tasks:
            if task.status == TaskStatus.COMPLETED:
                results[task.name] = task.output_data
                workflow.completed_tasks.append(task.id)
            elif task.status == TaskStatus.FAILED:
                workflow.failed_tasks.append(task.id)
        
        return {
            "status": "completed" if not workflow.failed_tasks else "partial_failure",
            "completed_tasks": len(workflow.completed_tasks),
            "failed_tasks": len(workflow.failed_tasks),
            "total_tokens": workflow.total_tokens_used,
            "total_cost": workflow.total_cost_usd,
            "results": results,
        }
    
    async def _execute_task_with_tracking(
        self,
        task: Task,
        workflow: WorkflowDefinition,
        context: Dict[str, Any],
    ) -> None:
        """Execute a task and update workflow tracking."""
        
        try:
            # Get assigned agent
            if not task.assigned_agent:
                task.assigned_agent = self._auto_assign_agent(task, workflow)
            
            agent = self.agent_pool[task.assigned_agent]
            
            # Execute task
            result = await agent.execute_task(task, context)
            
            # Update workflow metrics
            workflow.total_tokens_used += task.tokens_used
            workflow.total_cost_usd += task.cost_usd
            
        except Exception as e:
            logger.error(
                "Task execution failed in workflow",
                task=task.name,
                workflow=workflow.name,
                error=str(e),
            )
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
        
        finally:
            # Remove from current tasks
            if task.id in workflow.current_tasks:
                workflow.current_tasks.remove(task.id)
    
    def _get_ready_tasks(self, tasks: List[Task]) -> List[UUID]:
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
        
        # Simple assignment based on agent role and task requirements
        # TODO: Implement more sophisticated assignment logic
        
        available_agents = workflow.agents
        
        if not available_agents:
            raise ValueError("No agents available for task assignment")
        
        # For now, just assign the first available agent
        # In a real implementation, this would consider:
        # - Agent capabilities and skills
        # - Current workload
        # - Task requirements
        # - Agent performance history
        
        return available_agents[0].id


class MultiAgentOrchestrationFramework:
    """Main MAOF class that coordinates all orchestration components."""
    
    def __init__(self):
        self.die = DynamicIntelligenceEngine()
        self.mil = ModelIntegrationLayer()
        self.orchestrator = WorkflowOrchestrator(self.die, self.mil)
        self.workflow_templates: Dict[str, WorkflowDefinition] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self) -> None:
        """Initialize default workflow templates."""
        
        # Research and Analysis Workflow
        research_workflow = self._create_research_workflow_template()
        self.workflow_templates["research_analysis"] = research_workflow
        
        # Code Development Workflow
        code_workflow = self._create_code_development_template()
        self.workflow_templates["code_development"] = code_workflow
        
        logger.info("Initialized default workflow templates", count=len(self.workflow_templates))
    
    def _create_research_workflow_template(self) -> WorkflowDefinition:
        """Create a research and analysis workflow template."""
        
        # Define agents
        researcher = AgentDefinition(
            name="Research Specialist",
            role=AgentRole.RESEARCHER,
            description="Gathers and analyzes information from various sources",
            system_prompt="You are a research specialist. Gather comprehensive information and provide detailed analysis.",
            skills=["web_search", "data_analysis", "source_verification"],
            knowledge_domains=["general_knowledge", "current_events", "academic_research"],
        )
        
        analyst = AgentDefinition(
            name="Data Analyst",
            role=AgentRole.ANALYST,
            description="Analyzes data and extracts insights",
            system_prompt="You are a data analyst. Process information and extract meaningful insights.",
            skills=["statistical_analysis", "pattern_recognition", "insight_generation"],
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
            expected_output={"research_findings": "dict", "sources": "list", "key_insights": "list"},
            success_criteria=["Multiple reliable sources identified", "Key findings clearly documented"],
        )
        
        analysis_task = Task(
            name="Data Analysis",
            description="Analyze research findings and extract insights",
            dependencies=[research_task.id],
            expected_output={"analysis": "dict", "trends": "list", "recommendations": "list"},
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
            expected_output={"plan": "dict", "architecture": "dict", "requirements": "list"},
        )
        
        implementation_task = Task(
            name="Code Implementation",
            description="Implement the planned solution",
            dependencies=[planning_task.id],
            expected_output={"code": "string", "documentation": "string", "tests": "string"},
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
        custom_agents: Optional[List[AgentDefinition]] = None,
    ) -> Dict[str, Any]:
        """Execute a goal-oriented workflow."""
        
        # Select or create workflow
        if template_name and template_name in self.workflow_templates:
            workflow = self.workflow_templates[template_name]
            workflow.goal = goal  # Update goal
        else:
            # Create dynamic workflow based on goal
            workflow = await self._create_dynamic_workflow(goal, custom_agents)
        
        # Execute workflow
        return await self.orchestrator.execute_workflow(workflow)
    
    async def _create_dynamic_workflow(
        self,
        goal: str,
        custom_agents: Optional[List[AgentDefinition]] = None,
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
        )
        
        execute_task = Task(
            name="Goal Execution",
            description="Execute the planned approach",
            dependencies=[plan_task.id],
            assigned_agent=agents[1].id,
        )
        
        validate_task = Task(
            name="Goal Validation",
            description="Validate that the goal has been achieved",
            dependencies=[execute_task.id],
            assigned_agent=agents[2].id,
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