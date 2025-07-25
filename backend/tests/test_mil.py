"""
Tests for the Model Integration Layer (MIL) Core Module
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.mil import (
    ModelCapability,
    ModelInfo,
    LLMRequest,
    LLMResponse,
    LLMProvider,
    DynamicModelRouter,
    OpenAIProvider,
)


class TestModelInfo:
    """Test cases for ModelInfo dataclass."""
    
    def test_model_info_creation(self):
        """Test ModelInfo creation with all fields."""
        model = ModelInfo(
            id="gpt-4",
            provider="openai",
            name="GPT-4",
            description="Advanced reasoning model",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.FUNCTION_CALLING],
            context_window=128000,
            input_cost_per_million_tokens=10.0,
            output_cost_per_million_tokens=30.0,
            quality_score=0.95
        )
        
        assert model.id == "gpt-4"
        assert model.provider == "openai"
        assert ModelCapability.TEXT_GENERATION in model.capabilities
        assert model.context_window == 128000
        assert model.quality_score == 0.95


class TestLLMRequest:
    """Test cases for LLMRequest dataclass."""
    
    def test_llm_request_creation(self):
        """Test LLMRequest creation."""
        request = LLMRequest(
            prompt="Hello, how are you?",
            model_id="gpt-4",
            max_tokens=100,
            temperature=0.7
        )
        
        assert request.prompt == "Hello, how are you?"
        assert request.model_id == "gpt-4"
        assert request.max_tokens == 100
        assert request.temperature == 0.7


class TestLLMResponse:
    """Test cases for LLMResponse dataclass."""
    
    def test_llm_response_creation(self):
        """Test LLMResponse creation."""
        response = LLMResponse(
            content="Hello there!",
            model_used="gpt-4",
            provider="openai",
            tokens_used=10,
            cost_usd=0.001,
            latency_ms=250.0,
            finish_reason="stop"
        )
        
        assert response.content == "Hello there!"
        assert response.model_used == "gpt-4"
        assert response.provider == "openai"
        assert response.tokens_used == 10
        assert response.cost_usd == 0.001
        assert response.latency_ms == 250.0


class MockProvider(LLMProvider):
    """Mock provider for testing."""
    
    def __init__(self, name: str, api_key: str = "test_key"):
        super().__init__(api_key)
        self.name = name
        self.models = {}
    
    def get_provider_name(self) -> str:
        return self.name
    
    def get_available_models(self) -> list[ModelInfo]:
        return list(self.models.values())
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content=f"Mock response from {self.name}",
            model_used=request.model_id or "default_model",
            provider=self.name,
            tokens_used=10,
            cost_usd=0.001,
            latency_ms=100.0,
            finish_reason="stop"
        )
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        return input_tokens * 0.00001 + output_tokens * 0.00003
    
    def add_model(self, model: ModelInfo):
        self.models[model.id] = model


class TestDynamicModelRouter:
    """Test cases for DynamicModelRouter."""
    
    def test_router_initialization(self):
        """Test router initialization."""
        router = DynamicModelRouter()
        
        assert hasattr(router, 'providers')
        assert hasattr(router, 'models')
        assert hasattr(router, 'performance_history')
        assert len(router.providers) == 0
        assert len(router.models) == 0
    
    def test_register_provider(self):
        """Test provider registration."""
        router = DynamicModelRouter()
        mock_provider = MockProvider("test_provider")
        
        # Add a model to the provider
        mock_provider.add_model(ModelInfo(
            id="test_model",
            provider="test_provider",
            name="Test Model",
            description="Test",
            capabilities=[ModelCapability.TEXT_GENERATION],
            context_window=8000,
            input_cost_per_million_tokens=1.0,
            output_cost_per_million_tokens=2.0
        ))
        
        router.register_provider("test_provider", mock_provider)
        
        assert "test_provider" in router.providers
        assert router.providers["test_provider"] == mock_provider
        assert "test_provider/test_model" in router.models
    
    def test_get_available_models_through_registry(self):
        """Test getting available models from the router's registry."""
        router = DynamicModelRouter()
        
        provider = MockProvider("test_provider")
        provider.add_model(ModelInfo(
            id="model1",
            provider="test_provider",
            name="Model 1",
            description="Test model 1",
            capabilities=[ModelCapability.TEXT_GENERATION],
            context_window=8000,
            input_cost_per_million_tokens=1.0,
            output_cost_per_million_tokens=2.0
        ))
        
        router.register_provider("test_provider", provider)
        
        # Check that model was registered
        assert len(router.models) == 1
        assert "test_provider/model1" in router.models


class TestOpenAIProvider:
    """Tests for OpenAI provider (mocked)."""
    
    def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization."""
        with patch('openai.AsyncOpenAI') as mock_client:
            provider = OpenAIProvider(api_key="test_key")
            assert hasattr(provider, 'client')
            mock_client.assert_called_once()
    
    def test_openai_available_models(self):
        """Test OpenAI available models."""
        with patch('openai.AsyncOpenAI'):
            provider = OpenAIProvider(api_key="test_key")
            models = provider.get_available_models()
            
            assert len(models) > 0
            
            # Check for common OpenAI models
            model_ids = [m.id for m in models]
            assert any("gpt" in model_id for model_id in model_ids)
    
    @pytest.mark.asyncio
    async def test_openai_generate_response(self):
        """Test OpenAI response generation (mocked)."""
        with patch('openai.AsyncOpenAI') as mock_client:
            # Mock the OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.total_tokens = 25
            mock_response.model = "gpt-4"
            
            mock_client.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
            
            provider = OpenAIProvider(api_key="test_key")
            
            request = LLMRequest(
                prompt="Hello, how are you?",
                model_id="gpt-4"
            )
            
            response = await provider.generate(request)
            
            assert response.content == "Test response"
            assert response.model_used == "gpt-4"
            assert response.tokens_used == 25
            assert response.cost_usd > 0  # Should calculate some cost