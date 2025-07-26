"""
Comprehensive unit tests for LLM provider integration and model routing.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.basic_agent import BasicAIAgent
from app.agents.mil import (
    AnthropicProvider,
    DynamicModelRouter,
    LLMRequest,
    LLMResponse,
    ModelInfo,
    ModelIntegrationLayer,
    OpenAIProvider,
    RoutingPolicy,
)
from app.agents.mil import ModelCapability as MILModelCapability
from app.core.cache_and_rate_limit import LLMResponseCache, RateLimiter
from app.core.models_registry import (
    ALL_MODELS,
    get_model_by_id,
    get_models_by_capability,
    get_models_by_provider,
    ProviderType,
    validate_model_support,
)
from app.core.models_registry import ModelCapability


class TestModelRegistry:
    """Test the enhanced model registry functionality."""

    def test_model_registry_completeness(self):
        """Test that all models have required metadata."""
        for model_id, spec in ALL_MODELS.items():
            assert spec.model_id == model_id
            assert spec.provider in [ProviderType.OPENAI, ProviderType.ANTHROPIC, ProviderType.XAI]
            assert spec.name
            assert spec.description
            assert len(spec.capabilities) > 0
            # Note: Some models like Whisper have 0 token limits by design
            assert spec.input_token_limit >= 0
            assert spec.output_token_limit >= 0
            
            # Check that key models have cost and context window data
            if model_id in ["gpt-4.1", "gpt-4.1-mini", "o4-mini", "claude-sonnet-4-20250514"]:
                assert spec.cost_per_input_token is not None
                assert spec.cost_per_output_token is not None
                assert spec.context_window is not None

    def test_get_model_by_id(self):
        """Test retrieving models by ID."""
        model = get_model_by_id("gpt-4.1")
        assert model is not None
        assert model.name == "GPT-4.1"
        
        model = get_model_by_id("nonexistent-model")
        assert model is None

    def test_get_models_by_provider(self):
        """Test filtering models by provider."""
        openai_models = get_models_by_provider(ProviderType.OPENAI)
        assert len(openai_models) > 0
        assert all(spec.provider == ProviderType.OPENAI for spec in openai_models.values())
        
        anthropic_models = get_models_by_provider(ProviderType.ANTHROPIC)
        assert len(anthropic_models) > 0
        assert all(spec.provider == ProviderType.ANTHROPIC for spec in anthropic_models.values())

    def test_get_models_by_capability(self):
        """Test filtering models by capability."""
        reasoning_models = get_models_by_capability(ModelCapability.REASONING)
        assert len(reasoning_models) > 0
        assert all(
            ModelCapability.REASONING in spec.capabilities 
            for spec in reasoning_models.values()
        )
        
        multimodal_models = get_models_by_capability(ModelCapability.MULTIMODAL)
        assert len(multimodal_models) > 0
        assert all(
            ModelCapability.MULTIMODAL in spec.capabilities 
            for spec in multimodal_models.values()
        )

    def test_validate_model_support(self):
        """Test model capability validation."""
        # Test valid model with required capabilities
        result = validate_model_support("gpt-4.1", [ModelCapability.TEXT_GENERATION])
        assert result is True
        
        result = validate_model_support("gpt-4.1", [
            ModelCapability.TEXT_GENERATION, 
            ModelCapability.FUNCTION_CALLING
        ])
        assert result is True
        
        # Test invalid model
        result = validate_model_support("nonexistent-model", [ModelCapability.TEXT_GENERATION])
        assert result is False
        
        # Test model without required capability
        result = validate_model_support("whisper-1", [ModelCapability.TEXT_GENERATION])
        assert result is False


class TestLLMProviders:
    """Test LLM provider implementations."""

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response."""
        response = MagicMock()
        response.choices[0].message.content = "Test response from OpenAI"
        response.choices[0].finish_reason = "stop"
        response.usage.prompt_tokens = 10
        response.usage.completion_tokens = 20
        response.usage.total_tokens = 30
        return response

    @pytest.fixture
    def mock_anthropic_response(self):
        """Mock Anthropic API response."""
        response = MagicMock()
        text_block = MagicMock()
        text_block.text = "Test response from Claude"
        response.content = [text_block]
        response.stop_reason = "end_turn"
        response.usage.input_tokens = 15
        response.usage.output_tokens = 25
        return response

    @patch("openai.AsyncOpenAI")
    async def test_openai_provider_generate(self, mock_openai_client, mock_openai_response):
        """Test OpenAI provider response generation."""
        # Setup mock
        mock_client_instance = AsyncMock()
        mock_openai_client.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.return_value = mock_openai_response
        
        # Create provider and test
        provider = OpenAIProvider("test-api-key")
        
        request = LLMRequest(
            prompt="Test prompt",
            model_id="gpt-4.1-mini",
            max_tokens=100,
            temperature=0.7,
        )
        
        response = await provider.generate(request)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Test response from OpenAI"
        assert response.model_used == "gpt-4.1-mini"
        assert response.provider == "openai"
        assert response.tokens_used == 30
        assert response.cost_usd > 0

    @patch("anthropic.AsyncAnthropic")
    async def test_anthropic_provider_generate(self, mock_anthropic_client, mock_anthropic_response):
        """Test Anthropic provider response generation."""
        # Setup mock
        mock_client_instance = AsyncMock()
        mock_anthropic_client.return_value = mock_client_instance
        mock_client_instance.messages.create.return_value = mock_anthropic_response
        
        # Create provider and test
        provider = AnthropicProvider("test-api-key")
        
        request = LLMRequest(
            prompt="Test prompt",
            model_id="claude-3.5-sonnet",
            max_tokens=100,
            temperature=0.7,
        )
        
        response = await provider.generate(request)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Test response from Claude"
        assert response.model_used == "claude-3.5-sonnet"
        assert response.provider == "anthropic"
        assert response.tokens_used == 40
        assert response.cost_usd > 0

    def test_openai_provider_model_info(self):
        """Test OpenAI provider model information."""
        provider = OpenAIProvider("test-api-key")
        models = provider.get_available_models()
        
        assert len(models) > 0
        assert all(isinstance(model, ModelInfo) for model in models)
        assert all(model.provider == "openai" for model in models)

    def test_cost_calculation(self):
        """Test cost calculation for providers."""
        provider = OpenAIProvider("test-api-key")
        
        # Test known model
        cost = provider.calculate_cost(1000, 500, "gpt-4.1-mini")
        assert cost > 0
        
        # Test unknown model
        cost = provider.calculate_cost(1000, 500, "unknown-model")
        assert cost == 0.0


