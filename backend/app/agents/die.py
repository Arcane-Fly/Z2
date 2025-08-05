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
        def safe_format(template_str: str, vars_dict: dict[str, Any]) -> str:
            """Safely format a template string, handling missing variables."""
            try:
                return template_str.format(**vars_dict)
            except (KeyError, ValueError):
                # Return template with variable placeholders if formatting fails
                return template_str
        
        prompt_parts = [
            f"Role: {safe_format(self.role, variables)}",
            f"Task: {safe_format(self.task, variables)}",
            f"Format: {safe_format(self.format, variables)}",
        ]

        if self.context:
            prompt_parts.append(f"Context: {safe_format(self.context, variables)}")

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
        summary_parts = []

        # Add historical summary
        if context.summary:
            main_points = context.summary.get("main_points", "")
            if main_points:
                summary_parts.append(f"History: {main_points}")
            
            # Add performance metrics if available
            success_rate = context.summary.get("overall_success_rate")
            if success_rate is not None:
                summary_parts.append(f"Success rate: {success_rate:.1%}")

        # Add recent context with prioritization
        if context.short_term:
            # Prioritize recent items by relevance
            prioritized_items = self._prioritize_context_items(context.short_term)
            if prioritized_items:
                recent_summary = ", ".join([f"{k}: {v}" for k, v in prioritized_items])
                summary_parts.append(f"Current: {recent_summary}")

        # Add long-term context if relevant
        if context.long_term:
            relevant_long_term = self._extract_relevant_long_term(context.long_term)
            if relevant_long_term:
                summary_parts.append(f"Context: {relevant_long_term}")

        return " | ".join(summary_parts) if summary_parts else "No prior context"

    def _prioritize_context_items(self, short_term: dict[str, Any]) -> list[tuple[str, Any]]:
        """Prioritize context items by relevance."""
        # Define priority keywords that indicate important context
        priority_keywords = {
            "error", "failure", "success", "task", "goal", "objective", 
            "user", "current", "active", "status", "result", "output"
        }
        
        items = list(short_term.items())
        
        # Sort by priority (items with priority keywords first)
        def priority_score(item):
            key, value = item
            score = 0
            key_lower = key.lower()
            value_str = str(value).lower()
            
            # Boost score for priority keywords
            for keyword in priority_keywords:
                if keyword in key_lower or keyword in value_str:
                    score += 1
            
            # Boost score for recent timestamps or numeric values
            if isinstance(value, (int, float)):
                score += 0.5
                
            return score
        
        sorted_items = sorted(items, key=priority_score, reverse=True)
        
        # Return top 3 most relevant items
        return sorted_items[:3]

    def _extract_relevant_long_term(self, long_term: dict[str, Any]) -> str:
        """Extract relevant information from long-term memory."""
        relevant_items = []
        
        # Extract user preferences and settings
        for key, value in long_term.items():
            if key in ["user_preferences", "settings", "constraints", "requirements"]:
                relevant_items.append(f"{key}: {value}")
        
        return ", ".join(relevant_items) if relevant_items else ""

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
        """Apply intelligent token reduction while preserving meaning."""
        # Enhanced cost optimization techniques following agent-os best practices
        
        # Remove excessive whitespace and empty lines
        lines = [line.strip() for line in prompt.split("\n") if line.strip()]
        optimized = "\n".join(lines)
        
        # Intelligent abbreviation of common words/phrases
        abbreviations = {
            "please provide": "provide",
            "could you please": "please",
            "I would like you to": "please",
            "it is important to": "ensure to",
            "make sure to": "ensure",
            "in order to": "to",
            "with regard to": "regarding",
            "take into consideration": "consider",
            "as a result of": "due to",
            "at this point in time": "now",
            "for the purpose of": "for",
        }
        
        for verbose, concise in abbreviations.items():
            optimized = optimized.replace(verbose, concise)
        
        # Remove redundant filler words while preserving meaning
        filler_patterns = [
            r'\b(actually|basically|essentially|literally)\b',
            r'\b(really|quite|very|extremely) (\w+)',  # Replace with just the word
            r'\b(please note that|it should be noted that|it is worth noting that)\b',
        ]
        
        import re
        for pattern in filler_patterns:
            if r'(\w+)' in pattern:
                # Special handling for intensity words - replace with just the main word
                optimized = re.sub(pattern, r'\2', optimized, flags=re.IGNORECASE)
            else:
                optimized = re.sub(pattern, '', optimized, flags=re.IGNORECASE)
        
        # Clean up any double spaces created by removals
        optimized = re.sub(r'\s+', ' ', optimized).strip()
        
        # Log optimization results
        original_length = len(prompt)
        optimized_length = len(optimized)
        token_savings = original_length - optimized_length
        
        if token_savings > 50:
            logger.debug(
                "Applied cost optimization",
                original_tokens=original_length // 4,  # Rough estimate
                optimized_tokens=optimized_length // 4,
                savings_tokens=(token_savings // 4),
                savings_percent=f"{(token_savings/original_length)*100:.1f}%"
            )
        
        return optimized

    def enhance_context_compression(self, context: ContextualMemory, max_tokens: int = 500) -> None:
        """Enhanced context compression with semantic preservation."""
        # Estimate current context size (rough: 1 token ≈ 4 characters)
        current_size = 0
        
        # Calculate size of all context components
        if context.short_term:
            current_size += sum(len(str(v)) for v in context.short_term.values())
        if context.long_term:
            current_size += sum(len(str(v)) for v in context.long_term.values())
        if context.summary:
            current_size += sum(len(str(v)) for v in context.summary.values())
        
        estimated_tokens = current_size // 4
        
        if estimated_tokens <= max_tokens:
            return  # No compression needed
        
        logger.info(
            "Starting enhanced context compression",
            current_tokens=estimated_tokens,
            target_tokens=max_tokens
        )
        
        # 1. Compress short-term memory using semantic clustering
        if context.short_term:
            context.short_term = self._compress_short_term_semantically(
                context.short_term, max_items=5
            )
        
        # 2. Create intelligent summary from historical data
        if context.long_term:
            summary_text = self._create_intelligent_summary(context.long_term)
            if summary_text:
                context.summary["intelligent_summary"] = summary_text
        
        # 3. Prioritize and compress summary
        if context.summary:
            context.summary = self._compress_summary(context.summary, max_tokens // 4)
        
        # 4. Calculate final compression ratio
        final_size = 0
        if context.short_term:
            final_size += sum(len(str(v)) for v in context.short_term.values())
        if context.summary:
            final_size += sum(len(str(v)) for v in context.summary.values())
        
        final_tokens = final_size // 4
        compression_ratio = 1 - (final_tokens / estimated_tokens) if estimated_tokens > 0 else 0
        
        logger.info(
            "Context compression completed",
            original_tokens=estimated_tokens,
            compressed_tokens=final_tokens,
            compression_ratio=f"{compression_ratio*100:.1f}%"
        )

    def _compress_short_term_semantically(
        self, short_term: dict[str, Any], max_items: int = 5
    ) -> dict[str, Any]:
        """Compress short-term memory using semantic clustering."""
        # Group related items together to preserve relationships
        
        # Define semantic categories
        categories = {
            "actions": ["action", "execute", "run", "perform", "do"],
            "results": ["result", "output", "response", "answer", "outcome"],
            "errors": ["error", "fail", "exception", "problem", "issue"],
            "context": ["context", "background", "setting", "environment"],
            "goals": ["goal", "objective", "target", "aim", "purpose"],
        }
        
        categorized = {}
        uncategorized = {}
        
        # Categorize items
        for key, value in short_term.items():
            categorized_item = False
            key_lower = key.lower()
            value_str = str(value).lower()
            
            for category, keywords in categories.items():
                if any(keyword in key_lower or keyword in value_str for keyword in keywords):
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append((key, value))
                    categorized_item = True
                    break
            
            if not categorized_item:
                uncategorized[key] = value
        
        # Compress within categories
        compressed = {}
        
        for category, items in categorized.items():
            if len(items) == 1:
                # Single item, keep as-is
                key, value = items[0]
                compressed[key] = value
            else:
                # Multiple items, create compressed summary
                summary_parts = []
                for key, value in items:
                    # Keep only essential information
                    if len(str(value)) < 50:
                        summary_parts.append(f"{key}: {value}")
                    else:
                        # Truncate long values
                        summary_parts.append(f"{key}: {str(value)[:47]}...")
                
                compressed[f"{category}_summary"] = " | ".join(summary_parts)
        
        # Add most important uncategorized items
        remaining_slots = max_items - len(compressed)
        if remaining_slots > 0:
            # Sort uncategorized by importance (length as proxy for detail)
            sorted_uncategorized = sorted(
                uncategorized.items(),
                key=lambda x: len(str(x[1])),
                reverse=True
            )
            
            for key, value in sorted_uncategorized[:remaining_slots]:
                compressed[key] = value
        
        return compressed

    def _create_intelligent_summary(self, long_term: dict[str, Any]) -> str:
        """Create an intelligent summary of long-term context."""
        summary_parts = []
        
        # Extract key patterns and frequently mentioned items
        key_patterns = {}
        for key, value in long_term.items():
            # Look for patterns in keys (e.g., user_preference_*, setting_*)
            if "_" in key:
                pattern = key.split("_")[0]
                if pattern not in key_patterns:
                    key_patterns[pattern] = []
                key_patterns[pattern].append((key, value))
            else:
                summary_parts.append(f"{key}: {value}")
        
        # Summarize patterns
        for pattern, items in key_patterns.items():
            if len(items) > 1:
                # Multiple items with same pattern, create summary
                values = [str(item[1]) for item in items]
                summary_parts.append(f"{pattern}_settings: {', '.join(values[:3])}")
            else:
                # Single item
                key, value = items[0]
                summary_parts.append(f"{key}: {value}")
        
        return " | ".join(summary_parts[:5])  # Limit to 5 most important items

    def _compress_summary(self, summary: dict[str, Any], max_tokens: int) -> dict[str, Any]:
        """Compress summary while preserving most important information."""
        # Priority order for summary components
        priority_keys = [
            "intelligent_summary",
            "main_points", 
            "current_objective",
            "recent_context",
            "user_preferences",
            "constraints"
        ]
        
        compressed = {}
        token_budget = max_tokens
        
        for key in priority_keys:
            if key in summary and token_budget > 0:
                value = str(summary[key])
                value_tokens = len(value) // 4
                
                if value_tokens <= token_budget:
                    compressed[key] = value
                    token_budget -= value_tokens
                else:
                    # Truncate to fit budget
                    max_chars = token_budget * 4
                    if max_chars > 20:  # Only include if meaningful
                        compressed[key] = value[:max_chars-3] + "..."
                    break
        
        # Add any remaining important keys if budget allows
        for key, value in summary.items():
            if key not in compressed and token_budget > 10:
                value_str = str(value)
                value_tokens = len(value_str) // 4
                
                if value_tokens <= token_budget:
                    compressed[key] = value_str
                    token_budget -= value_tokens
        
        return compressed


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
