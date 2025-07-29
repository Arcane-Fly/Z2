"""
Tests for the quantum computing module.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.models.quantum import (
    QuantumTask,
    QuantumThreadResult,
    Variation,
    CollapseStrategy,
    TaskStatus,
    ThreadStatus,
)
from app.schemas.quantum import QuantumTaskCreate, VariationCreate
from app.services.quantum_service import QuantumAgentManager


class TestQuantumModels:
    """Test quantum model classes."""

    def test_quantum_task_creation(self):
        """Test QuantumTask model creation."""
        task = QuantumTask(
            id=uuid4(),
            name="Test Task",
            description="A test quantum task",
            task_description="Analyze this data",
            collapse_strategy=CollapseStrategy.BEST_SCORE,
            metrics_config={"weights": {"success_rate": 0.5}},
            max_parallel_executions=3,
            timeout_seconds=300,
            user_id=uuid4(),
            status=TaskStatus.PENDING,  # Explicitly set status
            progress=0.0,  # Explicitly set progress
        )
        
        assert task.name == "Test Task"
        assert task.collapse_strategy == CollapseStrategy.BEST_SCORE
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0.0

    def test_variation_creation(self):
        """Test Variation model creation."""
        task_id = uuid4()
        variation = Variation(
            id=uuid4(),
            name="Test Variation",
            agent_type="researcher",
            task_id=task_id,
            weight=1.5,
        )
        
        assert variation.name == "Test Variation"
        assert variation.agent_type == "researcher"
        assert variation.task_id == task_id
        assert variation.weight == 1.5

    def test_thread_result_creation(self):
        """Test QuantumThreadResult model creation."""
        task_id = uuid4()
        variation_id = uuid4()
        result = QuantumThreadResult(
            id=uuid4(),
            thread_name="Test Thread",
            task_id=task_id,
            variation_id=variation_id,
            total_score=0.85,
            status=ThreadStatus.PENDING,  # Explicitly set status
        )
        
        assert result.thread_name == "Test Thread"
        assert result.status == ThreadStatus.PENDING
        assert result.total_score == 0.85


class TestQuantumSchemas:
    """Test quantum Pydantic schemas."""

    def test_quantum_task_create_schema(self):
        """Test QuantumTaskCreate schema validation."""
        variations = [
            VariationCreate(
                name="Variation 1",
                agent_type="researcher",
                weight=1.0,
            ),
            VariationCreate(
                name="Variation 2", 
                agent_type="analyst",
                weight=1.5,
            ),
        ]
        
        task_data = QuantumTaskCreate(
            name="Test Task",
            task_description="Analyze market trends",
            collapse_strategy=CollapseStrategy.WEIGHTED,
            variations=variations,
        )
        
        assert task_data.name == "Test Task"
        assert task_data.collapse_strategy == CollapseStrategy.WEIGHTED
        assert len(task_data.variations) == 2
        assert task_data.max_parallel_executions == 5  # default

    def test_quantum_task_create_validation(self):
        """Test QuantumTaskCreate validation constraints."""
        # Test minimum variations requirement
        with pytest.raises(ValueError):
            QuantumTaskCreate(
                name="Test Task",
                task_description="Test",
                variations=[],  # Empty variations should fail
            )

        # Test maximum variations limit
        variations = [
            VariationCreate(name=f"Var {i}", agent_type="researcher")
            for i in range(25)  # Exceeds max of 20
        ]
        
        with pytest.raises(ValueError):
            QuantumTaskCreate(
                name="Test Task",
                task_description="Test",
                variations=variations,
            )


@pytest.mark.asyncio
class TestQuantumAgentManager:
    """Test QuantumAgentManager service."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        mock = AsyncMock()
        mock.add = AsyncMock()
        mock.flush = AsyncMock()
        mock.commit = AsyncMock()
        mock.refresh = AsyncMock()
        mock.execute = AsyncMock()
        return mock

    @pytest.fixture
    def quantum_manager(self, mock_db):
        """Create a QuantumAgentManager instance with mocked DB."""
        return QuantumAgentManager(mock_db)

    async def test_create_task(self, quantum_manager, mock_db):
        """Test quantum task creation."""
        user_id = uuid4()
        variations = [
            VariationCreate(
                name="Variation 1",
                agent_type="researcher",
            ),
        ]
        
        task_data = QuantumTaskCreate(
            name="Test Task",
            task_description="Analyze data",
            variations=variations,
        )
        
        # Mock the task creation
        mock_task = QuantumTask(
            id=uuid4(),
            name=task_data.name,
            task_description=task_data.task_description,
            user_id=user_id,
        )
        
        with patch.object(mock_db, 'flush', new_callable=AsyncMock):
            with patch.object(mock_db, 'commit', new_callable=AsyncMock):
                with patch.object(mock_db, 'refresh', new_callable=AsyncMock):
                    task = await quantum_manager.create_task(user_id, task_data)
                    
                    # Verify task creation calls
                    mock_db.add.assert_called()
                    mock_db.flush.assert_called()
                    mock_db.commit.assert_called()

    async def test_collapse_strategies(self, quantum_manager):
        """Test different collapse strategies."""
        # Create mock thread results
        results = [
            QuantumThreadResult(
                id=uuid4(),
                thread_name="Thread 1",
                status=ThreadStatus.COMPLETED,
                result={"response": "Result 1"},
                total_score=0.8,
                task_id=uuid4(),
                variation_id=uuid4(),
            ),
            QuantumThreadResult(
                id=uuid4(),
                thread_name="Thread 2", 
                status=ThreadStatus.COMPLETED,
                result={"response": "Result 2"},
                total_score=0.9,
                task_id=uuid4(),
                variation_id=uuid4(),
            ),
        ]
        
        # Test best score strategy
        collapsed_result, metrics = quantum_manager._collapse_best_score(results)
        assert metrics["final_score"] == 0.9
        assert "selected_result_id" in metrics
        
        # Test first success strategy
        collapsed_result, metrics = quantum_manager._collapse_first_success(results)
        assert metrics["strategy"] == "first_success"
        
        # Test consensus strategy
        collapsed_result, metrics = quantum_manager._collapse_consensus(results)
        assert metrics["strategy"] == "consensus"
        assert abs(metrics["final_score"] - 0.85) < 0.01  # Use approximate comparison for floating point

    async def test_metrics_calculation(self, quantum_manager):
        """Test thread metrics calculation."""
        result = {
            "response": "This is a good response with sufficient length",
            "success": True,
        }
        execution_time = 15.0
        variation = Variation(
            id=uuid4(),
            name="Test Variation",
            agent_type="researcher",
            task_id=uuid4(),
        )
        
        metrics = await quantum_manager._calculate_thread_metrics(
            result, execution_time, variation
        )
        
        assert metrics["success_rate"] == 1.0
        assert metrics["execution_time_score"] == 0.5  # (30-15)/30
        assert metrics["completeness"] > 0.0
        assert metrics["accuracy"] > 0.0
        assert "total_score" in metrics

    def test_prompt_modifications(self, quantum_manager):
        """Test prompt modification functionality."""
        base_prompt = "Analyze the following data"
        
        # Test prefix modification
        modifications = {"prefix": "You are an expert analyst."}
        modified = quantum_manager._apply_prompt_modifications(base_prompt, modifications)
        assert "You are an expert analyst." in modified
        assert base_prompt in modified
        
        # Test suffix modification
        modifications = {"suffix": "Provide detailed insights."}
        modified = quantum_manager._apply_prompt_modifications(base_prompt, modifications)
        assert "Provide detailed insights." in modified
        
        # Test replacements
        modifications = {"replacements": {"data": "information"}}
        modified = quantum_manager._apply_prompt_modifications(base_prompt, modifications)
        assert "information" in modified
        assert "data" not in modified
        
        # Test style modification
        modifications = {"style": "formal"}
        modified = quantum_manager._apply_prompt_modifications(base_prompt, modifications)
        assert "formal style" in modified


