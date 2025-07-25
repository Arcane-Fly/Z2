"""
Basic AI Agent Implementation demonstrating DIE + MIL integration
"""

from typing import Optional
import asyncio
import structlog

from app.agents.die import (
    ContextualMemory, 
    PromptTemplate, 
    DynamicPromptGenerator
)
from app.agents.mil import (
    LLMRequest,
    LLMResponse,
    DynamicModelRouter,
    OpenAIProvider,
    ModelCapability
)

logger = structlog.get_logger(__name__)


class BasicAIAgent:
    """
    A basic AI agent that demonstrates the integration of DIE and MIL.
    
    This shows how the Dynamic Intelligence Engine (DIE) and Model Integration Layer (MIL)
    work together to create an intelligent, context-aware agent.
    """
    
    def __init__(self, agent_name: str, role: str):
        self.name = agent_name
        self.role = role
        
        # Initialize DIE components
        self.prompt_generator = DynamicPromptGenerator()
        self.memory = ContextualMemory(
            short_term={},
            long_term={"agent_name": agent_name, "role": role},
            summary={}
        )
        
        # Initialize MIL components
        self.model_router = DynamicModelRouter()
        
        # Register a default template
        self._setup_default_templates()
        
        logger.info("Basic AI agent initialized", agent_name=agent_name, role=role)
    
    def _setup_default_templates(self):
        """Set up default prompt templates."""
        
        # General conversation template
        conversation_template = PromptTemplate(
            role="You are {agent_name}, a {role}",
            task="Respond to the user's message: {user_message}",
            format="Provide a helpful and contextually appropriate response"
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
                "Suggest actionable next steps if appropriate"
            ]
        )
        
        self.prompt_generator.register_template("analysis", analysis_template)
    
    def setup_llm_provider(self, api_key: str):
        """Set up LLM provider for the agent."""
        try:
            openai_provider = OpenAIProvider(api_key=api_key)
            self.model_router.register_provider("openai", openai_provider)
            logger.info("OpenAI provider registered successfully")
        except ImportError as e:
            logger.warning("Could not set up OpenAI provider", error=str(e))
        except Exception as e:
            logger.error("Failed to set up OpenAI provider", error=str(e))
    
    async def process_message(
        self, 
        user_message: str, 
        template_name: str = "conversation",
        model_preference: Optional[str] = None
    ) -> str:
        """
        Process a user message using DIE + MIL integration.
        
        This demonstrates how context flows through the system:
        1. Update contextual memory with new input
        2. Generate dynamic prompt using DIE
        3. Route to optimal model using MIL  
        4. Update context with response
        """
        
        # Update short-term context
        self.memory.update_context({
            "last_user_message": user_message,
            "template_used": template_name,
            "timestamp": str(asyncio.get_event_loop().time())
        })
        
        try:
            # Generate dynamic prompt using DIE
            prompt = self.prompt_generator.generate_prompt(
                template_name=template_name,
                variables={
                    "agent_name": self.name,
                    "role": self.role,
                    "user_message": user_message,
                    "content": user_message  # For analysis template
                },
                context=self.memory,
                agent_role=self.role,
                target_model=model_preference or "gpt-4.1-mini"
            )
            
            logger.debug("Generated prompt", template=template_name, prompt_length=len(prompt))
            
            # Check if we have any providers registered
            if not self.model_router.providers:
                logger.warning("No LLM providers available, returning mock response")
                response_content = f"[Mock Response] As {self.name}, I would respond to: {user_message}"
            else:
                # Create LLM request
                llm_request = LLMRequest(
                    prompt=prompt,
                    model_id=model_preference,
                    max_tokens=150,
                    temperature=0.7
                )
                
                # Route through MIL (this would normally call the actual LLM)
                # For now, we'll just demonstrate the structure
                logger.info("Would route request through MIL", model=model_preference)
                
                # Simulate response for demonstration
                response_content = f"[Demo Response] As {self.name}, I understand you said: '{user_message}'. This demonstrates the DIE+MIL integration working together."
            
            # Update context with response
            current_count = self.memory.short_term.get("interaction_count", 0)
            self.memory.update_context({
                "last_response": response_content,
                "interaction_count": current_count + 1
            })
            
            # Check if we need to compress context (after all updates)
            if len(self.memory.short_term) > 8:  # Lower threshold for testing
                logger.debug("Compressing context", items=len(self.memory.short_term))
                self.memory.compress_to_summary()
            
            return response_content
            
        except Exception as e:
            logger.error("Failed to process message", error=str(e))
            return f"I apologize, but I encountered an error processing your message: {str(e)}"
    
    def get_context_summary(self) -> dict:
        """Get a summary of the agent's current context."""
        return {
            "agent_name": self.name,
            "role": self.role,
            "short_term_items": len(self.memory.short_term),
            "long_term_items": len(self.memory.long_term),
            "summary_items": len(self.memory.summary),
            "interaction_count": self.memory.short_term.get("interaction_count", 0)
        }


# Example usage function for demonstration
async def demo_agent_interaction():
    """Demonstrate the basic AI agent functionality."""
    
    # Create an agent
    agent = BasicAIAgent("Alice", "research assistant")
    
    # Process some messages
    response1 = await agent.process_message("Hello, can you help me with data analysis?")
    print(f"Response 1: {response1}")
    
    response2 = await agent.process_message("What are the key trends in AI?", template_name="analysis")
    print(f"Response 2: {response2}")
    
    # Show context summary
    context = agent.get_context_summary()
    print(f"Agent context: {context}")
    
    return agent


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_agent_interaction())