"""
Basic AI Agent Implementation with Enhanced Prompting
Demonstrates DIE + MIL integration with dramatically improved prompts for superior AI performance.
"""

import asyncio
from typing import Optional

import structlog

from app.agents.die import ContextualMemory, DynamicPromptGenerator, PromptTemplate
from app.agents.mil import (
    DynamicModelRouter,
    LLMRequest,
    LLMResponse,
    ModelIntegrationLayer,
    RoutingPolicy,
)
from app.core.cache_and_rate_limit import get_cache, get_rate_limiter
from app.core.config import settings
from app.core.enhanced_prompts import (
    EnhancedPromptLibrary, 
    PromptEnhancer, 
    EnhancedPromptTemplate
)

logger = structlog.get_logger(__name__)


class BasicAIAgent:
    """
    A basic AI agent that demonstrates the integration of DIE and MIL.

    This shows how the Dynamic Intelligence Engine (DIE) and Model Integration Layer (MIL)
    work together to create an intelligent, context-aware agent with real LLM integration.
    """

    def __init__(self, agent_name: str, role: str):
        self.name = agent_name
        self.role = role

        # Initialize DIE components with enhanced prompting
        self.prompt_generator = DynamicPromptGenerator()
        self.memory = ContextualMemory(
            short_term={},
            long_term={"agent_name": agent_name, "role": role},
            summary={},
        )

        # Initialize enhanced prompt system
        self.enhanced_template = EnhancedPromptLibrary.get_template_by_role(role)
        self.prompt_enhancer = PromptEnhancer()
        
        # Initialize MIL components
        self.mil = ModelIntegrationLayer()
        
        # Track usage statistics
        self.total_requests = 0
        self.total_cost = 0.0
        self.total_tokens = 0

        # Register default templates (legacy + enhanced)
        self._setup_default_templates()

        logger.info("Basic AI agent initialized", agent_name=agent_name, role=role)

    def _setup_default_templates(self):
        """Set up default prompt templates."""

        # General conversation template
        conversation_template = PromptTemplate(
            role="You are {agent_name}, a {role}",
            task="Respond to the user's message: {user_message}",
            format="Provide a helpful and contextually appropriate response",
        )

        self.prompt_generator.register_template("conversation", conversation_template)

        # Analysis template
        analysis_template = PromptTemplate(
            role="You are {agent_name}, an expert {role}",
            task="Analyze the following content: {content}",
            format="Provide your analysis in a structured format with key insights",
            constraints=[
                "Be objective and evidence-based",
                "Highlight key findings clearly",
                "Suggest actionable next steps if appropriate",
            ],
        )

        self.prompt_generator.register_template("analysis", analysis_template)

    async def process_message(
        self,
        user_message: str,
        template_name: str = "conversation",
        model_preference: Optional[str] = None,
        use_cache: bool = True,
    ) -> str:
        """
        Process a user message using DIE + MIL integration with real LLM calls.

        This demonstrates how context flows through the system:
        1. Update contextual memory with new input
        2. Generate dynamic prompt using DIE
        3. Check cache for previous similar requests
        4. Apply rate limiting
        5. Route to optimal model using MIL
        6. Make actual LLM API call
        7. Cache response and update context
        """

        # Update short-term context
        self.memory.update_context(
            {
                "last_user_message": user_message,
                "template_used": template_name,
                "timestamp": str(asyncio.get_event_loop().time()),
            }
        )

        try:
            # Generate dynamic prompt using DIE
            prompt = self.prompt_generator.generate_prompt(
                template_name=template_name,
                variables={
                    "agent_name": self.name,
                    "role": self.role,
                    "user_message": user_message,
                    "content": user_message,  # For analysis template
                },
                context=self.memory,
                agent_role=self.role,
                target_model=model_preference or settings.default_model,
            )

            logger.debug(
                "Generated prompt", template=template_name, prompt_length=len(prompt)
            )

            # Create LLM request
            llm_request = LLMRequest(
                prompt=prompt,
                model_id=model_preference,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
            )

            # Check cache first if enabled
            cache = await get_cache()
            cached_response = None
            
            if use_cache:
                cached_response = await cache.get(
                    prompt=prompt,
                    model_id=model_preference or settings.default_model,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                )

            if cached_response:
                logger.info("Using cached response")
                response_content = cached_response.get("content", "")
                
                # Update context with cached response
                current_count = self.memory.short_term.get("interaction_count", 0)
                self.memory.update_context(
                    {
                        "last_response": response_content,
                        "interaction_count": current_count + 1,
                        "response_cached": True,
                    }
                )
            else:
                # Check if we have any providers available
                if not self.mil.router.providers:
                    logger.warning("No LLM providers available, using fallback response")
                    response_content = f"I apologize, but no LLM providers are currently configured. As {self.name}, I would respond to: {user_message}"
                else:
                    # Check rate limits
                    rate_limiter = await get_rate_limiter()
                    
                    # Estimate cost for rate limiting
                    estimated_tokens = len(prompt) // 4  # Rough token estimate
                    estimated_cost = estimated_tokens * 0.001  # Rough cost estimate
                    
                    allowed, rate_info = await rate_limiter.check_rate_limit(
                        provider="default",
                        model_id=model_preference or settings.default_model,
                        estimated_cost=estimated_cost,
                    )
                    
                    if not allowed:
                        logger.warning("Rate limit exceeded", rate_info=rate_info)
                        response_content = f"I apologize, but I'm currently rate-limited. Please try again in a moment."
                    else:
                        # Make actual LLM API call through MIL
                        try:
                            response: LLMResponse = await self.mil.generate_response(
                                request=llm_request,
                                policy=RoutingPolicy(
                                    cost_weight=0.3,
                                    latency_weight=0.4,
                                    quality_weight=0.3,
                                ),
                            )
                            
                            response_content = response.content
                            
                            # Update usage statistics
                            self.total_requests += 1
                            self.total_cost += response.cost_usd
                            self.total_tokens += response.tokens_used
                            
                            # Record usage for rate limiting
                            await rate_limiter.record_usage(
                                provider=response.provider,
                                model_id=response.model_used,
                                actual_cost=response.cost_usd,
                                tokens_used=response.tokens_used,
                            )
                            
                            # Cache the response if successful
                            if use_cache and response_content:
                                await cache.set(
                                    prompt=prompt,
                                    model_id=response.model_used,
                                    response_data={
                                        "content": response_content,
                                        "model_used": response.model_used,
                                        "provider": response.provider,
                                        "cost_usd": response.cost_usd,
                                        "tokens_used": response.tokens_used,
                                    },
                                    temperature=settings.temperature,
                                    max_tokens=settings.max_tokens,
                                )
                            
                            logger.info(
                                "LLM response generated",
                                model=response.model_used,
                                provider=response.provider,
                                tokens=response.tokens_used,
                                cost=response.cost_usd,
                                latency=response.latency_ms,
                            )
                        
                        except Exception as e:
                            logger.error("LLM API call failed", error=str(e))
                            response_content = f"I apologize, but I encountered an error while processing your request. As {self.name}, I understand you said: '{user_message}'. Please try again or rephrase your request."

                # Update context with response
                current_count = self.memory.short_term.get("interaction_count", 0)
                self.memory.update_context(
                    {
                        "last_response": response_content,
                        "interaction_count": current_count + 1,
                        "response_cached": False,
                    }
                )

            # Check if we need to compress context (after all updates)
            if len(self.memory.short_term) > 8:  # Lower threshold for testing
                logger.debug("Compressing context", items=len(self.memory.short_term))
                self.memory.compress_to_summary()

            return response_content

        except Exception as e:
            logger.error("Failed to process message", error=str(e))
            return f"I apologize, but I encountered an error processing your message: {str(e)}"

    async def process_message_enhanced(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        model_preference: Optional[str] = None,
        use_cache: bool = True,
    ) -> str:
        """
        Process a message using dramatically improved prompts for superior AI performance.
        
        This method uses the enhanced prompt system with advanced reasoning frameworks,
        structured thinking, and sophisticated prompt engineering techniques.
        """
        try:
            # Prepare variables for enhanced prompt
            variables = {
                "agent_name": self.agent_name,
                "role": self.role,
                "user_message": user_message,
                "context": context or self.memory.get_full_context(),
            }
            
            # Generate enhanced prompt
            enhanced_prompt = self.prompt_enhancer.apply_techniques(
                self.enhanced_template, 
                variables
            )
            
            # Optimize for the specific model
            if model_preference:
                enhanced_prompt = self.prompt_enhancer.optimize_for_model(
                    enhanced_prompt, 
                    model_preference
                )
            
            logger.info("Generated enhanced prompt", 
                       agent_name=self.agent_name,
                       prompt_length=len(enhanced_prompt),
                       template_name=self.enhanced_template.name)
            
            # Create LLM request with enhanced prompt
            request = LLMRequest(
                prompt=enhanced_prompt,
                task_type=self._determine_task_type(user_message),
                max_tokens=2048,
                temperature=0.7,
                context=variables
            )
            
            # Use MIL to route and execute
            response = await self.mil.route_and_execute(request, preferred_model=model_preference)
            
            if response and response.content:
                # Update memory with enhanced interaction
                self.memory.update_context({
                    "last_enhanced_prompt": enhanced_prompt[:200] + "...",
                    "last_response": response.content,
                    "enhanced_template_used": self.enhanced_template.name,
                    "model_used": response.model_used,
                    "timestamp": str(asyncio.get_event_loop().time()),
                })
                
                # Update statistics
                self.total_requests += 1
                self.total_cost += getattr(response, 'cost', 0.0)
                self.total_tokens += getattr(response, 'total_tokens', 0)
                
                logger.info("Enhanced message processed successfully",
                           agent_name=self.agent_name,
                           model_used=response.model_used,
                           response_length=len(response.content))
                
                return response.content
            else:
                # Enhanced fallback response
                fallback = f"""As {self.agent_name}, I understand you're asking: "{user_message}"

I apologize, but I'm experiencing technical difficulties at the moment. However, based on my expertise in {self.role}, I can offer this preliminary insight:

This appears to be a question that would benefit from careful analysis. I'd recommend breaking it down into key components and considering multiple perspectives to develop a comprehensive response.

Please try your request again, and I'll be better able to provide the detailed, thoughtful response you deserve."""
                
                return fallback
                
        except Exception as e:
            logger.error("Enhanced message processing failed", 
                        error=str(e), agent_name=self.agent_name)
            
            # Enhanced error response
            return f"""As {self.agent_name}, I apologize for the technical difficulty in processing your message: "{user_message}"

While I'm currently experiencing some challenges, I want to acknowledge that your question deserves a thoughtful response. Please try rephrasing your request, and I'll do my best to provide you with the insights you're looking for.

Technical note: {str(e)}"""

    def _determine_task_type(self, message: str) -> str:
        """Determine the type of task based on the message content."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["analyze", "analysis", "examine", "evaluate"]):
            return "analysis"
        elif any(word in message_lower for word in ["research", "investigate", "find", "search"]):
            return "research"
        elif any(word in message_lower for word in ["solve", "problem", "issue", "fix"]):
            return "problem_solving"
        elif any(word in message_lower for word in ["explain", "describe", "what", "how"]):
            return "explanation"
        else:
            return "general_conversation"

    def get_context_summary(self) -> dict:
        """Get a summary of the agent's current context."""
        return {
            "agent_name": self.name,
            "role": self.role,
            "short_term_items": len(self.memory.short_term),
            "long_term_items": len(self.memory.long_term),
            "summary_items": len(self.memory.summary),
            "interaction_count": self.memory.short_term.get("interaction_count", 0),
            "total_requests": self.total_requests,
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
        }

    def get_usage_stats(self) -> dict:
        """Get detailed usage statistics for the agent."""
        return {
            "total_requests": self.total_requests,
            "total_cost_usd": round(self.total_cost, 4),
            "total_tokens": self.total_tokens,
            "average_cost_per_request": (
                round(self.total_cost / self.total_requests, 4) 
                if self.total_requests > 0 else 0.0
            ),
            "average_tokens_per_request": (
                round(self.total_tokens / self.total_requests, 2) 
                if self.total_requests > 0 else 0.0
            ),
        }


# Example usage function for demonstration
async def demo_agent_interaction():
    """Demonstrate the basic AI agent functionality with real LLM integration."""

    # Create an agent
    agent = BasicAIAgent("Alice", "research assistant")

    # Process some messages
    print("Demo: Processing first message...")
    response1 = await agent.process_message(
        "Hello, can you help me understand machine learning?"
    )
    print(f"Response 1: {response1}")

    print("\nDemo: Processing analysis request...")
    response2 = await agent.process_message(
        "What are the key trends in AI for 2025?", template_name="analysis"
    )
    print(f"Response 2: {response2}")

    # Show context summary and usage stats
    context = agent.get_context_summary()
    usage = agent.get_usage_stats()
    print(f"\nAgent context: {context}")
    print(f"Usage stats: {usage}")

    # Get cache stats
    cache = await get_cache()
    cache_stats = cache.get_stats()
    print(f"Cache stats: {cache_stats}")

    return agent


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_agent_interaction())
