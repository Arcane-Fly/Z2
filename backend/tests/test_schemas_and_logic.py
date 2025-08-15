"""
Simple unit tests for schemas and core functionality.
"""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import (
    AgentExecutionRequest,
    ModelTestRequest,
    UserUpdate,
    WorkflowCreate,
)


class TestSchemaValidation:
    """Test Pydantic schema validation."""

    def test_user_update_validation(self):
        """Test UserUpdate schema validation."""
        # Valid update
        valid_update = UserUpdate(
            full_name="Valid Name",
            email="valid@example.com",
            user_type="developer",
            is_active=True
        )
        assert valid_update.full_name == "Valid Name"
        assert valid_update.email == "valid@example.com"
        assert valid_update.user_type == "developer"
        assert valid_update.is_active is True

        # Test email validation
        with pytest.raises(ValidationError):
            UserUpdate(email="invalid-email")

        # Test user_type validation
        with pytest.raises(ValidationError):
            UserUpdate(user_type="invalid_type")

        # Test optional fields
        minimal_update = UserUpdate()
        assert minimal_update.full_name is None
        assert minimal_update.email is None
        assert minimal_update.user_type is None
        assert minimal_update.is_active is None

    def test_agent_execution_request_validation(self):
        """Test AgentExecutionRequest schema validation."""
        # Valid request
        valid_request = AgentExecutionRequest(
            task_description="This is a valid task description that is long enough",
            input_data={"key": "value"},
            expected_output_format="json",
            max_tokens=2048,
            temperature=0.8
        )
        assert len(valid_request.task_description) >= 10
        assert valid_request.input_data == {"key": "value"}
        assert valid_request.max_tokens == 2048
        assert valid_request.temperature == 0.8

        # Test minimum task description length
        with pytest.raises(ValidationError):
            AgentExecutionRequest(task_description="short")

        # Test temperature bounds
        with pytest.raises(ValidationError):
            AgentExecutionRequest(
                task_description="Valid task description here",
                temperature=3.0  # Greater than 2.0
            )

        with pytest.raises(ValidationError):
            AgentExecutionRequest(
                task_description="Valid task description here",
                temperature=-0.1  # Less than 0.0
            )

        # Test max_tokens bounds
        with pytest.raises(ValidationError):
            AgentExecutionRequest(
                task_description="Valid task description here",
                max_tokens=0  # Less than 1
            )

        with pytest.raises(ValidationError):
            AgentExecutionRequest(
                task_description="Valid task description here",
                max_tokens=50000  # Greater than 32000
            )

    def test_workflow_create_validation(self):
        """Test WorkflowCreate schema validation."""
        # Valid workflow
        valid_workflow = WorkflowCreate(
            name="Test Workflow",
            description="A test workflow",
            goal="Complete the test successfully",
            max_duration_seconds=1800,
            max_cost_usd=5.0,
            require_human_approval=True,
            agent_ids=[uuid4(), uuid4()]
        )
        assert valid_workflow.name == "Test Workflow"
        assert valid_workflow.goal == "Complete the test successfully"
        assert valid_workflow.max_duration_seconds == 1800
        assert valid_workflow.max_cost_usd == 5.0
        assert valid_workflow.require_human_approval is True
        assert len(valid_workflow.agent_ids) == 2

        # Test name length validation
        with pytest.raises(ValidationError):
            WorkflowCreate(name="", goal="Valid goal here")

        # Test goal length validation
        with pytest.raises(ValidationError):
            WorkflowCreate(name="Valid Name", goal="short")

        # Test duration bounds
        with pytest.raises(ValidationError):
            WorkflowCreate(
                name="Valid Name",
                goal="Valid goal here",
                max_duration_seconds=30  # Less than 60
            )

        with pytest.raises(ValidationError):
            WorkflowCreate(
                name="Valid Name",
                goal="Valid goal here",
                max_duration_seconds=100000  # Greater than 86400
            )

        # Test cost bounds
        with pytest.raises(ValidationError):
            WorkflowCreate(
                name="Valid Name",
                goal="Valid goal here",
                max_cost_usd=0.05  # Less than 0.1
            )

        with pytest.raises(ValidationError):
            WorkflowCreate(
                name="Valid Name",
                goal="Valid goal here",
                max_cost_usd=2000.0  # Greater than 1000.0
            )

    def test_model_test_request_validation(self):
        """Test ModelTestRequest schema validation."""
        # Valid request
        valid_request = ModelTestRequest(
            model_id="gpt-4o",
            prompt="This is a test prompt for the model",
            max_tokens=1000,
            temperature=0.7
        )
        assert valid_request.model_id == "gpt-4o"
        assert len(valid_request.prompt) >= 10
        assert valid_request.max_tokens == 1000
        assert valid_request.temperature == 0.7

        # Test prompt length validation
        with pytest.raises(ValidationError):
            ModelTestRequest(
                model_id="gpt-4o",
                prompt="short"  # Less than 10 chars
            )

        # Test max_tokens bounds
        with pytest.raises(ValidationError):
            ModelTestRequest(
                model_id="gpt-4o",
                prompt="Valid prompt here",
                max_tokens=0  # Less than 1
            )

        with pytest.raises(ValidationError):
            ModelTestRequest(
                model_id="gpt-4o",
                prompt="Valid prompt here",
                max_tokens=5000  # Greater than 4096
            )

        # Test temperature bounds
        with pytest.raises(ValidationError):
            ModelTestRequest(
                model_id="gpt-4o",
                prompt="Valid prompt here",
                temperature=-0.1  # Less than 0.0
            )

        with pytest.raises(ValidationError):
            ModelTestRequest(
                model_id="gpt-4o",
                prompt="Valid prompt here",
                temperature=2.5  # Greater than 2.0
            )


