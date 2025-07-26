"""
Tests for the Multi-Agent Orchestration Framework (MAOF) Core Module
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents.die import ContextualMemory, DynamicIntelligenceEngine
from app.agents.maof import (
    Agent,
    AgentDefinition,
    AgentRole,
    MultiAgentOrchestrationFramework,
    Task,
    TaskStatus,
    WorkflowDefinition,
    WorkflowOrchestrator,
    WorkflowStatus,
)
from app.agents.mil import LLMResponse, ModelIntegrationLayer


class TestTask:
    """Test cases for Task class."""

    def test_task_initialization(self):
        """Test that Task initializes correctly."""
        task = Task(
            name="Test Task",
            description="A test task",
            input_data={"key": "value"},
            success_criteria=["Must complete successfully"]
        )

        assert task.name == "Test Task"
        assert task.description == "A test task"
        assert task.status == TaskStatus.PENDING
        assert task.input_data == {"key": "value"}
        assert task.success_criteria == ["Must complete successfully"]
        assert task.retry_count == 0
        assert task.max_retries == 3

    def test_task_cancellation(self):
        """Test task cancellation functionality."""
        task = Task(name="Test Task")

        assert not task.is_cancellation_requested()
        
        task.request_cancellation()
        
        assert task.is_cancellation_requested()
        assert task.status == TaskStatus.CANCELLED

    def test_task_retry_logic(self):
        """Test task retry logic."""
        task = Task(name="Test Task", max_retries=2)
        
        # Initially can retry
        task.status = TaskStatus.FAILED
        assert task.can_retry()
        
        # After max retries, cannot retry
        task.retry_count = 2
        assert not task.can_retry()
        
        # Completed tasks cannot retry
        task.status = TaskStatus.COMPLETED
        task.retry_count = 0
        assert not task.can_retry()


class TestAgentDefinition:
    """Test cases for AgentDefinition class."""

    def test_agent_definition_initialization(self):
        """Test that AgentDefinition initializes correctly."""
        agent = AgentDefinition(
            name="Test Agent",
            role=AgentRole.RESEARCHER,
            description="A test agent",
            skills=["research", "analysis"],
            knowledge_domains=["science", "technology"]
        )

        assert agent.name == "Test Agent"
        assert agent.role == AgentRole.RESEARCHER
        assert agent.description == "A test agent"
        assert agent.skills == ["research", "analysis"]
        assert agent.knowledge_domains == ["science", "technology"]
        assert agent.can_delegate is True
        assert agent.trust_level == 0.8

    def test_agent_definition_to_dict(self):
        """Test agent definition serialization."""
        agent = AgentDefinition(
            name="Test Agent",
            role=AgentRole.CODER,
            skills=["python", "javascript"]
        )

        agent_dict = agent.to_dict()

        assert agent_dict["name"] == "Test Agent"
        assert agent_dict["role"] == "coder"
        assert agent_dict["skills"] == ["python", "javascript"]
        assert "id" in agent_dict


class TestWorkflowDefinition:
    """Test cases for WorkflowDefinition class."""

    def test_workflow_definition_initialization(self):
        """Test that WorkflowDefinition initializes correctly."""
        workflow = WorkflowDefinition(
            name="Test Workflow",
            description="A test workflow",
            goal="Test goal"
        )

        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert workflow.goal == "Test goal"
        assert workflow.status == WorkflowStatus.DRAFT
        assert workflow.max_duration_seconds == 3600
        assert workflow.max_cost_usd == 10.0

    def test_workflow_stop_functionality(self):
        """Test workflow stop functionality."""
        workflow = WorkflowDefinition(name="Test Workflow")

        assert not workflow.is_stop_requested()
        
        workflow.request_stop()
        
        assert workflow.is_stop_requested()
        assert workflow.status == WorkflowStatus.STOPPING

    def test_workflow_get_task_by_id(self):
        """Test getting task by ID."""
        task1 = Task(name="Task 1")
        task2 = Task(name="Task 2")
        
        workflow = WorkflowDefinition(
            name="Test Workflow",
            tasks=[task1, task2]
        )

        found_task = workflow.get_task_by_id(task1.id)
        assert found_task == task1
        
        # Non-existent task
        from uuid import uuid4
        non_existent_task = workflow.get_task_by_id(uuid4())
        assert non_existent_task is None


@pytest.mark.asyncio
class TestAgent:
    """Test cases for Agent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_die = MagicMock(spec=DynamicIntelligenceEngine)
        self.mock_mil = MagicMock(spec=ModelIntegrationLayer)
        
        # Mock DIE methods
        self.mock_die.generate_contextual_prompt.return_value = "Test prompt"
        self.mock_die.update_interaction_context = MagicMock()
        
        # Mock MIL response
        self.mock_response = LLMResponse(
            content='{"result": "success"}',
            model_used="test-model",
            provider="test",
            tokens_used=100,
            cost_usd=0.01,
            latency_ms=500,
            finish_reason="stop"
        )
        self.mock_mil.generate_response = AsyncMock(return_value=self.mock_response)

    async def test_agent_initialization(self):
        """Test agent initialization."""
        agent_def = AgentDefinition(
            name="Test Agent",
            role=AgentRole.ANALYST
        )
        
        agent = Agent(agent_def, self.mock_die, self.mock_mil)
        
        assert agent.definition == agent_def
        assert agent.die == self.mock_die
        assert agent.mil == self.mock_mil
        assert isinstance(agent.memory, ContextualMemory)

    async def test_agent_execute_task_success(self):
        """Test successful task execution."""
        agent_def = AgentDefinition(
            name="Test Agent",
            role=AgentRole.ANALYST,
            timeout_seconds=30
        )
        agent = Agent(agent_def, self.mock_die, self.mock_mil)
        
        task = Task(
            name="Test Task",
            description="Analyze data",
            input_data={"data": "test"}
        )
        
        context = {"workflow_id": "test-workflow"}
        
        result = await agent.execute_task(task, context)
        
        assert task.status == TaskStatus.COMPLETED
        assert task.tokens_used == 100
        assert task.cost_usd == 0.01
        assert "result" in result
        assert result["result"] == "success"

    async def test_agent_execute_task_cancellation(self):
        """Test task execution with cancellation."""
        agent_def = AgentDefinition(name="Test Agent")
        agent = Agent(agent_def, self.mock_die, self.mock_mil)
        
        task = Task(name="Test Task")
        task.request_cancellation()  # Cancel before execution
        
        with pytest.raises(asyncio.CancelledError):
            await agent.execute_task(task, {})
        
        assert task.status == TaskStatus.CANCELLED

    async def test_agent_execute_task_timeout(self):
        """Test task execution timeout."""
        agent_def = AgentDefinition(
            name="Test Agent",
            timeout_seconds=1  # Very short timeout
        )
        agent = Agent(agent_def, self.mock_die, self.mock_mil)
        
        # Mock a slow response
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(2)  # Longer than timeout
            return self.mock_response
        
        self.mock_mil.generate_response = slow_response
        
        task = Task(name="Test Task")
        
        with pytest.raises(asyncio.TimeoutError):
            await agent.execute_task(task, {})
        
        assert task.status == TaskStatus.FAILED
        assert "timed out" in task.error_message

    async def test_agent_execute_task_with_retries(self):
        """Test task execution with retry logic."""
        agent_def = AgentDefinition(name="Test Agent")
        agent = Agent(agent_def, self.mock_die, self.mock_mil)
        
        # Mock failure then success
        call_count = 0
        async def mock_response_with_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary failure")
            return self.mock_response
        
        self.mock_mil.generate_response = mock_response_with_failure
        
        task = Task(name="Test Task")
        
        result = await agent.execute_task(task, {})
        
        assert task.status == TaskStatus.COMPLETED
        assert task.retry_count > 0  # Should have retried
        assert call_count == 2  # Failed once, succeeded on retry