class TestDynamicModelRouter:
    """Test dynamic model routing functionality."""

    @pytest.fixture
    def router_with_providers(self):
        """Create router with mock providers."""
        router = DynamicModelRouter()
        
        # Mock OpenAI provider
        openai_provider = MagicMock()
        openai_provider.get_available_models.return_value = [
            ModelInfo(
                id="gpt-4.1-mini",
                provider="openai",
                name="GPT-4.1 Mini",
                description="Test model",
                capabilities=[MILModelCapability.TEXT_GENERATION],
                context_window=128000,
                input_cost_per_million_tokens=0.15,
                output_cost_per_million_tokens=0.60,
                quality_score=0.85,
            )
        ]
        
        router.register_provider("openai", openai_provider)
        return router

    def test_provider_registration(self, router_with_providers):
        """Test provider registration."""
        assert "openai" in router_with_providers.providers
        assert len(router_with_providers.models) > 0
        assert "openai/gpt-4.1-mini" in router_with_providers.models

    def test_optimal_model_selection(self, router_with_providers):
        """Test optimal model selection logic."""
        request = LLMRequest(prompt="Test prompt")
        policy = RoutingPolicy(cost_weight=0.5, quality_weight=0.5)
        
        selected_model = router_with_providers.get_optimal_model(request, policy)
        assert selected_model is not None

    def test_capability_filtering(self, router_with_providers):
        """Test filtering by required capabilities."""
        request = LLMRequest(prompt="Test prompt")
        policy = RoutingPolicy(
            required_capabilities=[MILModelCapability.TEXT_GENERATION]
        )
        
        candidates = router_with_providers._filter_by_capabilities(request, policy)
        assert len(candidates) > 0

    def test_constraint_filtering(self, router_with_providers):
        """Test filtering by policy constraints."""
        candidates = ["openai/gpt-4.1-mini"]
        policy = RoutingPolicy(max_cost_per_request=0.01)
        
        filtered = router_with_providers._filter_by_constraints(candidates, policy)
        # Should filter based on constraints
        assert isinstance(filtered, list)


