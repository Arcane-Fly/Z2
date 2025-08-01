"""
Tests for Basic AI Agent demonstrating DIE + MIL integration
"""

import pytest

from app.agents.basic_agent import BasicAIAgent


class TestBasicAIAgent:
    """Test cases for the Basic AI Agent."""

    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        agent = BasicAIAgent("TestBot", "assistant")

        assert agent.name == "TestBot"
        assert agent.role == "assistant"
        assert agent.memory.long_term["agent_name"] == "TestBot"
        assert agent.memory.long_term["role"] == "assistant"

        # Check that templates were registered
        assert "conversation" in agent.prompt_generator.templates
        assert "analysis" in agent.prompt_generator.templates

    @pytest.mark.asyncio
    async def test_process_message_without_provider(self):
        """Test processing message without LLM provider (fallback mode)."""
        agent = BasicAIAgent("TestBot", "assistant")

        response = await agent.process_message("Hello there!")

        # Updated to match actual fallback behavior
        assert "no LLM providers are currently configured" in response
        assert "TestBot" in response
        assert "Hello there!" in response

        # Check that context was updated
        assert "last_user_message" in agent.memory.short_term
        assert agent.memory.short_term["last_user_message"] == "Hello there!"

    @pytest.mark.asyncio
    async def test_process_analysis_message(self):
        """Test processing message with analysis template."""
        agent = BasicAIAgent("AnalyzerBot", "data analyst")

        response = await agent.process_message(
            "Analyze this data: [1,2,3,4,5]",
            template_name="analysis"
        )

        assert "AnalyzerBot" in response
        assert "no LLM providers are currently configured" in response  # Updated fallback message

        # Check template was used
        assert agent.memory.short_term["template_used"] == "analysis"

    @pytest.mark.asyncio
    async def test_context_compression(self):
        """Test that context gets compressed when it grows too large."""
        agent = BasicAIAgent("TestBot", "assistant")

        # Each process_message call adds these items to short-term:
        # - last_user_message, template_used, timestamp (3 items initially)
        # - last_response, interaction_count (2 more items after processing)
        # But update_context replaces values, so we need to add more diverse data

        # Manually add more items to trigger compression
        for i in range(6):
            agent.memory.update_context({f"extra_item_{i}": f"value_{i}"})

        # Now process a message which will add 5 more items, bringing total > 8
        await agent.process_message("Test message")

        # Should have triggered compression
        assert len(agent.memory.summary) > 0

    def test_get_context_summary(self):
        """Test context summary functionality."""
        agent = BasicAIAgent("SummaryBot", "summarizer")

        summary = agent.get_context_summary()

        assert summary["agent_name"] == "SummaryBot"
        assert summary["role"] == "summarizer"
        assert summary["interaction_count"] == 0
        assert isinstance(summary["short_term_items"], int)
        assert isinstance(summary["long_term_items"], int)

    @pytest.mark.asyncio
    async def test_interaction_counting(self):
        """Test that interactions are counted correctly."""
        agent = BasicAIAgent("CounterBot", "counter")

        # Process several messages
        await agent.process_message("First message")
        await agent.process_message("Second message")
        await agent.process_message("Third message")

        # Check interaction count
        summary = agent.get_context_summary()
        assert summary["interaction_count"] == 3

    def test_template_registration(self):
        """Test that custom templates work correctly."""
        agent = BasicAIAgent("TemplateBot", "tester")

        # Check that default templates exist
        conversation_template = agent.prompt_generator.templates["conversation"]
        assert "You are {agent_name}" in conversation_template.role
        assert "Respond to the user's message" in conversation_template.task

        analysis_template = agent.prompt_generator.templates["analysis"]
        assert "expert {role}" in analysis_template.role
        assert "Analyze the following content" in analysis_template.task
        assert len(analysis_template.constraints) > 0