@pytest.mark.asyncio
class TestWorkflowOrchestrator:
    """Test cases for WorkflowOrchestrator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_die = MagicMock(spec=DynamicIntelligenceEngine)
        self.mock_mil = MagicMock(spec=ModelIntegrationLayer)
        
        # Mock responses
        self.mock_response = LLMResponse(
            content='{"output": "Task completed"}',
            model_used="test-model",
            provider="test",
            tokens_used=50,
            cost_usd=0.005,
            latency_ms=300,
            finish_reason="stop"
        )
        self.mock_mil.generate_response = AsyncMock(return_value=self.mock_response)
        self.mock_die.generate_contextual_prompt.return_value = "Test prompt"
        
        self.orchestrator = WorkflowOrchestrator(self.mock_die, self.mock_mil)

    async def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        assert self.orchestrator.die == self.mock_die
        assert self.orchestrator.mil == self.mock_mil
        assert len(self.orchestrator.active_workflows) == 0
        assert len(self.orchestrator.agent_pool) == 0

    async def test_simple_workflow_execution(self):
        """Test execution of a simple workflow."""
        # Create agent
        agent = AgentDefinition(
            name="Test Agent",
            role=AgentRole.EXECUTOR
        )
        
        # Create task
        task = Task(
            name="Simple Task",
            description="Do something simple",
            assigned_agent=agent.id
        )
        
        # Create workflow
        workflow = WorkflowDefinition(
            name="Simple Workflow",
            goal="Complete a simple task",
            agents=[agent],
            tasks=[task]
        )
        
        result = await self.orchestrator.execute_workflow(workflow)
        
        assert workflow.status == WorkflowStatus.COMPLETED
        assert len(workflow.completed_tasks) == 1
        assert len(workflow.failed_tasks) == 0
        assert result["status"] == "completed"
        assert "Simple Task" in result["results"]

    async def test_workflow_with_dependencies(self):
        """Test workflow execution with task dependencies."""
        # Create agents
        agent1 = AgentDefinition(name="Agent 1", role=AgentRole.PLANNER)
        agent2 = AgentDefinition(name="Agent 2", role=AgentRole.EXECUTOR)
        
        # Create tasks with dependencies
        task1 = Task(
            name="Planning Task",
            description="Plan the work",
            assigned_agent=agent1.id
        )
        
        task2 = Task(
            name="Execution Task",
            description="Execute the plan",
            assigned_agent=agent2.id,
            dependencies=[task1.id]  # Depends on task1
        )
        
        # Create workflow
        workflow = WorkflowDefinition(
            name="Dependent Workflow",
            goal="Plan and execute",
            agents=[agent1, agent2],
            tasks=[task1, task2]
        )
        
        result = await self.orchestrator.execute_workflow(workflow)
        
        assert workflow.status == WorkflowStatus.COMPLETED
        assert len(workflow.completed_tasks) == 2
        assert task1.end_time <= task2.start_time  # task1 should complete before task2 starts

    async def test_workflow_cancellation(self):
        """Test workflow cancellation."""
        # Create a workflow that takes some time
        agent = AgentDefinition(name="Test Agent")
        task = Task(name="Long Task", assigned_agent=agent.id)
        
        workflow = WorkflowDefinition(
            name="Cancellable Workflow",
            agents=[agent],
            tasks=[task]
        )
        
        # Mock a slow LLM response
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(1)
            return self.mock_response
        
        self.mock_mil.generate_response = slow_response
        
        # Start workflow execution
        execution_task = asyncio.create_task(
            self.orchestrator.execute_workflow(workflow)
        )
        
        # Cancel after a short delay
        await asyncio.sleep(0.1)
        workflow.request_stop()
        execution_task.cancel()
        
        with pytest.raises(asyncio.CancelledError):
            await execution_task

    async def test_workflow_cost_limit(self):
        """Test workflow cost limit enforcement."""
        agent = AgentDefinition(name="Expensive Agent")
        task = Task(name="Expensive Task", assigned_agent=agent.id)
        
        workflow = WorkflowDefinition(
            name="Cost Limited Workflow",
            agents=[agent],
            tasks=[task],
            max_cost_usd=0.001  # Very low limit
        )
        
        # Mock expensive response
        expensive_response = LLMResponse(
            content="Expensive result",
            model_used="expensive-model",
            provider="test",
            tokens_used=10000,
            cost_usd=1.0,  # Exceeds limit
            latency_ms=100,
            finish_reason="stop"
        )
        self.mock_mil.generate_response = AsyncMock(return_value=expensive_response)
        
        result = await self.orchestrator.execute_workflow(workflow)
        
        # Workflow should have exceeded cost limit and stopped
        assert workflow.total_cost_usd >= workflow.max_cost_usd

    def test_agent_task_scoring(self):
        """Test agent-task matching score calculation."""
        # Create agents with different specializations
        researcher = AgentDefinition(
            name="Researcher",
            role=AgentRole.RESEARCHER,
            skills=["research", "analysis"],
            knowledge_domains=["science"]
        )
        
        coder = AgentDefinition(
            name="Coder",
            role=AgentRole.CODER,
            skills=["python", "javascript"],
            knowledge_domains=["programming"]
        )
        
        # Create research task
        research_task = Task(
            name="Research Task",
            description="Conduct scientific research on climate change"
        )
        
        # Create coding task
        coding_task = Task(
            name="Coding Task",
            description="Implement a Python script for data analysis"
        )
        
        workflow = WorkflowDefinition(agents=[researcher, coder])
        
        # Test scoring
        researcher_research_score = self.orchestrator._calculate_agent_task_score(
            researcher, research_task
        )
        researcher_coding_score = self.orchestrator._calculate_agent_task_score(
            researcher, coding_task
        )
        coder_research_score = self.orchestrator._calculate_agent_task_score(
            coder, research_task
        )
        coder_coding_score = self.orchestrator._calculate_agent_task_score(
            coder, coding_task
        )
        
        # Researcher should score higher on research task
        assert researcher_research_score > researcher_coding_score
        # Coder should score higher on coding task
        assert coder_coding_score > coder_research_score
        # Cross-matching should be lower
        assert researcher_research_score > coder_research_score
        assert coder_coding_score > researcher_coding_score


class TestMultiAgentOrchestrationFramework:
    """Test cases for the main MAOF class."""

    def test_maof_initialization(self):
        """Test MAOF initialization."""
        maof = MultiAgentOrchestrationFramework()
        
        assert isinstance(maof.die, DynamicIntelligenceEngine)
        assert isinstance(maof.mil, ModelIntegrationLayer)
        assert isinstance(maof.orchestrator, WorkflowOrchestrator)
        assert len(maof.workflow_templates) > 0

    def test_workflow_templates(self):
        """Test that workflow templates are created."""
        maof = MultiAgentOrchestrationFramework()
        
        assert "research_analysis" in maof.workflow_templates
        assert "code_development" in maof.workflow_templates
        
        research_template = maof.workflow_templates["research_analysis"]
        assert research_template.name == "Research and Analysis Workflow"
        assert len(research_template.agents) == 3  # researcher, analyst, writer
        assert len(research_template.tasks) == 3  # research, analysis, report

    @pytest.mark.asyncio
    async def test_goal_oriented_workflow_with_template(self):
        """Test goal-oriented workflow execution with template."""
        maof = MultiAgentOrchestrationFramework()
        
        # Mock the orchestrator
        maof.orchestrator.execute_workflow = AsyncMock(return_value={
            "status": "completed",
            "results": {"test": "success"}
        })
        
        result = await maof.execute_goal_oriented_workflow(
            goal="Research artificial intelligence trends",
            template_name="research_analysis"
        )
        
        assert result["status"] == "completed"
        assert maof.orchestrator.execute_workflow.called

    @pytest.mark.asyncio
    async def test_dynamic_workflow_creation(self):
        """Test dynamic workflow creation."""
        maof = MultiAgentOrchestrationFramework()
        
        # Mock the orchestrator
        maof.orchestrator.execute_workflow = AsyncMock(return_value={
            "status": "completed",
            "results": {"dynamic": "workflow"}
        })
        
        result = await maof.execute_goal_oriented_workflow(
            goal="Create a custom solution",
            template_name=None  # Should trigger dynamic creation
        )
        
        assert result["status"] == "completed"
        assert maof.orchestrator.execute_workflow.called