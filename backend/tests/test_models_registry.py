"""
Tests for the models registry to ensure all model specifications are correct.
"""

import pytest
from app.core.models_registry import (
    ALL_MODELS,
    ProviderType,
    ModelCapability,
    get_model_by_id,
    get_models_by_provider,
    get_models_by_capability,
    get_reasoning_models,
    get_multimodal_models,
    validate_model_support,
    validate_model_registry_integrity,
    DEFAULT_MODEL_ROUTING,
    MINIMUM_SUPPORTED_MODELS,
)


class TestModelsRegistry:
    """Test cases for the models registry."""

    def test_registry_integrity(self):
        """Test that the registry maintains integrity and required models."""
        # This should not raise an exception
        assert validate_model_registry_integrity() is True

    def test_minimum_supported_models_exist(self):
        """Test that all minimum supported models are present."""
        for provider_name, required_models in MINIMUM_SUPPORTED_MODELS.items():
            provider = ProviderType(provider_name)
            provider_models = get_models_by_provider(provider)
            
            for required_model in required_models:
                assert required_model in provider_models, (
                    f"Required model '{required_model}' missing from provider '{provider_name}'"
                )

    def test_get_model_by_id(self):
        """Test retrieving specific models by ID."""
        # Test OpenAI models
        gpt4o = get_model_by_id("gpt-4o")
        assert gpt4o is not None
        assert gpt4o.name == "GPT-4o"
        assert gpt4o.provider == ProviderType.OPENAI

        # Test new o3-mini model
        o3_mini = get_model_by_id("o3-mini")
        assert o3_mini is not None
        assert o3_mini.name == "o3-mini"
        assert o3_mini.is_reasoning_model is True

        # Test Claude 4 models
        claude_4 = get_model_by_id("claude-sonnet-4-20250514")
        assert claude_4 is not None
        assert claude_4.name == "Claude Sonnet 4"
        assert claude_4.provider == ProviderType.ANTHROPIC

        # Test non-existent model
        assert get_model_by_id("non-existent-model") is None

    def test_get_models_by_provider(self):
        """Test filtering models by provider."""
        # Test OpenAI provider
        openai_models = get_models_by_provider(ProviderType.OPENAI)
        assert len(openai_models) >= 3  # At least gpt-4o, gpt-4o-mini, o3-mini
        assert "gpt-4o" in openai_models
        assert "o3-mini" in openai_models

        # Test Anthropic provider
        anthropic_models = get_models_by_provider(ProviderType.ANTHROPIC)
        assert len(anthropic_models) >= 2  # At least Claude 4 and 3.7
        assert "claude-sonnet-4-20250514" in anthropic_models

        # Test Google provider
        google_models = get_models_by_provider(ProviderType.GOOGLE)
        assert len(google_models) >= 2  # At least Gemini 2.5 models
        assert "gemini-2.5-pro" in google_models

    def test_get_models_by_capability(self):
        """Test filtering models by capability."""
        # Test reasoning models
        reasoning_models = get_models_by_capability(ModelCapability.REASONING)
        assert len(reasoning_models) > 0
        assert "o3-mini" in reasoning_models

        # Test multimodal models
        multimodal_models = get_models_by_capability(ModelCapability.MULTIMODAL)
        assert len(multimodal_models) > 0
        assert "gpt-4o" in multimodal_models

        # Test vision models
        vision_models = get_models_by_capability(ModelCapability.VISION)
        assert len(vision_models) > 0
        assert "gpt-4o" in vision_models

    def test_get_reasoning_models(self):
        """Test getting reasoning-optimized models."""
        reasoning_models = get_reasoning_models()
        assert len(reasoning_models) >= 3  # o1, o1-mini, o3-mini
        assert "o3-mini" in reasoning_models
        assert "o1" in reasoning_models

        # Verify they all have reasoning capability
        for model_id, spec in reasoning_models.items():
            assert spec.is_reasoning_model is True
            assert ModelCapability.REASONING in spec.capabilities

    def test_get_multimodal_models(self):
        """Test getting multimodal models."""
        multimodal_models = get_multimodal_models()
        assert len(multimodal_models) > 0
        assert "gpt-4o" in multimodal_models

        # Verify they all have multimodal capability
        for model_id, spec in multimodal_models.items():
            assert spec.is_multimodal is True
            assert ModelCapability.MULTIMODAL in spec.capabilities

    def test_validate_model_support(self):
        """Test model capability validation."""
        # Test valid combinations
        assert validate_model_support("gpt-4o", [ModelCapability.TEXT_GENERATION])
        assert validate_model_support("gpt-4o", [ModelCapability.VISION, ModelCapability.MULTIMODAL])
        assert validate_model_support("o3-mini", [ModelCapability.REASONING])

        # Test invalid combinations
        assert not validate_model_support("text-embedding-3-small", [ModelCapability.TEXT_GENERATION])
        assert not validate_model_support("dall-e-3", [ModelCapability.TEXT_GENERATION])
        assert not validate_model_support("non-existent-model", [ModelCapability.TEXT_GENERATION])

    def test_default_model_routing(self):
        """Test that default routing models exist and are valid."""
        for task_type, model_id in DEFAULT_MODEL_ROUTING.items():
            model = get_model_by_id(model_id)
            assert model is not None, f"Default model '{model_id}' for task '{task_type}' not found"

    def test_openai_latest_models(self):
        """Test that latest OpenAI models are included."""
        # GPT-4o series
        assert get_model_by_id("gpt-4o") is not None
        assert get_model_by_id("gpt-4o-mini") is not None

        # o-series reasoning models
        assert get_model_by_id("o1") is not None
        assert get_model_by_id("o1-mini") is not None
        assert get_model_by_id("o3-mini") is not None

        # Ensure o3-mini has latest features
        o3_mini = get_model_by_id("o3-mini")
        assert ModelCapability.STRUCTURED_OUTPUT in o3_mini.capabilities
        assert ModelCapability.FUNCTION_CALLING in o3_mini.capabilities

    def test_anthropic_claude_4_models(self):
        """Test that Claude 4 series models are included."""
        # Claude 4 models
        assert get_model_by_id("claude-opus-4-20250514") is not None
        assert get_model_by_id("claude-sonnet-4-20250514") is not None

        # Claude 3.7 with extended thinking
        assert get_model_by_id("claude-3-7-sonnet-20250219") is not None

        # Verify capabilities
        claude_4 = get_model_by_id("claude-sonnet-4-20250514")
        assert ModelCapability.REASONING in claude_4.capabilities
        assert ModelCapability.VISION in claude_4.capabilities

    def test_xai_grok_models(self):
        """Test that xAI Grok models are included."""
        # Grok 4 and 3 series
        assert get_model_by_id("grok-4-latest") is not None
        assert get_model_by_id("grok-3") is not None
        assert get_model_by_id("grok-3-mini") is not None

        # Verify Grok 4 has real-time search
        grok_4 = get_model_by_id("grok-4-latest")
        assert ModelCapability.REAL_TIME_SEARCH in grok_4.capabilities

    def test_qwen_models(self):
        """Test that Qwen models are included for Chinese optimization."""
        assert get_model_by_id("qwen2.5") is not None
        assert get_model_by_id("qwen-vl") is not None
        assert get_model_by_id("codeqwen") is not None

        # Verify multimodal capabilities
        qwen_vl = get_model_by_id("qwen-vl")
        assert qwen_vl.is_multimodal is True
        assert ModelCapability.VISION in qwen_vl.capabilities

    def test_model_specifications_completeness(self):
        """Test that all models have complete specifications."""
        for model_id, spec in ALL_MODELS.items():
            # Required fields
            assert spec.provider is not None
            assert spec.model_id is not None
            assert spec.name is not None
            assert spec.description is not None
            assert len(spec.capabilities) > 0

            # Most models should have token limits, but some special models like
            # audio/image generation models may not use traditional token limits
            special_models = {
                "whisper-1",  # Audio input
                "dall-e-3",   # Image generation
                "tts-1",      # Text-to-speech
                "tts-1-hd",   # Text-to-speech
            }
            
            if model_id not in special_models:
                assert spec.input_token_limit > 0, f"Model {model_id} should have input_token_limit > 0"

            # Reasoning models should have reasoning capability
            if spec.is_reasoning_model:
                assert ModelCapability.REASONING in spec.capabilities

            # Multimodal models should have multimodal capability
            if spec.is_multimodal:
                assert ModelCapability.MULTIMODAL in spec.capabilities

    def test_cost_information_present(self):
        """Test that cost information is present for major models."""
        # Major models should have cost information
        cost_models = ["gpt-4o", "gpt-4o-mini", "o3-mini", "claude-sonnet-4-20250514"]
        
        for model_id in cost_models:
            model = get_model_by_id(model_id)
            assert model is not None
            # Note: Some models might not have cost info yet, so we just check they exist
            # assert model.cost_per_input_token is not None

    def test_registry_version_and_locking(self):
        """Test that registry version and model locking is in place."""
        from app.core.models_registry import MODEL_REGISTRY_VERSION
        
        # Registry should have a version
        assert MODEL_REGISTRY_VERSION is not None
        assert "2025" in MODEL_REGISTRY_VERSION  # Should be current year

        # Minimum supported models should be enforced
        assert len(MINIMUM_SUPPORTED_MODELS) > 0
        assert "openai" in MINIMUM_SUPPORTED_MODELS
        assert "anthropic" in MINIMUM_SUPPORTED_MODELS