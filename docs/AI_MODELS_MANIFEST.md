# Complete AI Models & API Documentation

## Table of Contents

- [OpenAI Models](#openai-models)
- [Google AI Models](#google-ai-models)
- [Anthropic Claude Models](#anthropic-claude-models)
- [xAI Grok Models](#xai-grok-models)
- [Groq Models](#groq-models)
- [Perplexity AI Models](#perplexity-ai-models)
- [Moonshot AI Models](#moonshot-ai-models)
- [Qwen Models](#qwen-models)
- [Model Registry Statistics](#model-registry-statistics)
- [Model Selection Guidelines](#model-selection-guidelines)

---

## Overview

Z2 AI Workforce Platform supports **58 AI models** across **8 major providers**, providing comprehensive coverage for all AI workload requirements. This manifest documents all supported models with their capabilities, specifications, and recommended use cases.

## OpenAI Models

### GPT-4o
- **Model Code**: `gpt-4o`
- **Last Updated**: October 2024
- **Description**: OpenAI's flagship multimodal model that accepts text, audio, image, and video inputs, and can output text, audio, and images. Best choice for advanced tool use, vision, and multimodal workflows.
- **Status**: Active
- **Inputs**: text, audio, image, video
- **Outputs**: text, audio, image
- **Input Token Limit**: 128,000 tokens
- **Output Token Limit**: 16,384 tokens
- **Key Features**: Multimodal capabilities, Advanced tool use, Vision processing, Real-time audio processing, Function calling, Structured outputs
- **Model Card**: https://platform.openai.com/docs/models/gpt-4o

### GPT-4o mini
- **Model Code**: `gpt-4o-mini`
- **Last Updated**: October 2024
- **Description**: Cost-efficient small multimodal model with strong performance on text and image tasks. Video and audio capabilities coming soon.
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 128,000 tokens
- **Output Token Limit**: 16,384 tokens
- **Key Features**: Cost-efficient, Text and image processing, Video and audio capabilities coming soon, MMLU: 82.0%, MGSM: 87.0%, HumanEval: 87.2%, MMMU: 59.4%, Function calling, Structured outputs
- **Model Card**: https://platform.openai.com/docs/models/gpt-4o-mini

### GPT-4.1
- **Model Code**: `gpt-4.1`
- **Last Updated**: April 2025
- **Description**: Flagship GPT model for complex tasks with massive context window
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 1,000,000 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Massive context, Advanced reasoning, Multimodal processing, Function calling
- **Cost**: $5.00 input / $15.00 output per 1M tokens
- **Model Card**: https://platform.openai.com/docs/models/gpt-4.1

### GPT-4.1 mini
- **Model Code**: `gpt-4.1-mini`
- **Last Updated**: April 2025
- **Description**: Balanced for intelligence, speed, and cost with large context window
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 1,000,000 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Cost-efficient, Large context, Multimodal processing
- **Cost**: $0.15 input / $0.60 output per 1M tokens
- **Model Card**: https://platform.openai.com/docs/models/gpt-4.1-mini

### GPT-4.1 nano
- **Model Code**: `gpt-4.1-nano`
- **Last Updated**: April 2025
- **Description**: Fastest, most cost-effective GPT-4.1 model
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 1,000,000 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Ultra-fast response, Maximum cost efficiency, Large context
- **Model Card**: https://platform.openai.com/docs/models/gpt-4.1-nano

### o3
- **Model Code**: `o3`
- **Last Updated**: April 2025
- **Description**: Our most powerful reasoning model
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 100,000 tokens
- **Key Features**: Advanced reasoning, Step-by-step thinking, Complex problem solving
- **Cost**: $20.00 input / $60.00 output per 1M tokens
- **Model Card**: https://platform.openai.com/docs/models/o3

### o3-mini
- **Model Code**: `o3-mini`
- **Last Updated**: January 2025
- **Description**: A small model alternative to o3 for reasoning tasks
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 100,000 tokens
- **Key Features**: Reasoning optimization, Cost-effective, Mathematical problem solving
- **Model Card**: https://platform.openai.com/docs/models/o3-mini

### o4-mini
- **Model Code**: `o4-mini`
- **Last Updated**: April 2025
- **Description**: Faster, more affordable reasoning model
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 100,000 tokens
- **Key Features**: Fast reasoning, Affordable pricing, Code generation
- **Cost**: $3.00 input / $12.00 output per 1M tokens
- **Model Card**: https://platform.openai.com/docs/models/o4-mini

### Additional OpenAI Models
- **o3-pro**: Premium version of o3 with enhanced compute
- **o3-deep-research**: Specialized for deep research tasks
- **o4-mini-deep-research**: Fast deep research model
- **GPT Image 1**: State-of-the-art image generation
- **TTS-1 & TTS-1 HD**: Text-to-speech models
- **Whisper-1**: Speech recognition model
- **Text Embedding 3**: Small and large embedding models
- **Realtime Models**: GPT-4o realtime preview models

**Total OpenAI Models**: 31

---

## Google AI Models

### Gemini 2.5 Flash
- **Model Code**: `gemini-2.5-flash`
- **Last Updated**: November 2024
- **Description**: Fast, versatile performance across a broad range of tasks
- **Status**: Active
- **Inputs**: text, image, audio, video
- **Outputs**: text
- **Input Token Limit**: 1,000,000 tokens
- **Output Token Limit**: 8,192 tokens
- **Key Features**: Multimodal processing, Fast inference, Large context window
- **Cost**: $0.075 input / $0.30 output per 1M tokens
- **Model Card**: https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.5-flash

### Gemini 2.5 Pro
- **Model Code**: `gemini-2.5-pro`
- **Last Updated**: November 2024
- **Description**: Most capable model for complex reasoning tasks
- **Status**: Active
- **Inputs**: text, image, audio, video
- **Outputs**: text
- **Input Token Limit**: 2,000,000 tokens
- **Output Token Limit**: 8,192 tokens
- **Key Features**: Advanced reasoning, Multimodal processing, Massive context
- **Cost**: $1.25 input / $5.00 output per 1M tokens
- **Model Card**: https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.5-pro

**Total Google Models**: 2

---

## Anthropic Claude Models

### Claude Opus 4
- **Model Code**: `claude-opus-4-20250514`
- **Last Updated**: March 2025
- **Description**: Our most capable model with exceptional reasoning and analysis
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 32,000 tokens
- **Key Features**: Maximum capability, Advanced reasoning, Vision processing
- **Cost**: $15.00 input / $75.00 output per 1M tokens

### Claude Sonnet 4
- **Model Code**: `claude-sonnet-4-20250514`
- **Last Updated**: March 2025
- **Description**: High-performance model with exceptional reasoning
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 64,000 tokens
- **Key Features**: Balanced performance, Advanced reasoning, Large output
- **Cost**: $3.00 input / $15.00 output per 1M tokens

### Claude Sonnet 3.7
- **Model Code**: `claude-3-7-sonnet-20250219`
- **Last Updated**: November 2024
- **Description**: High-performance model with toggleable extended thinking
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 64,000 tokens
- **Key Features**: Extended thinking mode, Reasoning capabilities, Vision processing
- **Cost**: $3.00 input / $15.00 output per 1M tokens

### Claude Sonnet 3.5
- **Model Code**: `claude-3-5-sonnet-20241022`
- **Last Updated**: April 2024
- **Description**: Our previous intelligent model
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 8,192 tokens
- **Key Features**: Proven performance, Vision processing, Code generation
- **Cost**: $3.00 input / $15.00 output per 1M tokens

### Claude Haiku 3.5
- **Model Code**: `claude-3-5-haiku-20241022`
- **Last Updated**: July 2024
- **Description**: Our fastest model for intelligence at blazing speeds
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 8,192 tokens
- **Key Features**: Maximum speed, Cost efficiency, Vision processing
- **Cost**: $0.80 input / $4.00 output per 1M tokens

**Total Anthropic Models**: 5

---

## xAI Grok Models

### Grok 3
- **Model Code**: `grok-3`
- **Last Updated**: 2024
- **Description**: Latest generation Grok model with enhanced reasoning
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 32,000 tokens
- **Key Features**: Enhanced reasoning, Real-time search, Code generation
- **Cost**: $2.50 input / $12.50 output per 1M tokens

### Grok 4
- **Model Code**: `grok-4`
- **Last Updated**: 2024
- **Description**: Most advanced Grok model with superior reasoning capabilities
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 200,000 tokens
- **Output Token Limit**: 32,000 tokens
- **Key Features**: Superior reasoning, Real-time search, Advanced problem solving
- **Cost**: $3.00 input / $15.00 output per 1M tokens

**Total xAI Models**: 2

---

## Groq Models

### Llama 3.3 70B Versatile
- **Model Code**: `llama-3.3-70b-versatile`
- **Last Updated**: December 2024
- **Description**: Meta's flagship model optimized for versatile use cases
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Ultra-fast inference, Versatile applications, Code generation
- **Cost**: $0.59 input / $0.79 output per 1M tokens

### Llama 3.1 405B Reasoning
- **Model Code**: `llama-3.1-405b-reasoning`
- **Last Updated**: July 2024
- **Description**: Meta's largest model optimized for complex reasoning
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Maximum capability, Advanced reasoning, Complex problem solving
- **Cost**: $2.38 input / $2.38 output per 1M tokens

### Llama 3.1 70B Versatile
- **Model Code**: `llama-3.1-70b-versatile`
- **Last Updated**: July 2024
- **Description**: Versatile model balancing capability and speed
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Balanced performance, Fast inference, General purpose
- **Cost**: $0.59 input / $0.79 output per 1M tokens

### Llama 3.1 8B Instant
- **Model Code**: `llama-3.1-8b-instant`
- **Last Updated**: July 2024
- **Description**: Fast and efficient model for quick responses
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Ultra-fast responses, Maximum cost efficiency, Instant inference
- **Cost**: $0.05 input / $0.08 output per 1M tokens

### Gemma 3 9B IT
- **Model Code**: `gemma3-9b-it`
- **Last Updated**: 2024
- **Description**: Google's Gemma 3 model optimized for instruction following
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 8,192 tokens
- **Output Token Limit**: 8,192 tokens
- **Key Features**: Latest Gemma generation, Fast inference, Cost-effective
- **Cost**: $0.20 input / $0.20 output per 1M tokens

### Gemma 3 27B IT
- **Model Code**: `gemma3-27b-it`
- **Last Updated**: 2024
- **Description**: Google's larger Gemma 3 model for enhanced performance
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 8,192 tokens
- **Output Token Limit**: 8,192 tokens
- **Key Features**: Enhanced reasoning, Fast inference, Improved capabilities
- **Cost**: $0.35 input / $0.35 output per 1M tokens

**Total Groq Models**: 6

---

## Perplexity AI Models

### Llama 3.1 Sonar Large 128K Online
- **Model Code**: `llama-3.1-sonar-large-128k-online`
- **Last Updated**: Real-time
- **Description**: Large model with real-time search capabilities
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 127,072 tokens
- **Output Token Limit**: 4,096 tokens
- **Key Features**: Real-time search, Web browsing, Current information
- **Cost**: $1.00 input / $1.00 output per 1M tokens

### Llama 3.1 Sonar Small 128K Online
- **Model Code**: `llama-3.1-sonar-small-128k-online`
- **Last Updated**: Real-time
- **Description**: Smaller, faster model with real-time search
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 127,072 tokens
- **Output Token Limit**: 4,096 tokens
- **Key Features**: Fast search, Cost-effective, Real-time information
- **Cost**: $0.20 input / $0.20 output per 1M tokens

### Llama 3.1 Sonar Huge 128K Online
- **Model Code**: `llama-3.1-sonar-huge-128k-online`
- **Last Updated**: Real-time
- **Description**: Most capable search-augmented model
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 127,072 tokens
- **Output Token Limit**: 4,096 tokens
- **Key Features**: Maximum search capability, Advanced reasoning, Real-time data
- **Cost**: $5.00 input / $5.00 output per 1M tokens

**Total Perplexity Models**: 3

---

## Moonshot AI Models

### Moonshot v1 8K
- **Model Code**: `moonshot-v1-8k`
- **Last Updated**: 2024
- **Description**: Moonshot's base model with 8K context
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 8,000 tokens
- **Output Token Limit**: 8,000 tokens
- **Key Features**: Chinese language optimization, Cost-effective, General purpose
- **Cost**: $1.00 input / $1.00 output per 1M tokens

### Moonshot v1 32K
- **Model Code**: `moonshot-v1-32k`
- **Last Updated**: 2024
- **Description**: Moonshot's model with extended 32K context
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,000 tokens
- **Output Token Limit**: 32,000 tokens
- **Key Features**: Extended context, Chinese language support, Balanced performance
- **Cost**: $2.00 input / $2.00 output per 1M tokens

### Moonshot v1 128K
- **Model Code**: `moonshot-v1-128k`
- **Last Updated**: 2024
- **Description**: Moonshot's model with large 128K context window
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 128,000 tokens
- **Output Token Limit**: 128,000 tokens
- **Key Features**: Large context, Document processing, Chinese language excellence
- **Cost**: $5.00 input / $5.00 output per 1M tokens

**Total Moonshot Models**: 3

---

## Qwen Models

### Qwen3 72B Instruct
- **Model Code**: `qwen3-72b-instruct`
- **Last Updated**: 2024
- **Description**: Large language model optimized for instruction following
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Latest Qwen generation, Advanced reasoning, Multilingual support
- **Cost**: $0.50 input / $1.50 output per 1M tokens

### Qwen3 32B Instruct
- **Model Code**: `qwen3-32b-instruct`
- **Last Updated**: 2024
- **Description**: Mid-size model balancing performance and efficiency
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Enhanced reasoning, Cost efficiency, Improved capabilities
- **Cost**: $0.30 input / $1.00 output per 1M tokens

### Qwen3 14B Instruct
- **Model Code**: `qwen3-14b-instruct`
- **Last Updated**: 2024
- **Description**: Efficient model for general-purpose tasks
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: General purpose, Fast inference, Cost-effective
- **Cost**: $0.20 input / $0.60 output per 1M tokens

### Qwen3 7B Instruct
- **Model Code**: `qwen3-7b-instruct`
- **Last Updated**: 2024
- **Description**: Fast and cost-effective model for basic tasks
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Ultra cost efficiency, Fast responses, Enhanced performance
- **Cost**: $0.07 input / $0.07 output per 1M tokens

### Qwen3 Reasoning Preview
- **Model Code**: `qwen3-reasoning-preview`
- **Last Updated**: 2024
- **Description**: Reasoning model with step-by-step thinking capabilities
- **Status**: Active
- **Inputs**: text
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Advanced reasoning, Step-by-step thinking, Problem solving
- **Cost**: $1.00 input / $1.00 output per 1M tokens

### Qwen3 VL 72B Instruct
- **Model Code**: `qwen3-vl-72b-instruct`
- **Last Updated**: 2024
- **Description**: Large vision-language model
- **Status**: Active
- **Inputs**: text, image
- **Outputs**: text
- **Input Token Limit**: 32,768 tokens
- **Output Token Limit**: 32,768 tokens
- **Key Features**: Latest VL capabilities, Multimodal processing, Enhanced vision
- **Cost**: $1.00 input / $1.00 output per 1M tokens

**Total Qwen Models**: 6

---

## Model Registry Statistics

### Total Model Count: 58
- **OpenAI**: 31 models (53.4%)
- **Google**: 2 models (3.4%)
- **Anthropic**: 5 models (8.6%)
- **Groq**: 6 models (10.3%)
- **Perplexity**: 3 models (5.2%)
- **xAI**: 2 models (3.4%)
- **Moonshot**: 3 models (5.2%)
- **Qwen**: 6 models (10.3%)

### Capability Distribution
- **Text Generation**: 62 models (100%)
- **Code Generation**: 55 models (88.7%)
- **Vision Processing**: 19 models (30.6%)
- **Reasoning**: 17 models (27.4%)
- **Multimodal**: 14 models (22.6%)
- **Real-time Search**: 7 models (11.3%)
- **Function Calling**: 11 models (17.7%)
- **Audio Processing**: 8 models (12.9%)
- **Video Processing**: 4 models (6.5%)

### Context Window Distribution
- **1M+ tokens**: 8 models (12.9%)
- **200K+ tokens**: 15 models (24.2%)
- **128K+ tokens**: 8 models (12.9%)
- **32K+ tokens**: 25 models (40.3%)
- **8K+ tokens**: 6 models (9.7%)

---

## Model Selection Guidelines

### Default Model Routing
- **Text Generation**: `gpt-4.1-mini`
- **Reasoning**: `o4-mini`
- **Advanced Reasoning**: `claude-sonnet-4-20250514`
- **Flagship**: `gpt-4.1`
- **Multimodal**: `gemini-2.5-flash`
- **Vision**: `gemini-2.5-flash`
- **Code Generation**: `llama-3.3-70b-versatile`
- **Real-time Search**: `llama-3.1-sonar-large-128k-online`
- **Fast Model**: `llama-3.1-8b-instant`
- **Cost Efficient**: `qwen3-7b-instruct`
- **Multilingual**: `qwen3-72b-instruct`
- **Chinese**: `moonshot-v1-32k`

### Use Case Recommendations

#### For Code Generation
1. **High Performance**: `o4-mini`, `claude-sonnet-4-20250514`
2. **Fast & Efficient**: `llama-3.3-70b-versatile`, `llama-3.1-70b-versatile`
3. **Cost Optimized**: `llama-3.1-8b-instant`, `qwen3-7b-instruct`

#### For Reasoning Tasks
1. **Maximum Capability**: `o3`, `claude-opus-4-20250514`
2. **Balanced**: `o4-mini`, `claude-sonnet-4-20250514`
3. **Fast**: `llama-3.1-405b-reasoning`, `qwen3-reasoning-preview`

#### For Multimodal Tasks
1. **Best Overall**: `gemini-2.5-pro`, `gpt-4.1`
2. **Fast & Efficient**: `gemini-2.5-flash`, `gpt-4o`
3. **Vision Specialized**: `qwen3-vl-72b-instruct`

#### For Real-time Information
1. **Best Search**: `llama-3.1-sonar-huge-128k-online`
2. **Balanced**: `llama-3.1-sonar-large-128k-online`, `grok-4`
3. **Fast**: `llama-3.1-sonar-small-128k-online`, `grok-3`

#### For Cost Optimization
1. **Ultra Low Cost**: `qwen3-7b-instruct` ($0.07/$0.07)
2. **Low Cost**: `llama-3.1-8b-instant` ($0.05/$0.08)
3. **Budget Friendly**: `gemini-2.5-flash` ($0.075/$0.30)

#### For Large Context
1. **Largest**: `gemini-2.5-pro` (2M tokens)
2. **OpenAI**: `gpt-4.1` (1M tokens)
3. **Alternative**: `moonshot-v1-128k` (128K tokens)

### Provider-Specific Strengths

- **OpenAI**: Reasoning models, function calling, structured outputs
- **Google**: Multimodal processing, large context windows, cost efficiency
- **Anthropic**: Advanced reasoning, safety, long-form content
- **Groq**: Ultra-fast inference, cost efficiency, code generation
- **Perplexity**: Real-time search, current information, web browsing
- **xAI**: Real-time search, current events, unfiltered responses
- **Moonshot**: Chinese language, document processing, local deployment
- **Qwen**: Multilingual support, cost efficiency, reasoning capabilities

---

## API Integration

All models are accessible through the Z2 unified API with automatic provider routing, load balancing, and failover capabilities. Model selection can be:

1. **Automatic**: Based on task type and requirements
2. **Manual**: Explicit model specification in API calls
3. **Policy-based**: Organization-defined model preferences

For detailed API documentation, see [API Documentation](setup/api-documentation.md).

---

*This manifest is automatically generated from the Z2 models registry and is updated with each registry change. Last updated: 2025-01-25*