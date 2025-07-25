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
    GOOGLE = "google"
    XAI = "xai"
    GROQ = "groq"
    PERPLEXITY = "perplexity"
    MOONSHOT = "moonshot"
    QWEN = "qwen"


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


# OpenAI Models - Latest GPT-4o and o-series models
OPENAI_MODELS = {
    "gpt-4o": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o",
        name="GPT-4o",
        description="OpenAI's flagship multimodal model for text, audio, image, and video",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.AUDIO,
            ModelCapability.VIDEO,
            ModelCapability.IMAGE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        cost_per_input_token=2.50,
        cost_per_output_token=10.00,
        is_multimodal=True,
        knowledge_cutoff="October 2023",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o",
    ),
    "gpt-4o-mini": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="gpt-4o-mini",
        name="GPT-4o mini",
        description="Cost-efficient multimodal model with strong performance on text and image tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=128000,
        output_token_limit=16384,
        cost_per_input_token=0.15,
        cost_per_output_token=0.60,
        is_multimodal=True,
        knowledge_cutoff="October 2023",
        model_card_url="https://platform.openai.com/docs/models/gpt-4o-mini",
    ),
    "o1": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o1",
        name="o1",
        description="Advanced reasoning model with chain-of-thought capabilities",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=128000,
        output_token_limit=32768,
        cost_per_input_token=15.00,
        cost_per_output_token=60.00,
        is_reasoning_model=True,
        knowledge_cutoff="October 2023",
        model_card_url="https://platform.openai.com/docs/models/o1",
    ),
    "o1-mini": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o1-mini",
        name="o1-mini",
        description="Cost-efficient reasoning model for STEM tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.STRUCTURED_OUTPUT,
        },
        input_token_limit=128000,
        output_token_limit=65536,
        cost_per_input_token=3.00,
        cost_per_output_token=12.00,
        is_reasoning_model=True,
        knowledge_cutoff="October 2023",
        model_card_url="https://platform.openai.com/docs/models/o1-mini",
    ),
    "o3-mini": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="o3-mini",
        name="o3-mini",
        description="Latest reasoning model optimized for STEM with improved accuracy",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.FUNCTION_CALLING,
        },
        input_token_limit=200000,
        output_token_limit=100000,
        cost_per_input_token=3.00,
        cost_per_output_token=12.00,
        is_reasoning_model=True,
        knowledge_cutoff="Recent release",
        model_card_url="https://platform.openai.com/docs/models/o3-mini",
    ),
    "text-embedding-3-small": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="text-embedding-3-small",
        name="Text Embedding 3 Small",
        description="Cost-efficient embedding model for semantic search and RAG",
        capabilities={ModelCapability.EMBEDDINGS},
        input_token_limit=8191,
        output_token_limit=1536,  # dimensions
        cost_per_input_token=0.02,
        cost_per_output_token=0.0,
        supports_streaming=False,
        knowledge_cutoff="September 2021",
        model_card_url="https://platform.openai.com/docs/models/text-embedding-3-small",
    ),
    "dall-e-3": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="dall-e-3",
        name="DALL·E 3",
        description="Advanced image generation model with built-in safety moderation",
        capabilities={ModelCapability.IMAGE_GENERATION},
        input_token_limit=4000,  # prompt length
        output_token_limit=0,
        supports_streaming=False,
        model_card_url="https://platform.openai.com/docs/models/dall-e-3",
    ),
    "whisper-1": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="whisper-1",
        name="Whisper",
        description="Speech-to-text model supporting 50+ languages",
        capabilities={ModelCapability.SPEECH_TO_TEXT},
        input_token_limit=0,  # audio input
        output_token_limit=0,
        supports_streaming=False,
        model_card_url="https://platform.openai.com/docs/models/whisper-1",
    ),
    "tts-1": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="tts-1",
        name="TTS Speed",
        description="Speed-optimized text-to-speech model for real-time applications",
        capabilities={ModelCapability.TEXT_TO_SPEECH},
        input_token_limit=4096,
        output_token_limit=0,  # audio output
        supports_streaming=True,
        model_card_url="https://platform.openai.com/docs/models/tts-1",
    ),
    "tts-1-hd": ModelSpec(
        provider=ProviderType.OPENAI,
        model_id="tts-1-hd",
        name="TTS HD",
        description="Quality-optimized text-to-speech model for naturalness",
        capabilities={ModelCapability.TEXT_TO_SPEECH},
        input_token_limit=4096,
        output_token_limit=0,  # audio output
        supports_streaming=True,
        model_card_url="https://platform.openai.com/docs/models/tts-1-hd",
    ),
}