class TestCachingAndRateLimiting:
    """Test caching and rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_response_cache(self):
        """Test LLM response caching."""
        cache = LLMResponseCache()
        
        # Test cache miss
        result = await cache.get("test prompt", "gpt-4.1-mini")
        assert result is None
        
        # Set cache
        response_data = {
            "content": "Cached response",
            "model_used": "gpt-4.1-mini",
            "cost_usd": 0.001,
        }
        
        await cache.set(
            prompt="test prompt",
            model_id="gpt-4.1-mini",
            response_data=response_data,
            ttl_seconds=3600,
        )
        
        # Test cache hit
        result = await cache.get("test prompt", "gpt-4.1-mini")
        assert result is not None
        assert result["content"] == "Cached response"
        
        # Test cache stats
        stats = cache.get_stats()
        assert stats["cache_hits"] > 0
        assert stats["cache_misses"] > 0

    @pytest.mark.asyncio
    async def test_rate_limiter(self):
        """Test rate limiting functionality."""
        rate_limiter = RateLimiter()
        
        # Test initial request (should be allowed)
        allowed, info = await rate_limiter.check_rate_limit(
            provider="test",
            model_id="test-model",
            estimated_cost=0.001,
        )
        
        assert allowed is True
        assert "minute_count" in info
        assert "hour_count" in info
        
        # Test usage recording
        await rate_limiter.record_usage(
            provider="test",
            model_id="test-model",
            actual_cost=0.001,
            tokens_used=100,
        )


class TestBasicAgentIntegration:
    """Test the basic agent with real LLM integration."""

    @pytest.fixture
    def agent(self):
        """Create a basic agent for testing."""
        return BasicAIAgent("TestAgent", "test assistant")

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "TestAgent"
        assert agent.role == "test assistant"
        assert agent.total_requests == 0
        assert agent.total_cost == 0.0

    @pytest.mark.asyncio
    async def test_context_management(self, agent):
        """Test context management in agent."""
        # Test initial context
        context = agent.get_context_summary()
        assert context["agent_name"] == "TestAgent"
        assert context["interaction_count"] == 0
        
        # Process a message (will use fallback since no providers configured)
        await agent.process_message("Hello, test message")
        
        # Check context updated
        updated_context = agent.get_context_summary()
        assert updated_context["interaction_count"] == 1

    def test_usage_statistics(self, agent):
        """Test usage statistics tracking."""
        # Test initial stats
        stats = agent.get_usage_stats()
        assert stats["total_requests"] == 0
        assert stats["total_cost_usd"] == 0.0
        assert stats["average_cost_per_request"] == 0.0

    @pytest.mark.asyncio
    @patch("app.agents.basic_agent.ModelIntegrationLayer")
    async def test_real_llm_integration(self, mock_mil_class, agent):
        """Test agent with mocked real LLM integration."""
        # Setup mock MIL
        mock_mil = AsyncMock()
        mock_mil_class.return_value = mock_mil
        mock_mil.router.providers = {"openai": MagicMock()}
        
        # Mock LLM response
        mock_response = LLMResponse(
            content="Test LLM response",
            model_used="gpt-4.1-mini",
            provider="openai",
            tokens_used=50,
            cost_usd=0.001,
            latency_ms=500.0,
            finish_reason="stop",
        )
        mock_mil.generate_response.return_value = mock_response
        
        # Create new agent with mocked MIL
        agent.mil = mock_mil
        
        # Test message processing
        response = await agent.process_message("Test message")
        
        # Verify LLM was called
        mock_mil.generate_response.assert_called_once()
        
        # Check usage stats updated
        stats = agent.get_usage_stats()
        assert stats["total_requests"] == 1
        assert stats["total_cost_usd"] > 0


class TestModelIntegrationLayer:
    """Test the complete Model Integration Layer."""

    @pytest.mark.asyncio
    async def test_mil_initialization(self):
        """Test MIL initialization."""
        mil = ModelIntegrationLayer()
        
        # Should initialize with available providers based on config
        assert mil.router is not None
        assert mil.default_policy is not None

    @pytest.mark.asyncio
    async def test_mil_with_providers(self):
        """Test MIL with configured providers."""
        # Simple test that MIL can be initialized
        mil = ModelIntegrationLayer()
        
        # Should have router initialized
        assert mil.router is not None
        assert mil.default_policy is not None
        
        # Test provider status (should work even with no providers)
        status = mil.get_provider_status()
        assert isinstance(status, dict)

    def test_provider_status(self):
        """Test provider status reporting."""
        mil = ModelIntegrationLayer()
        status = mil.get_provider_status()
        
        assert isinstance(status, dict)
        # Should return status for each configured provider


if __name__ == "__main__":
    pytest.main([__file__, "-v"])