"""
Tests for the Dynamic Intelligence Engine (DIE) Core Module
"""

import pytest
from app.agents.die import (
    ContextualMemory,
    PromptTemplate,
    DynamicPromptGenerator,
)


class TestContextualMemory:
    """Test cases for ContextualMemory class."""
    
    def test_contextual_memory_initialization(self):
        """Test that ContextualMemory initializes correctly."""
        memory = ContextualMemory(
            short_term={"current_task": "testing"},
            long_term={"user_preferences": "concise"},
            summary={"session_count": 1}
        )
        
        assert memory.short_term == {"current_task": "testing"}
        assert memory.long_term == {"user_preferences": "concise"}
        assert memory.summary == {"session_count": 1}
    
    def test_update_context(self):
        """Test context updating functionality."""
        memory = ContextualMemory(
            short_term={},
            long_term={},
            summary={}
        )
        
        new_context = {"task": "analysis", "status": "in_progress"}
        memory.update_context(new_context)
        
        assert memory.short_term == new_context
        
        # Test updating existing context
        additional_context = {"priority": "high"}
        memory.update_context(additional_context)
        
        expected = {"task": "analysis", "status": "in_progress", "priority": "high"}
        assert memory.short_term == expected


class TestPromptTemplate:
    """Test cases for PromptTemplate class."""
    
    def test_prompt_template_basic_render(self):
        """Test basic prompt template rendering."""
        template = PromptTemplate(
            role="You are a helpful assistant",
            task="Analyze the following text: {text}",
            format="Provide a JSON response with 'analysis' and 'sentiment' fields"
        )
        
        variables = {"text": "This is a great product!"}
        rendered = template.render(variables)
        
        assert "You are a helpful assistant" in rendered
        assert "Analyze the following text: This is a great product!" in rendered
        assert "JSON response" in rendered
    
    def test_prompt_template_with_context(self):
        """Test prompt template with context."""
        template = PromptTemplate(
            role="You are an expert analyst",
            task="Review the data",
            format="Markdown format",
            context="Previous analysis showed positive trends: {context_info}"
        )
        
        variables = {"context_info": "sales increased 20%"}
        rendered = template.render(variables)
        
        assert "sales increased 20%" in rendered
        assert "Context:" in rendered
    
    def test_prompt_template_with_constraints(self):
        """Test prompt template with constraints."""
        template = PromptTemplate(
            role="Assistant",
            task="Summarize the text",
            format="Brief summary",
            constraints=["Keep under 100 words", "Focus on key points"]
        )
        
        rendered = template.render({})
        
        assert "Constraints:" in rendered
        assert "Keep under 100 words" in rendered
        assert "Focus on key points" in rendered


class TestDynamicPromptGenerator:
    """Test cases for DynamicPromptGenerator class."""
    
    def test_register_template(self):
        """Test template registration."""
        generator = DynamicPromptGenerator()
        
        template = PromptTemplate(
            role="Test role",
            task="Test task",
            format="Test format"
        )
        
        generator.register_template("test_template", template)
        
        assert "test_template" in generator.templates
        assert generator.templates["test_template"] == template
    
    def test_generate_prompt_basic(self):
        """Test basic prompt generation."""
        generator = DynamicPromptGenerator()
        
        template = PromptTemplate(
            role="You are a {role_type} assistant",
            task="Help with {task_type}",
            format="Provide {output_format} response"
        )
        
        generator.register_template("basic_template", template)
        
        memory = ContextualMemory(
            short_term={"last_action": "greeting"},
            long_term={"user_type": "developer"},
            summary={}
        )
        
        variables = {
            "role_type": "coding",
            "task_type": "debugging",
            "output_format": "structured"
        }
        
        prompt = generator.generate_prompt(
            template_name="basic_template",
            variables=variables,
            context=memory,
            agent_role="developer_assistant",
            target_model="gpt-4"
        )
        
        assert "coding assistant" in prompt
        assert "debugging" in prompt
        assert "structured response" in prompt
    
    def test_generate_prompt_with_context(self):
        """Test prompt generation with context integration."""
        generator = DynamicPromptGenerator()
        
        template = PromptTemplate(
            role="Assistant",
            task="Continue the conversation",
            format="Natural response"
        )
        
        generator.register_template("context_template", template)
        
        memory = ContextualMemory(
            short_term={"user_question": "What is Python?", "mood": "curious"},
            long_term={"skill_level": "beginner"},
            summary={"main_points": "User is learning programming"}
        )
        
        prompt = generator.generate_prompt(
            template_name="context_template",
            variables={},
            context=memory,
            agent_role="tutor",
            target_model="gpt-4"
        )
        
        # Should contain context information
        assert "User is learning programming" in prompt or "user_question" in prompt
    
    def test_model_specific_optimization(self):
        """Test model-specific prompt optimization."""
        generator = DynamicPromptGenerator()
        
        template = PromptTemplate(
            role="Assistant",
            task="Answer the question",
            format="Direct answer"
        )
        
        generator.register_template("model_test", template)
        
        memory = ContextualMemory({}, {}, {})
        
        # Test Claude optimization
        claude_prompt = generator.generate_prompt(
            template_name="model_test",
            variables={},
            context=memory,
            agent_role="assistant",
            target_model="claude-3.5-sonnet"
        )
        
        assert "Human:" in claude_prompt and "Assistant:" in claude_prompt
        
        # Test GPT optimization (should not have Human:/Assistant: format)
        gpt_prompt = generator.generate_prompt(
            template_name="model_test",
            variables={},
            context=memory,
            agent_role="assistant", 
            target_model="gpt-4"
        )
        
        assert "Human:" not in gpt_prompt
        
    def test_invalid_template_error(self):
        """Test error handling for invalid template names."""
        generator = DynamicPromptGenerator()
        memory = ContextualMemory({}, {}, {})
        
        with pytest.raises(ValueError, match="Template nonexistent not found"):
            generator.generate_prompt(
                template_name="nonexistent",
                variables={},
                context=memory,
                agent_role="assistant",
                target_model="gpt-4"
            )