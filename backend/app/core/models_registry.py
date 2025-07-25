"""
Model Registry for Z2 AI Workforce Platform

This module contains the complete registry of all supported AI models and providers.
It serves as the single source of truth for model specifications and capabilities.

IMPORTANT: This registry defines production model specifications.
Changes to this file should be carefully reviewed to prevent model downgrades or reversions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum


class ModelCapability(Enum):
    """Enumeration of model capabilities."""
    TEXT_GENERATION = "text_generation"
    VISION = "vision"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    EMBEDDINGS = "embeddings"
    FUNCTION_CALLING = "function_calling"
    STRUCTURED_OUTPUT = "structured_output"
    REASONING = "reasoning"
    CODE_GENERATION = "code_generation"
    REAL_TIME_SEARCH = "real_time_search"
    WEB_BROWSING = "web_browsing"
    MULTIMODAL = "multimodal"


class ProviderType(Enum):
    """Enumeration of AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    XAI = "xai"


@dataclass
class ModelSpec:
    """Complete specification for an AI model."""
    provider: ProviderType
    model_id: str
    name: str
    description: str
    capabilities: Set[ModelCapability]
    input_token_limit: int
    output_token_limit: int
    supports_streaming: bool = True
    supports_system_message: bool = True
    cost_per_input_token: Optional[float] = None  # USD per 1M tokens
    cost_per_output_token: Optional[float] = None  # USD per 1M tokens
    context_window: Optional[int] = None
    model_card_url: Optional[str] = None
    is_reasoning_model: bool = False
    is_multimodal: bool = False
    knowledge_cutoff: Optional[str] = None


