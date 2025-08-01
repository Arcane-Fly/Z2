"""
Tests for agent execution integration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.schemas import AgentExecutionRequest, AgentExecutionResponse


class TestAgentExecution:
    """Test agent execution with BasicAIAgent integration."""

    @pytest.mark.asyncio
    async def test_agent_execution_success(self):
        """Test successful agent task execution."""
        from app.api.v1.endpoints.agents import execute_agent_task
        from app.models.agent import Agent
        from app.models.user import User
        
        # Create mock agent
        agent_id = uuid4()
        mock_agent = MagicMock(spec=Agent)
        mock_agent.id = agent_id
        mock_agent.name = "TestAgent"
        mock_agent.role = "assistant"
        mock_agent.temperature = 0.7
        mock_agent.max_tokens = 4096
        mock_agent.total_executions = 0
        mock_agent.total_tokens_used = 0
        mock_agent.average_response_time = None

        # Create mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()

        # Create mock database session
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_agent
        mock_db.execute.return_value = mock_result

        # Create execution request
        execution_request = AgentExecutionRequest(
            task_description="Test task description",
            input_data={"key": "value"},
            expected_output_format="json"
        )

        # Mock BasicAIAgent
        with patch('app.api.v1.endpoints.agents.BasicAIAgent') as MockBasicAIAgent:
            mock_basic_agent = MockBasicAIAgent.return_value
            mock_basic_agent.process_message.return_value = "Test response from agent"

            # Execute the task
            result = await execute_agent_task(
                agent_id=agent_id,
                execution_request=execution_request,
                current_user=mock_user,
                db=mock_db
            )

            # Verify result
            assert isinstance(result, AgentExecutionResponse)
            assert result.status == "completed"
            assert "Test response from agent" in result.output["result"]
            assert result.tokens_used > 0
            assert result.cost_usd > 0
            assert result.execution_time_ms > 0

            # Verify agent was created correctly
            MockBasicAIAgent.assert_called_once_with(
                name="TestAgent",
                role="assistant"
            )

            # Verify agent statistics were updated
            assert mock_agent.total_executions == 1
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_execution_not_found(self):
        """Test agent execution with non-existent agent."""
        from app.api.v1.endpoints.agents import execute_agent_task
        from app.models.user import User
        from fastapi import HTTPException
        
        # Create mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()

        # Create mock database session that returns no agent
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Create execution request
        execution_request = AgentExecutionRequest(
            task_description="Test task description"
        )

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await execute_agent_task(
                agent_id=uuid4(),
                execution_request=execution_request,
                current_user=mock_user,
                db=mock_db
            )
        
        assert exc_info.value.status_code == 404
        assert "Agent not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_agent_execution_error_handling(self):
        """Test agent execution error handling."""
        from app.api.v1.endpoints.agents import execute_agent_task
        from app.models.agent import Agent
        from app.models.user import User
        from fastapi import HTTPException
        
        # Create mock agent
        agent_id = uuid4()
        mock_agent = MagicMock(spec=Agent)
        mock_agent.id = agent_id
        mock_agent.name = "TestAgent"
        mock_agent.role = "assistant"
        mock_agent.temperature = 0.7
        mock_agent.max_tokens = 4096

        # Create mock user
        mock_user = MagicMock(spec=User)

        # Create mock database session
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_agent
        mock_db.execute.return_value = mock_result

        # Create execution request
        execution_request = AgentExecutionRequest(
            task_description="Test task description"
        )

        # Mock BasicAIAgent to raise an exception
        with patch('app.api.v1.endpoints.agents.BasicAIAgent') as MockBasicAIAgent:
            mock_basic_agent = MockBasicAIAgent.return_value
            mock_basic_agent.process_message.side_effect = Exception("Test error")

            # Execute and expect exception
            with pytest.raises(HTTPException) as exc_info:
                await execute_agent_task(
                    agent_id=agent_id,
                    execution_request=execution_request,
                    current_user=mock_user,
                    db=mock_db
                )
            
            assert exc_info.value.status_code == 500
            assert "Agent execution failed" in exc_info.value.detail

    def test_agent_execution_request_schema(self):
        """Test AgentExecutionRequest schema validation."""
        # Valid request
        valid_request = AgentExecutionRequest(
            task_description="This is a valid task description",
            input_data={"key": "value"},
            expected_output_format="json",
            max_tokens=2048,
            temperature=0.8
        )
        assert valid_request.task_description == "This is a valid task description"
        assert valid_request.input_data == {"key": "value"}
        assert valid_request.max_tokens == 2048
        assert valid_request.temperature == 0.8

        # Test minimum task description length
        with pytest.raises(ValueError):
            AgentExecutionRequest(task_description="short")  # Less than 10 chars

        # Test temperature bounds
        with pytest.raises(ValueError):
            AgentExecutionRequest(
                task_description="Valid task description",
                temperature=3.0  # Greater than 2.0
            )

        # Test max_tokens bounds
        with pytest.raises(ValueError):
            AgentExecutionRequest(
                task_description="Valid task description",
                max_tokens=0  # Less than 1
            )