class TestBasicAgentLogic:
    """Test basic agent logic without external dependencies."""

    def test_contextual_memory_initialization(self):
        """Test ContextualMemory initialization."""
        from app.agents.die import ContextualMemory

        memory = ContextualMemory(
            short_term={},
            long_term={},
            summary={}
        )

        assert memory.short_term == {}
        assert memory.long_term == {}
        assert memory.summary == {}

    def test_contextual_memory_update(self):
        """Test ContextualMemory update functionality."""
        from app.agents.die import ContextualMemory

        memory = ContextualMemory(
            short_term={},
            long_term={},
            summary={}
        )

        # Update context
        memory.update_context({"user_input": "Hello", "timestamp": "2023-01-01"})

        assert memory.short_term["user_input"] == "Hello"
        assert memory.short_term["timestamp"] == "2023-01-01"

    def test_contextual_memory_compression(self):
        """Test ContextualMemory compression functionality."""
        from app.agents.die import ContextualMemory

        memory = ContextualMemory(
            short_term={
                "item1": "value1",
                "item2": "value2",
                "item3": "value3",
                "item4": "value4",
                "item5": "value5",
                "item6": "value6"  # More than 5 items
            },
            long_term={},
            summary={}
        )

        # Compress memory
        memory.compress_to_summary()

        # Short term should be cleared
        assert memory.short_term == {}

        # Summary should contain recent context
        assert "recent_context" in memory.summary
        assert "item" in memory.summary["recent_context"]

    def test_prompt_template_creation(self):
        """Test PromptTemplate creation."""
        from app.agents.die import PromptTemplate

        template = PromptTemplate(
            role="You are a helpful assistant",
            task="Answer the user's question",
            format="Respond in JSON format"
        )

        assert template.role == "You are a helpful assistant"
        assert template.task == "Answer the user's question"
        assert template.format == "Respond in JSON format"


class TestModelIntegrationLayer:
    """Test MIL functionality."""

    def test_model_info_creation(self):
        """Test ModelInfo creation."""
        from app.agents.mil import ModelCapability, ModelInfo

        model = ModelInfo(
            id="gpt-4o",
            provider="openai",
            name="GPT-4o",
            description="Latest GPT-4 model",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.FUNCTION_CALLING],
            context_window=128000,
            input_cost_per_million_tokens=10.0,
            output_cost_per_million_tokens=30.0,
            avg_latency_ms=1500.0,
            quality_score=0.95
        )

        assert model.id == "gpt-4o"
        assert model.provider == "openai"
        assert model.context_window == 128000
        assert model.has_capability(ModelCapability.TEXT_GENERATION)
        assert model.has_capability(ModelCapability.FUNCTION_CALLING)
        assert not model.has_capability(ModelCapability.IMAGE_INPUT)

    def test_routing_policy_creation(self):
        """Test RoutingPolicy creation."""
        from app.agents.mil import RoutingPolicy

        policy = RoutingPolicy(
            cost_weight=0.3,
            latency_weight=0.4,
            quality_weight=0.3,
            prefer_provider="openai",
            max_cost_per_request=1.0,
            max_latency_ms=3000.0
        )

        assert policy.cost_weight == 0.3
        assert policy.latency_weight == 0.4
        assert policy.quality_weight == 0.3
        assert policy.prefer_provider == "openai"
        assert policy.max_cost_per_request == 1.0
        assert policy.max_latency_ms == 3000.0