# OpenAI Models - Official Complete Technical Specifications
OPENAI_MODELS = {
    # Reasoning models
    "o4-mini": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o4-mini",
        name="o4-mini",
        description="Faster, more affordable reasoning model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        is_reasoning_model=True,
        knowledge_cutoff="April 16, 2025",
        model_card_url="https://platform.openai.com/docs/models/o4-mini",
    ),
    "o3": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o3",
        name="o3",
        description="Our most powerful reasoning model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        is_reasoning_model=True,
        knowledge_cutoff="April 16, 2025",
        model_card_url="https://platform.openai.com/docs/models/o3",
    ),
    "o3-pro": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o3-pro",
        name="o3-pro",
        description="Version of o3 with more compute for better responses",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        is_reasoning_model=True,
        knowledge_cutoff="June 10, 2025",
        model_card_url="https://platform.openai.com/docs/models/o3-pro",
    ),
    "o3-mini": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o3-mini",
        name="o3-mini",
        description="A small model alternative to o3",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        is_reasoning_model=True,
        knowledge_cutoff="January 31, 2025",
        model_card_url="https://platform.openai.com/docs/models/o3-mini",
    ),
    
    # Flagship chat models
    "gpt-4.1": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4.1",
        name="GPT-4.1",
        description="Flagship GPT model for complex tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=1000000,
        output_token_limit=32768,
        is_multimodal=True,
        knowledge_cutoff="April 14, 2025",
        model_card_url="https://platform.openai.com/docs/models/gpt-4.1",
    ),
    "gpt-4o": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o",
        name="GPT-4o",
        description="Fast, intelligent, flexible GPT model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        is_multimodal=True,
        knowledge_cutoff="October 2024",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o",
    ),
    "chatgpt-4o-latest": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="chatgpt-4o-latest",
        name="ChatGPT-4o",
        description="GPT-4o model used in ChatGPT",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        is_multimodal=True,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/chatgpt-4o-latest",
    ),
    
    # Cost-optimized models
    "gpt-4.1-mini": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4.1-mini",
        name="GPT-4.1 mini",
        description="Balanced for intelligence, speed, and cost",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=1000000,
        output_token_limit=32768,
        is_multimodal=True,
        knowledge_cutoff="April 14, 2025",
        model_card_url="https://platform.openai.com/docs/models/gpt-4.1-mini",
    ),
    "gpt-4.1-nano": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4.1-nano",
        name="GPT-4.1 nano",
        description="Fastest, most cost-effective GPT-4.1 model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=1000000,
        output_token_limit=32768,
        is_multimodal=True,
        knowledge_cutoff="April 14, 2025",
        model_card_url="https://platform.openai.com/docs/models/gpt-4.1-nano",
    ),
    
    # Deep research models
    "o3-deep-research": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o3-deep-research",
        name="o3-deep-research",
        description="Our most powerful deep research model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        is_reasoning_model=True,
        knowledge_cutoff="2025",
        model_card_url="https://platform.openai.com/docs/models/o3-deep-research",
    ),
    "o4-mini-deep-research": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o4-mini-deep-research",
        name="o4-mini-deep-research",
        description="Faster, more affordable deep research model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        is_reasoning_model=True,
        knowledge_cutoff="2025",
        model_card_url="https://platform.openai.com/docs/models/o4-mini-deep-research",
    ),
    "o4-mini-deep-research-2025-06-26": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o4-mini-deep-research-2025-06-26",
        name="o4-mini-deep-research-2025-06-26",
        description="Faster, more affordable deep research model (June 26, 2025 version)",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        is_reasoning_model=True,
        knowledge_cutoff="June 26, 2025",
        model_card_url="https://platform.openai.com/docs/models/o4-mini-deep-research",
    ),
    
    # Realtime models
    "gpt-4o-realtime-preview": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o-realtime-preview",
        name="GPT-4o Realtime",
        description="Model capable of realtime text and audio inputs and outputs",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.AUDIO,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        is_multimodal=True,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o-realtime-preview",
    ),
    "gpt-4o-mini-realtime-preview": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o-mini-realtime-preview",
        name="GPT-4o mini Realtime",
        description="Smaller realtime model for text and audio inputs and outputs",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.AUDIO,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        is_multimodal=True,
        knowledge_cutoff="December 17, 2024",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o-mini-realtime-preview",
    ),
    
    # Image generation models
    "gpt-image-1": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-image-1",
        name="GPT Image 1",
        description="State-of-the-art image generation model",
        capabilities={ModelCapability.IMAGE_GENERATION},
        input_token_limit=4000,
        output_token_limit=0,
        supports_streaming=False,
        knowledge_cutoff="2025",
        model_card_url="https://platform.openai.com/docs/models/gpt-image-1",
    ),
    
    # Text-to-speech
    "gpt-4o-mini-tts": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o-mini-tts",
        name="GPT-4o mini TTS",
        description="Text-to-speech model powered by GPT-4o mini",
        capabilities={ModelCapability.TEXT_TO_SPEECH},
        input_token_limit=4096,
        output_token_limit=0,
        supports_streaming=True,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o-mini-tts",
    ),
    "tts-1": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="tts-1",
        name="TTS-1",
        description="Text-to-speech model optimized for speed",
        capabilities={ModelCapability.TEXT_TO_SPEECH},
        input_token_limit=4096,
        output_token_limit=0,
        supports_streaming=True,
        knowledge_cutoff="2023",
        model_card_url="https://platform.openai.com/docs/models/tts-1",
    ),
    "tts-1-hd": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="tts-1-hd",
        name="TTS-1 HD",
        description="Text-to-speech model optimized for quality",
        capabilities={ModelCapability.TEXT_TO_SPEECH},
        input_token_limit=4096,
        output_token_limit=0,
        supports_streaming=True,
        knowledge_cutoff="2023",
        model_card_url="https://platform.openai.com/docs/models/tts-1-hd",
    ),
    
    # Transcription
    "gpt-4o-transcribe": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o-transcribe",
        name="GPT-4o Transcribe",
        description="Speech-to-text model powered by GPT-4o",
        capabilities={ModelCapability.SPEECH_TO_TEXT},
        input_token_limit=128000,
        output_token_limit=16384,
        supports_streaming=False,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o-transcribe",
    ),
    "gpt-4o-mini-transcribe": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o-mini-transcribe",
        name="GPT-4o mini Transcribe",
        description="Speech-to-text model powered by GPT-4o mini",
        capabilities={ModelCapability.SPEECH_TO_TEXT},
        input_token_limit=128000,
        output_token_limit=16384,
        supports_streaming=False,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o-mini-transcribe",
    ),
    "whisper-1": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="whisper-1",
        name="Whisper",
        description="General-purpose speech recognition model",
        capabilities={ModelCapability.SPEECH_TO_TEXT},
        input_token_limit=0,
        output_token_limit=0,
        supports_streaming=False,
        knowledge_cutoff="2022",
        model_card_url="https://platform.openai.com/docs/models/whisper-1",
    ),
    
    # Tool-specific models
    "gpt-4o-search-preview": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o-search-preview",
        name="GPT-4o Search Preview",
        description="GPT model for web search in Chat Completions",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.WEB_BROWSING,
            ModelCapability.REAL_TIME_SEARCH,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o-search-preview",
    ),
    "gpt-4o-mini-search-preview": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o-mini-search-preview",
        name="GPT-4o mini Search Preview",
        description="Fast, affordable small model for web search",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.WEB_BROWSING,
            ModelCapability.REAL_TIME_SEARCH,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o-mini-search-preview",
    ),
    "computer-use-preview": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="computer-use-preview",
        name="computer-use-preview",
        description="Specialized model for computer use tool",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.FUNCTION_CALLING,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/computer-use-preview",
    ),
    "codex-mini-latest": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="codex-mini-latest",
        name="codex-mini-latest",
        description="Fast reasoning model optimized for the Codex CLI",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        is_reasoning_model=True,
        knowledge_cutoff="2025",
        model_card_url="https://platform.openai.com/docs/models/codex-mini-latest",
    ),
    
    # Embeddings
    "text-embedding-3-small": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="text-embedding-3-small",
        name="text-embedding-3-small",
        description="Small embedding model",
        capabilities={ModelCapability.EMBEDDINGS},
        input_token_limit=8191,
        output_token_limit=1536,
        supports_streaming=False,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/text-embedding-3-small",
    ),
    "text-embedding-3-large": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="text-embedding-3-large",
        name="text-embedding-3-large",
        description="Most capable embedding model",
        capabilities={ModelCapability.EMBEDDINGS},
        input_token_limit=8191,
        output_token_limit=3072,
        supports_streaming=False,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/text-embedding-3-large",
    ),
    "text-embedding-ada-002": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="text-embedding-ada-002",
        name="text-embedding-ada-002",
        description="Older embedding model",
        capabilities={ModelCapability.EMBEDDINGS},
        input_token_limit=8191,
        output_token_limit=1536,
        supports_streaming=False,
        knowledge_cutoff="2022",
        model_card_url="https://platform.openai.com/docs/models/text-embedding-ada-002",
    ),
    
    # Moderation
    "omni-moderation-latest": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="omni-moderation-latest",
        name="omni-moderation",
        description="Identify potentially harmful content in text and images",
        capabilities={ModelCapability.TEXT_GENERATION},
        input_token_limit=32768,
        output_token_limit=1024,
        supports_streaming=False,
        knowledge_cutoff="2024",
        model_card_url="https://platform.openai.com/docs/models/omni-moderation-latest",
    ),
    "text-moderation-latest": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="text-moderation-latest",
        name="text-moderation",
        description="Previous generation text-only moderation model",
        capabilities={ModelCapability.TEXT_GENERATION},
        input_token_limit=32768,
        output_token_limit=1024,
        supports_streaming=False,
        knowledge_cutoff="2023",
        model_card_url="https://platform.openai.com/docs/models/text-moderation-latest",
    ),
    
    # Older GPT models
    "gpt-4-turbo": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4-turbo",
        name="GPT-4 Turbo",
        description="An older high-intelligence GPT model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=128000,
        output_token_limit=4096,
        knowledge_cutoff="2023",
        model_card_url="https://platform.openai.com/docs/models/gpt-4-turbo",
    ),
}