# Anthropic Claude Models - Latest Claude 4 and 3.x series
ANTHROPIC_MODELS = {
    "claude-opus-4-20250514": ModelSpec(
        provider=ProviderType.ANTHROPIC,
        model_id="claude-opus-4-20250514",
        name="Claude Opus 4",
        description="Most capable model with superior reasoning and vision",
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
        description="Intelligent model with high capability and vision",
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
        description="Fastest model for intelligence at blazing speeds",
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

# Google AI Models - Latest Gemini 2.5 and 2.0 series
GOOGLE_MODELS = {
    "gemini-2.5-pro": ModelSpec(
        provider=ProviderType.GOOGLE,
        model_id="gemini-2.5-pro",
        name="Gemini 2.5 Pro",
        description="Advanced multimodal model with enhanced reasoning",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.AUDIO,
            ModelCapability.VIDEO,
            ModelCapability.MULTIMODAL,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=2000000,
        output_token_limit=8192,
        is_multimodal=True,
        knowledge_cutoff="December 2024",
        model_card_url="https://ai.google.dev/models/gemini-2.5-pro",
    ),
    "gemini-2.5-flash": ModelSpec(
        provider=ProviderType.GOOGLE,
        model_id="gemini-2.5-flash",
        name="Gemini 2.5 Flash",
        description="Fast multimodal model optimized for speed",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.AUDIO,
            ModelCapability.VIDEO,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=1000000,
        output_token_limit=8192,
        is_multimodal=True,
        knowledge_cutoff="December 2024",
        model_card_url="https://ai.google.dev/models/gemini-2.5-flash",
    ),
    "gemini-2.0-flash": ModelSpec(
        provider=ProviderType.GOOGLE,
        model_id="gemini-2.0-flash",
        name="Gemini 2.0 Flash",
        description="Fast multimodal model with tool use and code execution",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.AUDIO,
            ModelCapability.VIDEO,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=1000000,
        output_token_limit=8192,
        is_multimodal=True,
        knowledge_cutoff="December 2024",
        model_card_url="https://ai.google.dev/models/gemini-2.0-flash",
    ),
    "imagen-4": ModelSpec(
        provider=ProviderType.GOOGLE,
        model_id="imagen-4",
        name="Imagen 4",
        description="Latest image generation model with improved quality and safety",
        capabilities={ModelCapability.IMAGE_GENERATION},
        input_token_limit=4000,
        output_token_limit=0,
        supports_streaming=False,
        model_card_url="https://ai.google.dev/models/imagen-4",
    ),
}

# xAI Grok Models - Latest Grok 4 and 3 series
XAI_MODELS = {
    "grok-4-latest": ModelSpec(
        provider=ProviderType.XAI,
        model_id="grok-4-latest",
        name="Grok 4",
        description="Latest language model with X platform integration",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.REAL_TIME_SEARCH,
        },
        input_token_limit=256000,
        output_token_limit=8192,
        cost_per_input_token=3.00,
        cost_per_output_token=15.00,
        knowledge_cutoff="July 2025",
        model_card_url="https://docs.x.ai/docs/models/grok-4",
    ),
    "grok-3": ModelSpec(
        provider=ProviderType.XAI,
        model_id="grok-3",
        name="Grok 3",
        description="High-performance language model with function calling",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
        },
        input_token_limit=131072,
        output_token_limit=8192,
        cost_per_input_token=3.00,
        cost_per_output_token=15.00,
        knowledge_cutoff="February 2025",
        model_card_url="https://docs.x.ai/docs/models/grok-3",
    ),
    "grok-3-mini": ModelSpec(
        provider=ProviderType.XAI,
        model_id="grok-3-mini",
        name="Grok 3 Mini",
        description="Cost-efficient language model with function calling",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
        },
        input_token_limit=131072,
        output_token_limit=8192,
        cost_per_input_token=0.30,
        cost_per_output_token=0.50,
        knowledge_cutoff="February 2025",
        model_card_url="https://docs.x.ai/docs/models/grok-3-mini",
    ),
}

