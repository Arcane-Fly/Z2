"""
Tests for the models registry to ensure all model specifications are correct.
"""

from app.core.models_registry import (
    DEFAULT_MODEL_ROUTING,
    MINIMUM_SUPPORTED_MODELS,
    ModelCapability,
    ProviderType,
    get_model_by_id,
    get_models_by_capability,
    get_models_by_provider,
    get_multimodal_models,
    get_reasoning_models,
    validate_model_registry_integrity,
    validate_model_support,
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

        # Test new reasoning models
        o4_mini = get_model_by_id("o4-mini")
        assert o4_mini is not None
        assert o4_mini.name == "o4-mini"
        assert o4_mini.is_reasoning_model is True

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
        assert len(openai_models) >= 3  # At least gpt-4.1, gpt-4o, o4-mini
        assert "gpt-4o" in openai_models
        assert "gpt-4.1" in openai_models
        assert "o4-mini" in openai_models

        # Test Anthropic provider
        anthropic_models = get_models_by_provider(ProviderType.ANTHROPIC)
        assert len(anthropic_models) >= 2  # At least Claude 4 and 3.7
        assert "claude-sonnet-4-20250514" in anthropic_models

        # Test xAI provider
        xai_models = get_models_by_provider(ProviderType.XAI)
        assert len(xai_models) >= 1  # At least Grok 4
        assert "grok-4-8789" in xai_models

    def test_get_models_by_capability(self):
        """Test filtering models by capability."""
        # Test reasoning models
        reasoning_models = get_models_by_capability(ModelCapability.REASONING)
        assert len(reasoning_models) > 0
        assert "o4-mini" in reasoning_models or "o3-mini" in reasoning_models

        # Test multimodal models
        multimodal_models = get_models_by_capability(ModelCapability.MULTIMODAL)
        assert len(multimodal_models) > 0
        assert "gpt-4o" in multimodal_models
        assert "gpt-4.1" in multimodal_models

        # Test vision models
        vision_models = get_models_by_capability(ModelCapability.VISION)
        assert len(vision_models) > 0
        assert "gpt-4o" in vision_models
        assert "gpt-4.1" in vision_models

    def test_get_reasoning_models(self):
        """Test getting reasoning-optimized models."""
        reasoning_models = get_reasoning_models()
        assert len(reasoning_models) >= 2  # o4-mini, o3, o3-mini, etc.

        # Check for available reasoning models
        reasoning_model_ids = list(reasoning_models.keys())
        assert any(model_id in ["o4-mini", "o3", "o3-mini"] for model_id in reasoning_model_ids)

        # Verify they all have reasoning capability
        for _model_id, spec in reasoning_models.items():
            assert spec.is_reasoning_model is True
            assert ModelCapability.REASONING in spec.capabilities

    def test_get_multimodal_models(self):
        """Test getting multimodal models."""
        multimodal_models = get_multimodal_models()
        assert len(multimodal_models) > 0
        assert "gpt-4o" in multimodal_models
        assert "gpt-4.1" in multimodal_models

        # Verify they all have multimodal capability
        for _model_id, spec in multimodal_models.items():
            assert spec.is_multimodal is True
            assert ModelCapability.MULTIMODAL in spec.capabilities

    def test_validate_model_support(self):
        """Test model capability validation."""
        # Test valid combinations
        assert validate_model_support("gpt-4o", [ModelCapability.TEXT_GENERATION])
        assert validate_model_support("gpt-4o", [ModelCapability.VISION, ModelCapability.MULTIMODAL])

        # Test reasoning models - use available ones
        reasoning_models = get_reasoning_models()
        if reasoning_models:
            first_reasoning_model = list(reasoning_models.keys())[0]
            assert validate_model_support(first_reasoning_model, [ModelCapability.REASONING])

        # Test invalid combinations
        assert not validate_model_support("text-embedding-3-small", [ModelCapability.TEXT_GENERATION])
        assert not validate_model_support("gpt-image-1", [ModelCapability.TEXT_GENERATION])
        assert not validate_model_support("non-existent-model", [ModelCapability.TEXT_GENERATION])

    def test_default_model_routing(self):
        """Test that default routing models exist and are valid."""
        for task_type, model_id in DEFAULT_MODEL_ROUTING.items():
            model = get_model_by_id(model_id)
            assert model is not None, f"Default model '{model_id}' for task '{task_type}' not found"

    def test_openai_latest_models(self):
        """Test that latest OpenAI models are included."""
        # GPT-4.1 series
        assert get_model_by_id("gpt-4.1") is not None
        assert get_model_by_id("gpt-4.1-mini") is not None
        assert get_model_by_id("gpt-4.1-nano") is not None

        # GPT-4o series
        assert get_model_by_id("gpt-4o") is not None
        assert get_model_by_id("chatgpt-4o-latest") is not None

        # o-series reasoning models
        assert get_model_by_id("o4-mini") is not None
        assert get_model_by_id("o3") is not None
        assert get_model_by_id("o3-pro") is not None
        assert get_model_by_id("o3-mini") is not None

        # Ensure latest models have expected features
        gpt41 = get_model_by_id("gpt-4.1")
        assert gpt41.input_token_limit == 1000000  # 1M context window

        o4_mini = get_model_by_id("o4-mini")
        assert o4_mini.input_token_limit == 200000  # 200k context window

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
        # Grok 4 series
        assert get_model_by_id("grok-4-8789") is not None

        # Verify Grok 4 has expected capabilities
        grok_4 = get_model_by_id("grok-4-8789")
        assert ModelCapability.TEXT_GENERATION in grok_4.capabilities
        assert grok_4.provider == ProviderType.XAI

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