# Anthropic Claude Models - Official Complete Technical Specifications
ANTHROPIC_MODELS = {
    "claude-opus-4-20250514": ModelSpec(
        provider=ProviderType.ANTHROPIC,
        model_id="claude-opus-4-20250514",
        name="Claude Opus 4",
        description="Our most capable model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=32000,
        cost_per_input_token=15.00,
        cost_per_output_token=75.00,
        knowledge_cutoff="March 2025",
    ),
    "claude-sonnet-4-20250514": ModelSpec(
        provider=ProviderType.ANTHROPIC,
        model_id="claude-sonnet-4-20250514",
        name="Claude Sonnet 4",
        description="High-performance model with exceptional reasoning",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=64000,
        cost_per_input_token=3.00,
        cost_per_output_token=15.00,
        knowledge_cutoff="March 2025",
    ),
    "claude-3-7-sonnet-20250219": ModelSpec(
        provider=ProviderType.ANTHROPIC,
        model_id="claude-3-7-sonnet-20250219",
        name="Claude Sonnet 3.7",
        description="High-performance model with toggleable extended thinking",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=64000,
        cost_per_input_token=3.00,
        cost_per_output_token=15.00,
        knowledge_cutoff="November 2024",
    ),
    "claude-3-5-sonnet-20241022": ModelSpec(
        provider=ProviderType.ANTHROPIC,
        model_id="claude-3-5-sonnet-20241022",
        name="Claude Sonnet 3.5",
        description="Our previous intelligent model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=8192,
        cost_per_input_token=3.00,
        cost_per_output_token=15.00,
        knowledge_cutoff="April 2024",
    ),
    "claude-3-5-haiku-20241022": ModelSpec(
        provider=ProviderType.ANTHROPIC,
        model_id="claude-3-5-haiku-20241022",
        name="Claude Haiku 3.5",
        description="Our fastest model for intelligence at blazing speeds",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
        },
        input_token_limit=200000,
        output_token_limit=8192,
        cost_per_input_token=0.80,
        cost_per_output_token=4.00,
        knowledge_cutoff="July 2024",
    ),
}

