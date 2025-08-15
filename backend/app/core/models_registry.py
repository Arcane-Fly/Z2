"""
Model Registry for Z2 AI Workforce Platform

This module contains the complete registry of all supported AI models and providers.
It serves as the single source of truth for model specifications and capabilities.

IMPORTANT: This registry defines production model specifications.
Changes to this file should be carefully reviewed to prevent model downgrades or reversions.
"""

from dataclasses import dataclass
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
    GOOGLE = "google"
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
    capabilities: set[ModelCapability]
    input_token_limit: int
    output_token_limit: int
    supports_streaming: bool = True
    supports_system_message: bool = True
    cost_per_input_token: float | None = None  # USD per 1M tokens
    cost_per_output_token: float | None = None  # USD per 1M tokens
    context_window: int | None = None
    model_card_url: str | None = None
    is_reasoning_model: bool = False
    is_multimodal: bool = False
    knowledge_cutoff: str | None = None


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
        cost_per_input_token=3.00,  # USD per 1M tokens
        cost_per_output_token=12.00,  # USD per 1M tokens
        context_window=200000,
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
        cost_per_input_token=20.00,  # USD per 1M tokens
        cost_per_output_token=60.00,  # USD per 1M tokens
        context_window=200000,
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
        cost_per_input_token=5.00,  # USD per 1M tokens
        cost_per_output_token=15.00,  # USD per 1M tokens
        context_window=1000000,
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
        cost_per_input_token=2.50,  # USD per 1M tokens
        cost_per_output_token=10.00,  # USD per 1M tokens
        context_window=128000,
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
        cost_per_input_token=0.15,  # USD per 1M tokens
        cost_per_output_token=0.60,  # USD per 1M tokens
        context_window=1000000,
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
        context_window=200000,
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
        context_window=200000,
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
    "grok-3": ModelSpec(
        provider=ProviderType.XAI,
        model_id="grok-3",
        name="Grok 3",
        description="Latest generation Grok model with enhanced reasoning",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REAL_TIME_SEARCH,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=200000,
        output_token_limit=32000,
        cost_per_input_token=2.50,
        cost_per_output_token=12.50,
        context_window=200000,
        knowledge_cutoff="2024",
    ),
    "grok-4": ModelSpec(
        provider=ProviderType.XAI,
        model_id="grok-4",
        name="Grok 4",
        description="Most advanced Grok model with superior reasoning capabilities",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REAL_TIME_SEARCH,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=200000,
        output_token_limit=32000,
        cost_per_input_token=3.00,
        cost_per_output_token=15.00,
        context_window=200000,
        knowledge_cutoff="2024",
    ),
}

# Google AI Models - Gemini Series
GOOGLE_MODELS = {
    "gemini-2.5-flash": ModelSpec(
        provider=ProviderType.GOOGLE,
        model_id="gemini-2.5-flash",
        name="Gemini 2.5 Flash",
        description="Fast, versatile performance across a broad range of tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.AUDIO,
            ModelCapability.VIDEO,
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=1000000,
        output_token_limit=8192,
        cost_per_input_token=0.075,  # USD per 1M tokens
        cost_per_output_token=0.30,  # USD per 1M tokens
        context_window=1000000,
        is_multimodal=True,
        knowledge_cutoff="November 2024",
        model_card_url="https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.5-flash",
    ),
    "gemini-2.5-pro": ModelSpec(
        provider=ProviderType.GOOGLE,
        model_id="gemini-2.5-pro",
        name="Gemini 2.5 Pro",
        description="Most capable model for complex reasoning tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.AUDIO,
            ModelCapability.VIDEO,
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.REASONING,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=2000000,
        output_token_limit=8192,
        cost_per_input_token=1.25,  # USD per 1M tokens
        cost_per_output_token=5.00,  # USD per 1M tokens
        context_window=2000000,
        is_multimodal=True,
        knowledge_cutoff="November 2024",
        model_card_url="https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.5-pro",
    ),
}

