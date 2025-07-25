"""
Dynamic Intelligence Engine (DIE) Core Module

The DIE is responsible for adaptive contextual flows, dynamic prompt generation,
and structured prompt engineering as specified in the Z2 requirements.
"""

from dataclasses import dataclass
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ContextualMemory:
    """Manages contextual information across agent interactions."""

    short_term: dict[str, Any]  # Recent conversation/task context
    long_term: dict[str, Any]  # Persistent knowledge and preferences
    summary: dict[str, Any]  # Compressed historical context

    def update_context(self, new_context: dict[str, Any]) -> None:
        """Update contextual memory with new information."""
        self.short_term.update(new_context)

    def compress_to_summary(self) -> None:
        """Compress short-term context into summary for efficiency."""
        if not self.short_term:
            return

        # Simple implementation: move recent context to summary
        key_items = list(self.short_term.items())[-5:]  # Keep last 5 items

        # Create a compressed summary
        if key_items:
            summary_text = ", ".join([f"{k}: {str(v)[:50]}" for k, v in key_items])
            self.summary["recent_context"] = summary_text

        # Clear short-term memory
        self.short_term.clear()


@dataclass
class PromptTemplate:
    """Structured prompt template following RTF (Role-Task-Format) standard."""

    role: str  # Agent's role description
    task: str  # Specific task to perform
    format: str  # Expected output format
    context: Optional[str] = None  # Additional context
    constraints: Optional[list[str]] = None  # Task constraints
    examples: Optional[list[str]] = None  # Few-shot examples

    def render(self, variables: dict[str, Any]) -> str:
        """Render the template with provided variables."""
        prompt_parts = [
            f"Role: {self.role.format(**variables)}",
            f"Task: {self.task.format(**variables)}",
            f"Format: {self.format.format(**variables)}",
        ]

        if self.context:
            prompt_parts.append(f"Context: {self.context.format(**variables)}")

        if self.constraints:
            prompt_parts.append("Constraints:")
            for constraint in self.constraints:
                prompt_parts.append(f"- {constraint}")

        if self.examples:
            prompt_parts.append("Examples:")
            for example in self.examples:
                prompt_parts.append(f"- {example}")

        return "\n\n".join(prompt_parts)


class DynamicPromptGenerator:
    """Generates and refines prompts dynamically based on context and task."""

    def __init__(self):
        self.templates: dict[str, PromptTemplate] = {}
        self.performance_cache: dict[str, float] = {}

    def register_template(self, name: str, template: PromptTemplate) -> None:
        """Register a new prompt template."""
        self.templates[name] = template
        logger.info("Registered prompt template", template_name=name)

    def generate_prompt(
        self,
        template_name: str,
        variables: dict[str, Any],
        context: ContextualMemory,
        agent_role: str,
        target_model: str,
    ) -> str:
        """Generate a dynamic prompt based on context and parameters."""

        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")

        template = self.templates[template_name]

        # Enhance variables with contextual information
        enhanced_variables = {
            **variables,
            "context_summary": self._summarize_context(context),
            "agent_role": agent_role,
            "target_model": target_model,
        }

        # Generate base prompt
        prompt = template.render(enhanced_variables)

        # Add context summary if available and not already in template
        context_summary = enhanced_variables["context_summary"]
        if context_summary and context_summary != "No prior context":
            if "Context:" not in prompt:
                prompt += f"\n\nContext: {context_summary}"

        # Apply model-specific optimizations
        prompt = self._optimize_for_model(prompt, target_model)

        # Apply cost optimization techniques
        prompt = self._optimize_for_cost(prompt)

        logger.debug(
            "Generated dynamic prompt",
            template=template_name,
            model=target_model,
            prompt_length=len(prompt),
        )

        return prompt

    def _summarize_context(self, context: ContextualMemory) -> str:
        """Create a concise summary of contextual information."""
        # TODO: Implement intelligent context summarization
        summary_parts = []

        if context.summary:
            summary_parts.append(
                "Previous: " + str(context.summary.get("main_points", ""))
            )

        if context.short_term:
            recent_items = list(context.short_term.items())[-3:]  # Last 3 items
            summary_parts.append(
                "Recent: " + ", ".join([f"{k}: {v}" for k, v in recent_items])
            )

        return " | ".join(summary_parts) if summary_parts else "No prior context"

    def _optimize_for_model(self, prompt: str, model: str) -> str:
        """Apply model-specific optimizations."""
        # Different models have different optimal prompt structures
        if "claude" in model.lower():
            # Anthropic Claude prefers more structured prompts
            return f"Human: {prompt}\n\nAssistant:"
        elif "gpt" in model.lower():
            # OpenAI models work well with direct prompts
            return prompt
        elif "llama" in model.lower():
            # Llama models benefit from explicit formatting
            return f"### Instruction:\n{prompt}\n\n### Response:"

        return prompt

    def _optimize_for_cost(self, prompt: str) -> str:
        """Apply cost optimization techniques like token reduction."""
        # TODO: Implement intelligent token reduction while preserving meaning
        # For now, just basic cleanup

        # Remove excessive whitespace
        lines = [line.strip() for line in prompt.split("\n") if line.strip()]
        optimized = "\n".join(lines)

        # Log optimization if significant reduction
        original_length = len(prompt)
        optimized_length = len(optimized)

        if original_length - optimized_length > 50:
            logger.debug(
                "Applied cost optimization",
                original_tokens=original_length // 4,  # Rough token estimate
                optimized_tokens=optimized_length // 4,
                reduction_percent=(original_length - optimized_length)
                / original_length
                * 100,
            )

        return optimized