# xAI Models
XAI_MODELS = {
    "grok-4-8789": ModelSpec(
        provider=ProviderType.XAI,
        model_id="grok-4-8789",
        name="Grok 4 8789",
        description="Language model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REAL_TIME_SEARCH,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=200000,
        output_token_limit=32000,
        cost_per_input_token=3.00,
        cost_per_output_token=15.00,
        knowledge_cutoff="2024",
    ),
}

# Combined model registry
ALL_MODELS: Dict[str, ModelSpec] = {
    **OPENAI_MODELS,
    **ANTHROPIC_MODELS,
    **XAI_MODELS,
}


def get_model_by_id(model_id: str) -> Optional[ModelSpec]:
    """Get a model specification by its ID."""
    return ALL_MODELS.get(model_id)


def get_models_by_provider(provider: ProviderType) -> Dict[str, ModelSpec]:
    """Get all models for a specific provider."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if spec.provider == provider
    }


def get_models_by_capability(capability: ModelCapability) -> Dict[str, ModelSpec]:
    """Get all models that support a specific capability."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if capability in spec.capabilities
    }


def get_reasoning_models() -> Dict[str, ModelSpec]:
    """Get all models optimized for reasoning tasks."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if spec.is_reasoning_model
    }


def get_multimodal_models() -> Dict[str, ModelSpec]:
    """Get all multimodal models."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if spec.is_multimodal
    }


def get_cost_efficient_models(max_input_cost: float = 1.0) -> Dict[str, ModelSpec]:
    """Get models under a certain cost threshold per million input tokens."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if spec.cost_per_input_token is not None
        and spec.cost_per_input_token <= max_input_cost
    }


def validate_model_support(model_id: str, required_capabilities: List[ModelCapability]) -> bool:
    """Validate that a model supports all required capabilities."""
    spec = get_model_by_id(model_id)
    if not spec:
        return False
    
    return all(capability in spec.capabilities for capability in required_capabilities)


# Model routing configuration for automatic model selection
DEFAULT_MODEL_ROUTING = {
    "text_generation": "gpt-4.1-mini",
    "reasoning": "o4-mini",
    "advanced_reasoning": "claude-sonnet-4-20250514",
    "flagship": "gpt-4.1",
    "multimodal": "gpt-4o",
    "vision": "gpt-4o",
    "code_generation": "o4-mini",
    "embeddings": "text-embedding-3-small",
    "image_generation": "gpt-image-1",
    "speech_to_text": "whisper-1",
    "text_to_speech": "tts-1",
    "real_time_search": "grok-4-8789",
    "fast_model": "gpt-4.1-nano",
    "cost_efficient": "gpt-4.1-nano",
}


# Version lock to prevent model downgrades
MODEL_REGISTRY_VERSION = "2025.01.25"
MINIMUM_SUPPORTED_MODELS = {
    "openai": ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "o4-mini", "o3", "o4-mini-deep-research-2025-06-26"],
    "anthropic": ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219"],
    "xai": ["grok-4-8789"],
}


def validate_model_registry_integrity() -> bool:
    """
    Validate that the model registry maintains minimum required models.
    This prevents accidental downgrades or removal of production models.
    """
    for provider, required_models in MINIMUM_SUPPORTED_MODELS.items():
        provider_enum = ProviderType(provider)
        provider_models = get_models_by_provider(provider_enum)
        
        for required_model in required_models:
            if required_model not in provider_models:
                raise ValueError(
                    f"CRITICAL: Required model '{required_model}' missing from "
                    f"provider '{provider}'. This would cause a production downgrade."
                )
    
    return True


# Validate registry integrity on import
validate_model_registry_integrity()