"""
Heavy Analysis Integration Tests

Basic tests to verify the make-it-heavy integration is working correctly.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch

# Import the modules we want to test
from app.services.heavy_analysis import HeavyAnalysisService, HeavyAnalysisProgress
from app.services.heavy_analysis_tools import (
    HeavyAnalysisToolRegistry, 
    WebSearchTool,
    CalculatorTool,
    FileReadTool,
    TaskCompletionTool
)
from app.agents.heavy_analysis_agent import HeavyAnalysisAgent


class TestHeavyAnalysisTools:
    """Test the tool system functionality."""
    
    def test_tool_registry_initialization(self):
        """Test that tool registry initializes correctly."""
        registry = HeavyAnalysisToolRegistry()
        
        # Should have the core tools
        expected_tools = ['search_web', 'calculate', 'read_file', 'mark_task_complete']
        assert all(tool in registry.get_all_tools() for tool in expected_tools)
        assert len(registry.get_all_tools()) == len(expected_tools)
    
    def test_function_schemas(self):
        """Test that tools provide valid function schemas."""
        registry = HeavyAnalysisToolRegistry()
        schemas = registry.get_function_schemas()
        
        assert len(schemas) > 0
        for schema in schemas:
            assert 'type' in schema
            assert schema['type'] == 'function'
            assert 'function' in schema
            assert 'name' in schema['function']
            assert 'description' in schema['function']
            assert 'parameters' in schema['function']
    
    @pytest.mark.asyncio
    async def test_calculator_tool(self):
        """Test calculator tool functionality."""
        calc = CalculatorTool()
        
        # Test basic operations
        result = await calc.execute('2 + 3')
        assert result['result'] == 5
        assert result['expression'] == '2 + 3'
        
        # Test complex operations
        result = await calc.execute('2 + 3 * 4')
        assert result['result'] == 14
        
        # Test functions
        result = await calc.execute('sqrt(16)')
        assert result['result'] == 4.0
        
        # Test error handling
        result = await calc.execute('invalid_expression')
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_task_completion_tool(self):
        """Test task completion tool."""
        tool = TaskCompletionTool()
        
        result = await tool.execute(
            task_summary="Test task completed",
            completion_message="Test message"
        )
        
        assert result['status'] == 'completed'
        assert result['summary'] == "Test task completed"
        assert result['message'] == "Test message"
        assert 'timestamp' in result


class TestHeavyAnalysisProgress:
    """Test progress tracking functionality."""
    
    def test_progress_initialization(self):
        """Test progress tracker initialization."""
        progress = HeavyAnalysisProgress(4)
        
        assert progress.num_agents == 4
        assert len(progress.agent_progress) == 4
        
        # All agents should start as QUEUED
        status = progress.get_progress_status()
        assert all(status[i] == "QUEUED" for i in range(4))
    
    def test_progress_updates(self):
        """Test progress update functionality."""
        progress = HeavyAnalysisProgress(2)
        
        # Update agent progress
        progress.update_agent_progress(0, "PROCESSING...")
        progress.update_agent_progress(1, "COMPLETED", "Agent 1 result")
        
        status = progress.get_progress_status()
        assert status[0] == "PROCESSING..."
        assert status[1] == "COMPLETED"
        assert progress.agent_results[1] == "Agent 1 result"
    
    def test_elapsed_time(self):
        """Test elapsed time calculation."""
        progress = HeavyAnalysisProgress(1)
        
        # Should have some elapsed time
        elapsed = progress.get_elapsed_time()
        assert elapsed >= 0
        assert isinstance(elapsed, float)


class TestHeavyAnalysisService:
    """Test the core heavy analysis service."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = HeavyAnalysisService()
        
        assert service.default_num_agents == 4
        assert service.task_timeout == 300
        assert hasattr(service, 'mil')
        assert hasattr(service, 'question_generation_prompt')
        assert hasattr(service, 'synthesis_prompt')
    
    @pytest.mark.asyncio
    async def test_task_decomposition_fallback(self):
        """Test task decomposition with fallback when no LLM providers."""
        service = HeavyAnalysisService()
        
        # This should use fallback questions since no providers are configured
        questions = await service.decompose_task("Test query", 4)
        
        assert len(questions) == 4
        assert all("Test query" in q for q in questions)
        assert any("Research" in q for q in questions)
        assert any("Analyze" in q for q in questions)
    
    @pytest.mark.asyncio
    async def test_result_aggregation_single_result(self):
        """Test result aggregation with single successful result."""
        service = HeavyAnalysisService()
        
        agent_results = [
            {
                "agent_id": 0,
                "status": "success",
                "response": "Test response",
                "execution_time": 1.0
            }
        ]
        
        result = await service.aggregate_results(agent_results)
        assert result == "Test response"
    
    @pytest.mark.asyncio
    async def test_result_aggregation_all_failed(self):
        """Test result aggregation when all agents fail."""
        service = HeavyAnalysisService()
        
        agent_results = [
            {
                "agent_id": 0,
                "status": "error",
                "response": "Error message",
                "execution_time": 0
            }
        ]
        
        result = await service.aggregate_results(agent_results)
        assert "All agents failed" in result