# Groq Models - High-speed inference
GROQ_MODELS = {
    "llama-3.3-70b-versatile": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="llama-3.3-70b-versatile",
        name="Llama 3.3 70B Versatile",
        description="Meta's flagship model optimized for versatile use cases",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=0.59,  # USD per 1M tokens
        cost_per_output_token=0.79,  # USD per 1M tokens
        context_window=32768,
        knowledge_cutoff="December 2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
    "llama-3.1-405b-reasoning": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="llama-3.1-405b-reasoning",
        name="Llama 3.1 405B Reasoning",
        description="Meta's largest model optimized for complex reasoning",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=2.38,  # USD per 1M tokens
        cost_per_output_token=2.38,  # USD per 1M tokens
        context_window=32768,
        is_reasoning_model=True,
        knowledge_cutoff="July 2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
    "llama-3.1-70b-versatile": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="llama-3.1-70b-versatile",
        name="Llama 3.1 70B Versatile",
        description="Versatile model balancing capability and speed",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=0.59,  # USD per 1M tokens
        cost_per_output_token=0.79,  # USD per 1M tokens
        context_window=32768,
        knowledge_cutoff="July 2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
    "llama-3.1-8b-instant": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="llama-3.1-8b-instant",
        name="Llama 3.1 8B Instant",
        description="Fast and efficient model for quick responses",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=0.05,  # USD per 1M tokens
        cost_per_output_token=0.08,  # USD per 1M tokens
        context_window=32768,
        knowledge_cutoff="July 2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
    "gemma3-9b-it": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="gemma3-9b-it",
        name="Gemma 3 9B IT",
        description="Google's Gemma 3 model optimized for instruction following",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=8192,
        output_token_limit=8192,
        cost_per_input_token=0.20,  # USD per 1M tokens
        cost_per_output_token=0.20,  # USD per 1M tokens
        context_window=8192,
        knowledge_cutoff="2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
    "gemma3-27b-it": ModelSpec(
        provider=ProviderType.GROQ,
        model_id="gemma3-27b-it",
        name="Gemma 3 27B IT",
        description="Google's larger Gemma 3 model for enhanced performance",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=8192,
        output_token_limit=8192,
        cost_per_input_token=0.35,  # USD per 1M tokens
        cost_per_output_token=0.35,  # USD per 1M tokens
        context_window=8192,
        knowledge_cutoff="2024",
        model_card_url="https://console.groq.com/docs/models",
    ),
}

# Perplexity AI Models - Search-augmented models
PERPLEXITY_MODELS = {
    "llama-3.1-sonar-large-128k-online": ModelSpec(
        provider=ProviderType.PERPLEXITY,
        model_id="llama-3.1-sonar-large-128k-online",
        name="Llama 3.1 Sonar Large 128K Online",
        description="Large model with real-time search capabilities",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REAL_TIME_SEARCH,
            ModelCapability.WEB_BROWSING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=127072,
        output_token_limit=4096,
        cost_per_input_token=1.00,  # USD per 1M tokens
        cost_per_output_token=1.00,  # USD per 1M tokens
        context_window=127072,
        knowledge_cutoff="Real-time",
        model_card_url="https://docs.perplexity.ai/docs/model-cards",
    ),
    "llama-3.1-sonar-small-128k-online": ModelSpec(
        provider=ProviderType.PERPLEXITY,
        model_id="llama-3.1-sonar-small-128k-online",
        name="Llama 3.1 Sonar Small 128K Online",
        description="Smaller, faster model with real-time search",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REAL_TIME_SEARCH,
            ModelCapability.WEB_BROWSING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=127072,
        output_token_limit=4096,
        cost_per_input_token=0.20,  # USD per 1M tokens
        cost_per_output_token=0.20,  # USD per 1M tokens
        context_window=127072,
        knowledge_cutoff="Real-time",
        model_card_url="https://docs.perplexity.ai/docs/model-cards",
    ),
    "llama-3.1-sonar-huge-128k-online": ModelSpec(
        provider=ProviderType.PERPLEXITY,
        model_id="llama-3.1-sonar-huge-128k-online",
        name="Llama 3.1 Sonar Huge 128K Online",
        description="Most capable search-augmented model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REAL_TIME_SEARCH,
            ModelCapability.WEB_BROWSING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=127072,
        output_token_limit=4096,
        cost_per_input_token=5.00,  # USD per 1M tokens
        cost_per_output_token=5.00,  # USD per 1M tokens
        context_window=127072,
        is_reasoning_model=True,
        knowledge_cutoff="Real-time",
        model_card_url="https://docs.perplexity.ai/docs/model-cards",
    ),
}