class AdaptiveContextualFlow:
    """Manages adaptive contextual flows throughout agent interactions."""

    def __init__(self):
        self.memory = ContextualMemory(short_term={}, long_term={}, summary={})
        self.interaction_history: list[dict[str, Any]] = []

    def update_context(
        self, user_input: str, agent_response: str, metadata: dict[str, Any]
    ) -> None:
        """Update contextual flow with new interaction."""

        interaction = {
            "timestamp": metadata.get("timestamp"),
            "user_input": user_input,
            "agent_response": agent_response,
            "success": metadata.get("success", True),
            "tokens_used": metadata.get("tokens_used", 0),
            "model_used": metadata.get("model_used"),
        }

        self.interaction_history.append(interaction)

        # Update short-term memory
        self.memory.update_context(
            {
                "last_user_input": user_input,
                "last_response": agent_response,
                "conversation_length": len(self.interaction_history),
                "recent_success_rate": self._calculate_recent_success_rate(),
            }
        )

        # Compress context if conversation is getting long
        if len(self.interaction_history) > 10:
            self._compress_context()

    def get_context_for_prompt(self) -> ContextualMemory:
        """Get current contextual memory for prompt generation."""
        return self.memory

    def _calculate_recent_success_rate(self, window: int = 5) -> float:
        """Calculate success rate for recent interactions."""
        if not self.interaction_history:
            return 1.0

        recent_interactions = self.interaction_history[-window:]
        successful = sum(
            1 for interaction in recent_interactions if interaction["success"]
        )

        return successful / len(recent_interactions)

    def _compress_context(self) -> None:
        """Compress older interactions into summary."""
        # Keep last 5 interactions in short-term, compress the rest
        if len(self.interaction_history) > 5:
            to_compress = self.interaction_history[:-5]

            # Simple compression - track main themes and outcomes
            total_tokens = sum(
                interaction["tokens_used"] for interaction in to_compress
            )
            success_rate = sum(
                1 for interaction in to_compress if interaction["success"]
            ) / len(to_compress)

            self.memory.summary.update(
                {
                    "total_interactions": len(to_compress),
                    "total_tokens_used": total_tokens,
                    "overall_success_rate": success_rate,
                    "main_topics": self._extract_topics(to_compress),
                }
            )

            # Remove compressed interactions
            self.interaction_history = self.interaction_history[-5:]

            logger.debug(
                "Compressed context",
                compressed_interactions=len(to_compress),
                success_rate=success_rate,
            )

    def _extract_topics(self, interactions: list[dict[str, Any]]) -> list[str]:
        """Extract main topics from interactions (simple keyword-based for now)."""
        # TODO: Implement more sophisticated topic extraction
        all_text = " ".join(
            [
                interaction["user_input"] + " " + interaction["agent_response"]
                for interaction in interactions
            ]
        )

        # Simple keyword extraction (placeholder)
        common_words = ["analysis", "code", "data", "help", "create", "explain"]
        topics = [word for word in common_words if word in all_text.lower()]

        return topics[:3]  # Return top 3 topics


class DynamicIntelligenceEngine:
    """Main DIE class that orchestrates all dynamic intelligence components."""

    def __init__(self):
        self.prompt_generator = DynamicPromptGenerator()
        self.contextual_flow = AdaptiveContextualFlow()
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """Initialize standard prompt templates."""

        # General task template
        general_template = PromptTemplate(
            role="You are an intelligent AI agent specialized in {agent_role}",
            task="Complete the following task: {task_description}",
            format="Provide your response in {output_format} format",
            constraints=[
                "Be accurate and concise",
                "If uncertain, clearly state your uncertainty",
                "Follow all specified requirements",
            ],
        )
        self.prompt_generator.register_template("general", general_template)

        # Research agent template
        research_template = PromptTemplate(
            role="You are a research specialist with expertise in information gathering and analysis",
            task="Research and analyze: {research_topic}",
            format="Provide a structured report with: 1) Summary, 2) Key findings, 3) Sources, 4) Recommendations",
            constraints=[
                "Use reliable sources",
                "Cite all information",
                "Maintain objectivity",
                "Identify any limitations in the research",
            ],
        )
        self.prompt_generator.register_template("research", research_template)

        # Code generation template
        code_template = PromptTemplate(
            role="You are an expert software developer proficient in {programming_language}",
            task="Generate code for: {code_requirements}",
            format="Provide clean, well-commented code with explanation",
            constraints=[
                "Follow best practices and conventions",
                "Include error handling",
                "Add helpful comments",
                "Ensure code is production-ready",
            ],
        )
        self.prompt_generator.register_template("code", code_template)

    def generate_contextual_prompt(
        self,
        template_name: str,
        variables: dict[str, Any],
        agent_role: str,
        target_model: str,
    ) -> str:
        """Generate a contextually-aware prompt."""
        context = self.contextual_flow.get_context_for_prompt()

        return self.prompt_generator.generate_prompt(
            template_name=template_name,
            variables=variables,
            context=context,
            agent_role=agent_role,
            target_model=target_model,
        )

    def update_interaction_context(
        self,
        user_input: str,
        agent_response: str,
        metadata: dict[str, Any],
    ) -> None:
        """Update the contextual flow with a new interaction."""
        self.contextual_flow.update_context(user_input, agent_response, metadata)