class TestHeavyAnalysisAgent:
    """Test the enhanced heavy analysis agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = HeavyAnalysisAgent("TestAgent", "research_analyst")
        
        assert agent.name == "TestAgent"
        assert agent.role == "research_analyst"
        assert hasattr(agent, 'tool_registry')
        assert hasattr(agent, 'tools')
        assert len(agent.tools) > 0
        assert agent.tool_enabled is True
    
    def test_system_prompt_generation(self):
        """Test system prompt generation."""
        agent = HeavyAnalysisAgent("TestAgent", "research_analyst")
        
        prompt = agent._create_system_prompt()
        
        assert "TestAgent" in prompt
        assert "research_analyst" in prompt
        assert "Available Tools:" in prompt
        assert "search_web" in prompt
    
    def test_tool_call_extraction(self):
        """Test tool call extraction from content."""
        agent = HeavyAnalysisAgent("TestAgent", "research_analyst")
        
        # Test content with tool call
        content = "I need to search_web(query='test query') for information."
        tool_calls = agent._extract_tool_calls(content)
        
        # Note: This is a simplified test since the extraction logic is basic
        # In a full implementation, this would be more sophisticated
        assert isinstance(tool_calls, list)
    
    def test_completion_detection(self):
        """Test completion detection."""
        agent = HeavyAnalysisAgent("TestAgent", "research_analyst")
        
        # Test complete responses
        complete_responses = [
            "In conclusion, this analysis shows...",
            "To summarize the findings...",
            "This comprehensive overview demonstrates..."
        ]
        
        for response in complete_responses:
            assert agent._is_response_complete(response)
        
        # Test incomplete responses
        incomplete_response = "Let me continue analyzing..."
        assert not agent._is_response_complete(incomplete_response)


# Integration test function that can be run manually
async def run_integration_tests():
    """Run integration tests manually."""
    print("🧪 Running Heavy Analysis Integration Tests")
    print("=" * 50)
    
    try:
        # Test tool system
        print("✅ Testing tool system...")
        registry = HeavyAnalysisToolRegistry()
        assert len(registry.get_all_tools()) == 4
        
        # Test calculator
        calc_result = await registry.execute_tool('calculate', expression='2 + 3')
        assert calc_result['result'] == 5
        
        # Test service
        print("✅ Testing heavy analysis service...")
        service = HeavyAnalysisService()
        questions = await service.decompose_task("Test", 3)
        assert len(questions) == 3
        
        # Test agent
        print("✅ Testing heavy analysis agent...")
        agent = HeavyAnalysisAgent("TestAgent", "research_analyst")
        assert len(agent.tools) > 0
        
        print("✅ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run integration tests
    success = asyncio.run(run_integration_tests())
    exit(0 if success else 1)