# Moonshot AI Models - Chinese AI company models
MOONSHOT_MODELS = {
    "moonshot-v1-8k": ModelSpec(
        provider=ProviderType.MOONSHOT,
        model_id="moonshot-v1-8k",
        name="Moonshot v1 8K",
        description="Moonshot's base model with 8K context",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=8000,
        output_token_limit=8000,
        cost_per_input_token=1.00,  # USD per 1M tokens
        cost_per_output_token=1.00,  # USD per 1M tokens
        context_window=8000,
        knowledge_cutoff="2024",
    ),
    "moonshot-v1-32k": ModelSpec(
        provider=ProviderType.MOONSHOT,
        model_id="moonshot-v1-32k",
        name="Moonshot v1 32K",
        description="Moonshot's model with extended 32K context",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=32000,
        output_token_limit=32000,
        cost_per_input_token=2.00,  # USD per 1M tokens
        cost_per_output_token=2.00,  # USD per 1M tokens
        context_window=32000,
        knowledge_cutoff="2024",
    ),
    "moonshot-v1-128k": ModelSpec(
        provider=ProviderType.MOONSHOT,
        model_id="moonshot-v1-128k",
        name="Moonshot v1 128K",
        description="Moonshot's model with large 128K context window",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=128000,
        output_token_limit=128000,
        cost_per_input_token=5.00,  # USD per 1M tokens
        cost_per_output_token=5.00,  # USD per 1M tokens
        context_window=128000,
        knowledge_cutoff="2024",
    ),
}

# Qwen Models - Alibaba Cloud's AI models
QWEN_MODELS = {
    "qwen3-72b-instruct": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="qwen3-72b-instruct",
        name="Qwen3 72B Instruct",
        description="Large language model optimized for instruction following",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=0.50,  # USD per 1M tokens
        cost_per_output_token=1.50,  # USD per 1M tokens
        context_window=32768,
        knowledge_cutoff="2024",
    ),
    "qwen3-32b-instruct": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="qwen3-32b-instruct",
        name="Qwen3 32B Instruct",
        description="Mid-size model balancing performance and efficiency",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=0.30,  # USD per 1M tokens
        cost_per_output_token=1.00,  # USD per 1M tokens
        context_window=32768,
        knowledge_cutoff="2024",
    ),
    "qwen3-14b-instruct": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="qwen3-14b-instruct",
        name="Qwen3 14B Instruct",
        description="Efficient model for general-purpose tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=0.20,  # USD per 1M tokens
        cost_per_output_token=0.60,  # USD per 1M tokens
        context_window=32768,
        knowledge_cutoff="2024",
    ),
    "qwen3-7b-instruct": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="qwen3-7b-instruct",
        name="Qwen3 7B Instruct",
        description="Fast and cost-effective model for basic tasks",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=0.07,  # USD per 1M tokens
        cost_per_output_token=0.07,  # USD per 1M tokens
        context_window=32768,
        knowledge_cutoff="2024",
    ),
    "qwen3-reasoning-preview": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="qwen3-reasoning-preview",
        name="Qwen3 Reasoning Preview",
        description="Reasoning model with step-by-step thinking capabilities",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=1.00,  # USD per 1M tokens
        cost_per_output_token=1.00,  # USD per 1M tokens
        context_window=32768,
        is_reasoning_model=True,
        knowledge_cutoff="2024",
    ),
    "qwen3-vl-72b-instruct": ModelSpec(
        provider=ProviderType.QWEN,
        model_id="qwen3-vl-72b-instruct",
        name="Qwen3 VL 72B Instruct",
        description="Large vision-language model",
        capabilities={
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.MULTIMODAL,
        },
        input_token_limit=32768,
        output_token_limit=32768,
        cost_per_input_token=1.00,  # USD per 1M tokens
        cost_per_output_token=1.00,  # USD per 1M tokens
        context_window=32768,
        is_multimodal=True,
        knowledge_cutoff="2024",
    ),
}