# Groq Models - Hardware-accelerated inference
GROQ_MODELS = {
    "llama-3.1-405b": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="llama-3.1-405b",
        name="Llama 3.1 405B",
        description="Large context reasoning model with ultra-fast inference",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=128000,
        output_token_limit=8192,
        knowledge_cutoff="April 2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
    "llama-3.1-70b": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="llama-3.1-70b",
        name="Llama 3.1 70B",
        description="Versatile instruction-following model with fast inference",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=128000,
        output_token_limit=8192,
        knowledge_cutoff="April 2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
    "llama-3.1-8b": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="llama-3.1-8b",
        name="Llama 3.1 8B",
        description="Efficient model for lighter workloads with ultra-fast inference",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=128000,
        output_token_limit=8192,
        knowledge_cutoff="April 2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
}

# Qwen Models - Chinese language optimization and multimodal
QWEN_MODELS = {
    "qwen2.5": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="qwen2.5",
        name="Qwen 2.5",
        description="Latest generation model with improved capabilities",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=128000,
        output_token_limit=8192,
        model_card_url="https://help.aliyun.com/zh/dashscope/",
    ),
    "qwen-vl": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="qwen-vl",
        name="Qwen-VL",
        description="Vision-language model for multimodal tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=128000,
        output_token_limit=8192,
        is_multimodal=True,
        model_card_url="https://help.aliyun.com/zh/dashscope/",
    ),
    "codeqwen": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="codeqwen",
        name="CodeQwen",
        description="Specialized model for code generation and programming tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=128000,
        output_token_limit=8192,
        model_card_url="https://help.aliyun.com/zh/dashscope/",
    ),
}

# Combined model registry
ALL_MODELS: Dict[str, ModelSpec] = {
    **OPENAI_MODELS,
    **ANTHROPIC_MODELS,
    **GOOGLE_MODELS,
    **XAI_MODELS,
    **GROQ_MODELS,
    **QWEN_MODELS,
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
    "text_generation": "gpt-4o-mini",
    "reasoning": "o3-mini",
    "advanced_reasoning": "claude-sonnet-4-20250514",
    "fast_inference": "llama-3.1-70b",
    "multimodal": "gemini-2.5-flash",
    "vision": "gpt-4o",
    "code_generation": "o3-mini",
    "embeddings": "text-embedding-3-small",
    "image_generation": "dall-e-3",
    "speech_to_text": "whisper-1",
    "text_to_speech": "tts-1",
    "real_time_search": "grok-4-latest",
}


# Version lock to prevent model downgrades
MODEL_REGISTRY_VERSION = "2025.01.25"
MINIMUM_SUPPORTED_MODELS = {
    "openai": ["gpt-4o", "gpt-4o-mini", "o3-mini"],
    "anthropic": ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219"],
    "google": ["gemini-2.5-pro", "gemini-2.5-flash"],
    "xai": ["grok-4-latest", "grok-3"],
    "groq": ["llama-3.1-70b"],
    "qwen": ["qwen2.5"],
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