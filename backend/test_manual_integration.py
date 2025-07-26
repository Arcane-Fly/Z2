#!/usr/bin/env python3
"""
Manual test script for LLM integration functionality.
This allows testing the complete system without requiring actual API keys.
"""

import asyncio
import os
import sys

# Add the app to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.basic_agent import BasicAIAgent
from app.core.models_registry import (
    ALL_MODELS, 
    get_model_by_id, 
    get_models_by_capability,
    ModelCapability,
    DEFAULT_MODEL_ROUTING
)
from app.core.cache_and_rate_limit import get_cache, get_rate_limiter


async def test_model_registry():
    """Test the model registry functionality."""
    print("=== Testing Model Registry ===")
    
    # Test basic model retrieval
    gpt4_model = get_model_by_id("gpt-4.1")
    print(f"GPT-4.1 model: {gpt4_model.name if gpt4_model else 'Not found'}")
    
    # Test filtering by capability
    reasoning_models = get_models_by_capability(ModelCapability.REASONING)
    print(f"Reasoning models: {len(reasoning_models)} found")
    for model_id in list(reasoning_models.keys())[:3]:
        print(f"  - {model_id}")
    
    # Test cost information
    claude_model = get_model_by_id("claude-sonnet-4-20250514")
    if claude_model:
        print(f"Claude Sonnet 4 cost: ${claude_model.cost_per_input_token}/1M input tokens")
    
    print(f"Total models in registry: {len(ALL_MODELS)}")
    print(f"Default routing: {DEFAULT_MODEL_ROUTING}")
    print()


async def test_caching_and_rate_limiting():
    """Test caching and rate limiting functionality."""
    print("=== Testing Caching and Rate Limiting ===")
    
    # Test cache
    cache = await get_cache()
    
    # Test cache miss
    result = await cache.get("test prompt", "gpt-4.1-mini")
    print(f"Cache miss result: {result}")
    
    # Test cache set and get
    await cache.set(
        prompt="test prompt",
        model_id="gpt-4.1-mini", 
        response_data={"content": "Test cached response", "cost": 0.001},
    )
    
    result = await cache.get("test prompt", "gpt-4.1-mini")
    print(f"Cache hit result: {result['content'] if result else 'None'}")
    
    # Test rate limiter
    rate_limiter = await get_rate_limiter()
    allowed, info = await rate_limiter.check_rate_limit(
        provider="test",
        model_id="test-model",
        estimated_cost=0.001,
    )
    print(f"Rate limit check: allowed={allowed}, info={info}")
    print()


async def test_agent_without_providers():
    """Test agent functionality without real LLM providers."""
    print("=== Testing Agent Without Providers ===")
    
    agent = BasicAIAgent("TestAgent", "research assistant")
    
    # Test context
    initial_context = agent.get_context_summary()
    print(f"Initial context: {initial_context}")
    
    # Test message processing (will use fallback since no providers)
    response = await agent.process_message("Hello, can you help with AI research?")
    print(f"Agent response: {response[:100]}...")
    
    # Test usage stats
    stats = agent.get_usage_stats()
    print(f"Usage stats: {stats}")
    
    # Test caching
    cached_response = await agent.process_message("Hello, can you help with AI research?", use_cache=True)
    print(f"Cached response available: {response != cached_response}")
    print()


async def test_model_recommendation():
    """Test model recommendation functionality."""
    print("=== Testing Model Recommendation ===")
    
    # Test capability-based filtering
    text_models = get_models_by_capability(ModelCapability.TEXT_GENERATION)
    print(f"Text generation models: {len(text_models)}")
    
    multimodal_models = get_models_by_capability(ModelCapability.MULTIMODAL)
    print(f"Multimodal models: {len(multimodal_models)}")
    
    # Show cost comparison for key models
    print("\nCost comparison (USD per 1M tokens):")
    key_models = ["gpt-4.1-mini", "gpt-4.1", "claude-sonnet-4-20250514", "o4-mini"]
    for model_id in key_models:
        model = get_model_by_id(model_id)
        if model and model.cost_per_input_token:
            print(f"  {model_id}: ${model.cost_per_input_token:.2f} input, ${model.cost_per_output_token:.2f} output")
    print()


async def main():
    """Run all tests."""
    print("Starting LLM Integration Manual Tests...\n")
    
    try:
        await test_model_registry()
        await test_caching_and_rate_limiting()
        await test_agent_without_providers()
        await test_model_recommendation()
        
        print("✅ All manual tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())