# Combined model registry
ALL_MODELS: dict[str, ModelSpec] = {
    **OPENAI_MODELS,
    **ANTHROPIC_MODELS,
    **XAI_MODELS,
    **GOOGLE_MODELS,
    **GROQ_MODELS,
    **PERPLEXITY_MODELS,
    **MOONSHOT_MODELS,
    **QWEN_MODELS,
}


def get_model_by_id(model_id: str) -> ModelSpec | None:
    """Get a model specification by its ID."""
    return ALL_MODELS.get(model_id)


def get_models_by_provider(provider: ProviderType) -> dict[str, ModelSpec]:
    """Get all models for a specific provider."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if spec.provider == provider
    }


def get_models_by_capability(capability: ModelCapability) -> dict[str, ModelSpec]:
    """Get all models that support a specific capability."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if capability in spec.capabilities
    }


def get_reasoning_models() -> dict[str, ModelSpec]:
    """Get all models optimized for reasoning tasks."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if spec.is_reasoning_model
    }


def get_multimodal_models() -> dict[str, ModelSpec]:
    """Get all multimodal models."""
    return {
        model_id: spec for model_id, spec in ALL_MODELS.items() if spec.is_multimodal
    }


def get_cost_efficient_models(max_input_cost: float = 1.0) -> dict[str, ModelSpec]:
    """Get models under a certain cost threshold per million input tokens."""
    return {
        model_id: spec
        for model_id, spec in ALL_MODELS.items()
        if spec.cost_per_input_token is not None
        and spec.cost_per_input_token <= max_input_cost
    }


def validate_model_support(
    model_id: str, required_capabilities: list[ModelCapability]
) -> bool:
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
    "multimodal": "gemini-2.5-flash",
    "vision": "gemini-2.5-flash",
    "code_generation": "llama-3.3-70b-versatile",
    "embeddings": "text-embedding-3-small",
    "image_generation": "gpt-image-1",
    "speech_to_text": "whisper-1",
    "text_to_speech": "tts-1",
    "real_time_search": "llama-3.1-sonar-large-128k-online",
    "fast_model": "llama-3.1-8b-instant",
    "cost_efficient": "qwen3-7b-instruct",
    "multilingual": "qwen3-72b-instruct",
    "chinese": "moonshot-v1-32k",
}


# Version lock to prevent model downgrades
MODEL_REGISTRY_VERSION = "2025.01.25"
MINIMUM_SUPPORTED_MODELS = {
    "openai": [
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4o",
        "o4-mini",
        "o3",
        "o4-mini-deep-research-2025-06-26",
    ],
    "anthropic": ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219"],
    "xai": ["grok-3", "grok-4"],
    "google": ["gemini-2.5-flash", "gemini-2.5-pro"],
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
    "perplexity": ["llama-3.1-sonar-large-128k-online"],
    "moonshot": ["moonshot-v1-32k"],
    "qwen": ["qwen3-72b-instruct", "qwen3-reasoning-preview"],
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
