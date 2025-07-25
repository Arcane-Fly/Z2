"""
Model Integration Layer (MIL) Core Module

The MIL provides a standardized interface for all LLM providers, dynamic model routing,
and cost optimization as specified in the Z2 requirements.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import asyncio
import time
import structlog

from app.core.config import settings


logger = structlog.get_logger(__name__)


class ModelCapability(Enum):
    """Enumeration of model capabilities."""
    TEXT_GENERATION = "text_generation"
    FUNCTION_CALLING = "function_calling"
    STRUCTURED_OUTPUT = "structured_output"
    WEB_SEARCH = "web_search"
    IMAGE_INPUT = "image_input"
    CODE_GENERATION = "code_generation"
    LONG_CONTEXT = "long_context"


@dataclass
class ModelInfo:
    """Information about a specific model."""
    
    id: str
    provider: str
    name: str
    description: str
    capabilities: List[ModelCapability]
    context_window: int
    input_cost_per_million_tokens: float
    output_cost_per_million_tokens: float
    max_tokens_per_minute: Optional[int] = None
    avg_latency_ms: Optional[float] = None
    quality_score: Optional[float] = None  # 0-1 rating
    
    def has_capability(self, capability: ModelCapability) -> bool:
        """Check if this model has a specific capability."""
        return capability in self.capabilities


@dataclass
class LLMRequest:
    """Standardized request format for all LLM providers."""
    
    prompt: str
    model_id: Optional[str] = None  # If None, will be routed dynamically
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stop_sequences: Optional[List[str]] = None
    functions: Optional[List[Dict[str, Any]]] = None
    response_format: Optional[str] = None  # "json", "text", etc.
    metadata: Dict[str, Any] = None


@dataclass
class LLMResponse:
    """Standardized response format from all LLM providers."""
    
    content: str
    model_used: str
    provider: str
    tokens_used: int
    cost_usd: float
    latency_ms: float
    finish_reason: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using the provider's API."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from this provider."""
        pass
    
    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """Calculate cost for token usage."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package is required for OpenAI provider")
        
        self.models = {
            "gpt-4.1": ModelInfo(
                id="gpt-4.1",
                provider="openai",
                name="GPT-4.1",
                description="Most capable model for complex reasoning",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STRUCTURED_OUTPUT,
                    ModelCapability.WEB_SEARCH,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.LONG_CONTEXT,
                ],
                context_window=1_000_000,
                input_cost_per_million_tokens=5.00,
                output_cost_per_million_tokens=15.00,
                quality_score=0.95,
            ),
            "gpt-4.1-mini": ModelInfo(
                id="gpt-4.1-mini",
                provider="openai",
                name="GPT-4.1 Mini",
                description="Fast and cost-effective model",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STRUCTURED_OUTPUT,
                    ModelCapability.CODE_GENERATION,
                ],
                context_window=1_000_000,
                input_cost_per_million_tokens=0.15,
                output_cost_per_million_tokens=0.60,
                quality_score=0.85,
            ),
        }
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API."""
        start_time = time.time()
        
        # Prepare messages
        messages = [{"role": "user", "content": request.prompt}]
        
        # Prepare request parameters
        params = {
            "model": request.model_id or "gpt-4.1-mini",
            "messages": messages,
            "max_tokens": request.max_tokens or settings.max_tokens,
            "temperature": request.temperature or settings.temperature,
        }
        
        if request.top_p:
            params["top_p"] = request.top_p
        
        if request.stop_sequences:
            params["stop"] = request.stop_sequences
        
        if request.functions:
            params["tools"] = [{"type": "function", "function": func} for func in request.functions]
        
        if request.response_format == "json":
            params["response_format"] = {"type": "json_object"}
        
        try:
            response = await self.client.chat.completions.create(**params)
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response data
            message = response.choices[0].message
            content = message.content or ""
            
            # Calculate cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self.calculate_cost(input_tokens, output_tokens, params["model"])
            
            # Handle function calls
            function_calls = None
            if message.tool_calls:
                function_calls = [
                    {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                        "id": call.id,
                    }
                    for call in message.tool_calls
                ]
            
            return LLMResponse(
                content=content,
                model_used=params["model"],
                provider="openai",
                tokens_used=response.usage.total_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason,
                function_calls=function_calls,
                metadata={"usage": response.usage.model_dump()},
            )
            
        except Exception as e:
            logger.error("OpenAI API error", error=str(e), model=params["model"])
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get available OpenAI models."""
        return list(self.models.values())
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """Calculate cost for OpenAI usage."""
        if model_id not in self.models:
            logger.warning("Unknown model for cost calculation", model=model_id)
            return 0.0
        
        model_info = self.models[model_id]
        input_cost = (input_tokens / 1_000_000) * model_info.input_cost_per_million_tokens
        output_cost = (output_tokens / 1_000_000) * model_info.output_cost_per_million_tokens
        
        return input_cost + output_cost


class AnthropicProvider(LLMProvider):
    """Anthropic provider implementation."""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package is required for Anthropic provider")
        
        self.models = {
            "claude-3.5-sonnet": ModelInfo(
                id="claude-3.5-sonnet",
                provider="anthropic",
                name="Claude 3.5 Sonnet",
                description="High-performance model balancing speed and intelligence",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.LONG_CONTEXT,
                ],
                context_window=200_000,
                input_cost_per_million_tokens=3.00,
                output_cost_per_million_tokens=15.00,
                quality_score=0.92,
            ),
        }
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic API."""
        start_time = time.time()
        
        params = {
            "model": request.model_id or "claude-3.5-sonnet",
            "max_tokens": request.max_tokens or settings.max_tokens,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        
        if request.temperature:
            params["temperature"] = request.temperature
        
        if request.top_p:
            params["top_p"] = request.top_p
        
        if request.stop_sequences:
            params["stop_sequences"] = request.stop_sequences
        
        try:
            response = await self.client.messages.create(**params)
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract content
            content = "".join([block.text for block in response.content if hasattr(block, 'text')])
            
            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self.calculate_cost(input_tokens, output_tokens, params["model"])
            
            return LLMResponse(
                content=content,
                model_used=params["model"],
                provider="anthropic",
                tokens_used=input_tokens + output_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                finish_reason=response.stop_reason,
                metadata={"usage": response.usage.model_dump()},
            )
            
        except Exception as e:
            logger.error("Anthropic API error", error=str(e), model=params["model"])
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get available Anthropic models."""
        return list(self.models.values())
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """Calculate cost for Anthropic usage."""
        if model_id not in self.models:
            logger.warning("Unknown model for cost calculation", model=model_id)
            return 0.0
        
        model_info = self.models[model_id]
        input_cost = (input_tokens / 1_000_000) * model_info.input_cost_per_million_tokens
        output_cost = (output_tokens / 1_000_000) * model_info.output_cost_per_million_tokens
        
        return input_cost + output_cost


class GroqProvider(LLMProvider):
    """Groq provider implementation for high-speed inference."""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        try:
            import groq
            self.client = groq.AsyncGroq(api_key=api_key)
        except ImportError:
            raise ImportError("groq package is required for Groq provider")
        
        self.models = {
            "llama-3.3-70b-versatile": ModelInfo(
                id="llama-3.3-70b-versatile",
                provider="groq",
                name="Llama 3.3 70B Versatile",
                description="High-speed inference optimized model",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STRUCTURED_OUTPUT,
                    ModelCapability.CODE_GENERATION,
                ],
                context_window=8192,
                input_cost_per_million_tokens=0.59,
                output_cost_per_million_tokens=0.79,
                max_tokens_per_minute=280_000,
                avg_latency_ms=50,
                quality_score=0.82,
            ),
            "llama-3.3-70b-specdec": ModelInfo(
                id="llama-3.3-70b-specdec",
                provider="groq",
                name="Llama 3.3 70B SpecDec",
                description="Extreme speed with speculative decoding",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STRUCTURED_OUTPUT,
                ],
                context_window=8192,
                input_cost_per_million_tokens=0.59,
                output_cost_per_million_tokens=0.79,
                max_tokens_per_minute=1_600_000,
                avg_latency_ms=25,
                quality_score=0.80,
            ),
        }
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Groq API."""
        start_time = time.time()
        
        params = {
            "model": request.model_id or "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens or settings.max_tokens,
        }
        
        if request.temperature:
            params["temperature"] = request.temperature
        
        if request.top_p:
            params["top_p"] = request.top_p
        
        if request.stop_sequences:
            params["stop"] = request.stop_sequences
        
        if request.functions:
            params["tools"] = [{"type": "function", "function": func} for func in request.functions]
        
        if request.response_format == "json":
            params["response_format"] = {"type": "json_object"}
        
        try:
            response = await self.client.chat.completions.create(**params)
            
            latency_ms = (time.time() - start_time) * 1000
            
            message = response.choices[0].message
            content = message.content or ""
            
            # Calculate cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self.calculate_cost(input_tokens, output_tokens, params["model"])
            
            return LLMResponse(
                content=content,
                model_used=params["model"],
                provider="groq",
                tokens_used=response.usage.total_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason,
                metadata={"usage": response.usage.model_dump()},
            )
            
        except Exception as e:
            logger.error("Groq API error", error=str(e), model=params["model"])
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get available Groq models."""
        return list(self.models.values())
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """Calculate cost for Groq usage."""
        if model_id not in self.models:
            logger.warning("Unknown model for cost calculation", model=model_id)
            return 0.0
        
        model_info = self.models[model_id]
        input_cost = (input_tokens / 1_000_000) * model_info.input_cost_per_million_tokens
        output_cost = (output_tokens / 1_000_000) * model_info.output_cost_per_million_tokens
        
        return input_cost + output_cost


@dataclass
class RoutingPolicy:
    """Configuration for dynamic model routing."""
    
    cost_weight: float = 0.3          # Weight for cost optimization
    latency_weight: float = 0.4       # Weight for latency optimization
    quality_weight: float = 0.3       # Weight for quality optimization
    prefer_provider: Optional[str] = None  # Preferred provider
    max_cost_per_request: Optional[float] = None  # Cost limit
    max_latency_ms: Optional[float] = None  # Latency limit
    required_capabilities: List[ModelCapability] = None  # Required capabilities


class DynamicModelRouter:
    """Intelligent model routing based on task requirements and policies."""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.models: Dict[str, ModelInfo] = {}
        self.performance_history: Dict[str, List[float]] = {}
        
    def register_provider(self, name: str, provider: LLMProvider) -> None:
        """Register a new LLM provider."""
        self.providers[name] = provider
        
        # Register all models from this provider
        for model in provider.get_available_models():
            full_model_id = f"{name}/{model.id}"
            self.models[full_model_id] = model
            self.performance_history[full_model_id] = []
        
        logger.info("Registered LLM provider", provider=name, models=len(provider.get_available_models()))
    
    def get_optimal_model(
        self,
        request: LLMRequest,
        policy: RoutingPolicy,
    ) -> str:
        """Select the optimal model based on request and routing policy."""
        
        # Filter models by required capabilities
        candidates = self._filter_by_capabilities(request, policy)
        
        if not candidates:
            logger.warning("No models match requirements, using default")
            return settings.default_model
        
        # Filter by constraints
        candidates = self._filter_by_constraints(candidates, policy)
        
        if not candidates:
            logger.warning("No models meet constraints, using best available")
            candidates = list(self.models.keys())
        
        # Score and rank candidates
        scored_models = []
        for model_id in candidates:
            score = self._calculate_model_score(model_id, request, policy)
            scored_models.append((model_id, score))
        
        # Sort by score (higher is better)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        selected_model = scored_models[0][0]
        
        logger.info(
            "Selected optimal model",
            model=selected_model,
            score=scored_models[0][1],
            alternatives=len(scored_models) - 1,
        )
        
        return selected_model
    
    def _filter_by_capabilities(
        self, 
        request: LLMRequest, 
        policy: RoutingPolicy
    ) -> List[str]:
        """Filter models by required capabilities."""
        required_caps = policy.required_capabilities or []
        
        # Add capabilities based on request features
        if request.functions:
            required_caps.append(ModelCapability.FUNCTION_CALLING)
        
        if request.response_format == "json":
            required_caps.append(ModelCapability.STRUCTURED_OUTPUT)
        
        # Estimate if long context is needed
        estimated_tokens = len(request.prompt) // 4  # Rough estimate
        if estimated_tokens > 16_000:
            required_caps.append(ModelCapability.LONG_CONTEXT)
        
        if not required_caps:
            return list(self.models.keys())
        
        candidates = []
        for model_id, model_info in self.models.items():
            if all(cap in model_info.capabilities for cap in required_caps):
                candidates.append(model_id)
        
        return candidates
    
    def _filter_by_constraints(
        self, 
        candidates: List[str], 
        policy: RoutingPolicy
    ) -> List[str]:
        """Filter models by policy constraints."""
        filtered = []
        
        for model_id in candidates:
            model_info = self.models[model_id]
            
            # Check cost constraint
            if policy.max_cost_per_request:
                # Estimate cost based on prompt length
                estimated_tokens = len("dummy prompt") // 4  # This would be actual request
                estimated_cost = model_info.input_cost_per_million_tokens * (estimated_tokens / 1_000_000)
                if estimated_cost > policy.max_cost_per_request:
                    continue
            
            # Check latency constraint
            if policy.max_latency_ms and model_info.avg_latency_ms:
                if model_info.avg_latency_ms > policy.max_latency_ms:
                    continue
            
            # Check provider preference
            if policy.prefer_provider and model_info.provider != policy.prefer_provider:
                # Don't exclude, just deprioritize in scoring
                pass
            
            filtered.append(model_id)
        
        return filtered
    
    def _calculate_model_score(
        self,
        model_id: str,
        request: LLMRequest,
        policy: RoutingPolicy,
    ) -> float:
        """Calculate a score for model selection."""
        model_info = self.models[model_id]
        
        # Normalize scores to 0-1 range
        cost_score = self._normalize_cost_score(model_info)
        latency_score = self._normalize_latency_score(model_info)
        quality_score = model_info.quality_score or 0.5
        
        # Apply provider preference bonus
        provider_bonus = 0.1 if policy.prefer_provider == model_info.provider else 0.0
        
        # Calculate weighted score
        total_score = (
            cost_score * policy.cost_weight +
            latency_score * policy.latency_weight +
            quality_score * policy.quality_weight +
            provider_bonus
        )
        
        return total_score
    
    def _normalize_cost_score(self, model_info: ModelInfo) -> float:
        """Normalize cost to 0-1 score (lower cost = higher score)."""
        # Get all costs for normalization
        all_costs = [m.input_cost_per_million_tokens for m in self.models.values()]
        min_cost = min(all_costs)
        max_cost = max(all_costs)
        
        if max_cost == min_cost:
            return 1.0
        
        # Invert so lower cost = higher score
        normalized = 1.0 - (model_info.input_cost_per_million_tokens - min_cost) / (max_cost - min_cost)
        return max(0.0, min(1.0, normalized))
    
    def _normalize_latency_score(self, model_info: ModelInfo) -> float:
        """Normalize latency to 0-1 score (lower latency = higher score)."""
        if not model_info.avg_latency_ms:
            return 0.5  # Unknown latency gets neutral score
        
        # Get all latencies for normalization
        all_latencies = [m.avg_latency_ms for m in self.models.values() if m.avg_latency_ms]
        
        if not all_latencies:
            return 0.5
        
        min_latency = min(all_latencies)
        max_latency = max(all_latencies)
        
        if max_latency == min_latency:
            return 1.0
        
        # Invert so lower latency = higher score
        normalized = 1.0 - (model_info.avg_latency_ms - min_latency) / (max_latency - min_latency)
        return max(0.0, min(1.0, normalized))
    
    async def route_request(
        self,
        request: LLMRequest,
        policy: RoutingPolicy,
    ) -> LLMResponse:
        """Route request to optimal model and execute."""
        
        # Select optimal model if not specified
        if not request.model_id:
            request.model_id = self.get_optimal_model(request, policy)
        
        # Extract provider from model ID
        if "/" in request.model_id:
            provider_name, model_id = request.model_id.split("/", 1)
        else:
            # Fallback: find provider that has this model
            provider_name = None
            for name, provider in self.providers.items():
                available_models = [m.id for m in provider.get_available_models()]
                if request.model_id in available_models:
                    provider_name = name
                    model_id = request.model_id
                    break
            
            if not provider_name:
                raise ValueError(f"Model {request.model_id} not found in any provider")
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not registered")
        
        # Update request with actual model ID
        request.model_id = model_id
        
        # Execute request
        provider = self.providers[provider_name]
        response = await provider.generate(request)
        
        # Update performance history
        full_model_id = f"{provider_name}/{model_id}"
        if full_model_id in self.performance_history:
            self.performance_history[full_model_id].append(response.latency_ms)
            # Keep only last 100 measurements
            self.performance_history[full_model_id] = self.performance_history[full_model_id][-100:]
        
        return response


class ModelIntegrationLayer:
    """Main MIL class that orchestrates all model integration components."""
    
    def __init__(self):
        self.router = DynamicModelRouter()
        self.default_policy = RoutingPolicy()
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize all configured LLM providers."""
        
        # OpenAI
        if settings.openai_api_key:
            provider = OpenAIProvider(settings.openai_api_key)
            self.router.register_provider("openai", provider)
        
        # Anthropic
        if settings.anthropic_api_key:
            provider = AnthropicProvider(settings.anthropic_api_key)
            self.router.register_provider("anthropic", provider)
        
        # Groq
        if settings.groq_api_key:
            provider = GroqProvider(settings.groq_api_key)
            self.router.register_provider("groq", provider)
        
        # TODO: Add Google and Perplexity providers
        
        logger.info("Initialized MIL providers", count=len(self.router.providers))
    
    async def generate_response(
        self,
        request: LLMRequest,
        policy: Optional[RoutingPolicy] = None,
    ) -> LLMResponse:
        """Generate response using optimal model routing."""
        
        routing_policy = policy or self.default_policy
        
        try:
            response = await self.router.route_request(request, routing_policy)
            
            logger.info(
                "Generated LLM response",
                model=response.model_used,
                provider=response.provider,
                tokens=response.tokens_used,
                cost=response.cost_usd,
                latency=response.latency_ms,
            )
            
            return response
            
        except Exception as e:
            logger.error("Failed to generate LLM response", error=str(e))
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get all available models across providers."""
        return list(self.router.models.values())
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        status = {}
        for name, provider in self.router.providers.items():
            try:
                models = provider.get_available_models()
                status[name] = {
                    "status": "healthy",
                    "models": len(models),
                    "model_list": [m.id for m in models],
                }
            except Exception as e:
                status[name] = {
                    "status": "error",
                    "error": str(e),
                }
        
        return status
    
    def update_routing_policy(self, policy: RoutingPolicy) -> None:
        """Update the default routing policy."""
        self.default_policy = policy
        logger.info("Updated default routing policy")