class TestCollapseStrategies:
    """Test collapse strategy implementations."""

    def test_collapse_strategy_enum(self):
        """Test CollapseStrategy enum values."""
        assert CollapseStrategy.FIRST_SUCCESS == "first_success"
        assert CollapseStrategy.BEST_SCORE == "best_score"
        assert CollapseStrategy.CONSENSUS == "consensus"
        assert CollapseStrategy.COMBINED == "combined"
        assert CollapseStrategy.WEIGHTED == "weighted"

    def test_task_status_enum(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELLED == "cancelled"

    def test_thread_status_enum(self):
        """Test ThreadStatus enum values."""
        assert ThreadStatus.PENDING == "pending"
        assert ThreadStatus.RUNNING == "running"
        assert ThreadStatus.COMPLETED == "completed"
        assert ThreadStatus.FAILED == "failed"
        assert ThreadStatus.CANCELLED == "cancelled"


@pytest.mark.asyncio
class TestQuantumAPIIntegration:
    """Integration tests for quantum API endpoints."""

    @pytest.fixture
    def mock_quantum_manager(self):
        """Create a mock QuantumAgentManager."""
        mock = AsyncMock()
        
        # Mock task creation
        mock_task = QuantumTask(
            id=uuid4(),
            name="Test Task",
            task_description="Test description",
            user_id=uuid4(),
        )
        mock.create_task.return_value = mock_task
        mock.get_task.return_value = mock_task
        mock.execute_task.return_value = mock_task
        
        return mock

    async def test_quantum_task_workflow(self, mock_quantum_manager):
        """Test complete quantum task workflow."""
        user_id = uuid4()
        
        # Create task
        task_data = QuantumTaskCreate(
            name="Integration Test Task",
            task_description="Test task description",
            variations=[
                VariationCreate(name="Var 1", agent_type="researcher"),
                VariationCreate(name="Var 2", agent_type="analyst"),
            ],
        )
        
        # Test task creation
        task = await mock_quantum_manager.create_task(user_id, task_data)
        assert task is not None
        mock_quantum_manager.create_task.assert_called_once_with(user_id, task_data)
        
        # Test task execution
        executed_task = await mock_quantum_manager.execute_task(task.id)
        assert executed_task is not None
        mock_quantum_manager.execute_task.assert_called_once_with(task.id)
        
        # Test task retrieval
        retrieved_task = await mock_quantum_manager.get_task(task.id)
        assert retrieved_task is not None
        mock_quantum_manager.get_task.assert_called_once_with(task.id)