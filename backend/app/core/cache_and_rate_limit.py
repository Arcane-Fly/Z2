"""
Caching and Rate Limiting Module for LLM Integration.

This module provides caching and rate limiting functionality to optimize
cost and latency for LLM API calls.
"""

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Optional

import structlog
from redis.asyncio import Redis

from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class CacheConfig:
    """Configuration for response caching."""

    ttl_seconds: int = 3600  # Default 1 hour cache
    max_cache_size: int = 10000  # Maximum cached items
    enable_compression: bool = True


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    cost_limit_per_hour: float = 100.0  # USD
    burst_allowance: int = 10


class LLMResponseCache:
    """Redis-based cache for LLM responses to reduce API calls and costs."""

    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis = redis_client
        self.local_cache: dict[str, Any] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    async def _init_redis(self) -> None:
        """Initialize Redis connection if not provided."""
        if self.redis is None:
            try:
                self.redis = Redis.from_url(settings.redis_url)
                await self.redis.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning("Redis connection failed, using local cache", error=str(e))
                self.redis = None

    def _generate_cache_key(
        self,
        prompt: str,
        model_id: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate a deterministic cache key for the request."""
        key_data = f"{prompt}:{model_id}:{temperature}:{max_tokens}"
        return f"llm_cache:{hashlib.sha256(key_data.encode()).hexdigest()[:16]}"

    async def get(
        self,
        prompt: str,
        model_id: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Optional[dict[str, Any]]:
        """Get cached response if available."""
        cache_key = self._generate_cache_key(prompt, model_id, temperature, max_tokens)

        try:
            # Try Redis first
            if self.redis is None:
                await self._init_redis()

            if self.redis:
                cached_data = await self.redis.get(cache_key)
                if cached_data:
                    self.cache_hits += 1
                    logger.debug("Cache hit", key=cache_key[:8])
                    import json
                    return json.loads(cached_data)

            # Fall back to local cache
            if cache_key in self.local_cache:
                cached_item = self.local_cache[cache_key]
                if cached_item["expires_at"] > time.time():
                    self.cache_hits += 1
                    logger.debug("Local cache hit", key=cache_key[:8])
                    return cached_item["data"]
                else:
                    # Remove expired item
                    del self.local_cache[cache_key]

        except Exception as e:
            logger.warning("Cache retrieval error", error=str(e))

        self.cache_misses += 1
        return None

    async def set(
        self,
        prompt: str,
        model_id: str,
        response_data: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        ttl_seconds: int = 3600,
    ) -> None:
        """Cache a response."""
        cache_key = self._generate_cache_key(prompt, model_id, temperature, max_tokens)

        try:
            # Store in Redis if available
            if self.redis:
                import json
                await self.redis.setex(
                    cache_key,
                    ttl_seconds,
                    json.dumps(response_data, default=str)
                )
                logger.debug("Cached in Redis", key=cache_key[:8])

            # Also store in local cache as backup
            self.local_cache[cache_key] = {
                "data": response_data,
                "expires_at": time.time() + ttl_seconds,
            }

            # Clean up local cache if it gets too large
            if len(self.local_cache) > 1000:
                # Remove oldest 20% of items
                sorted_items = sorted(
                    self.local_cache.items(),
                    key=lambda x: x[1]["expires_at"]
                )
                items_to_remove = sorted_items[:200]
                for key, _ in items_to_remove:
                    del self.local_cache[key]

        except Exception as e:
            logger.warning("Cache storage error", error=str(e))

    def get_stats(self) -> dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (
            self.cache_hits / total_requests if total_requests > 0 else 0.0
        )

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "local_cache_size": len(self.local_cache),
        }


class RateLimiter:
    """Rate limiter for LLM API calls to prevent hitting provider limits."""

    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis = redis_client
        self.local_state: dict[str, dict] = {}

    async def _init_redis(self) -> None:
        """Initialize Redis connection if not provided."""
        if self.redis is None:
            try:
                self.redis = Redis.from_url(settings.redis_url)
                await self.redis.ping()
                logger.info("Redis rate limiter initialized successfully")
            except Exception as e:
                logger.warning("Redis connection failed, using local rate limiting", error=str(e))
                self.redis = None

    async def check_rate_limit(
        self,
        provider: str,
        model_id: str,
        estimated_cost: float = 0.0,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check if request is within rate limits.
        
        Returns:
            tuple: (is_allowed, rate_limit_info)
        """
        current_time = time.time()
        minute_window = int(current_time // 60)
        hour_window = int(current_time // 3600)
        
        key_base = f"rate_limit:{provider}:{model_id}"
        minute_key = f"{key_base}:minute:{minute_window}"
        hour_key = f"{key_base}:hour:{hour_window}"
        cost_key = f"{key_base}:cost:{hour_window}"

        try:
            if self.redis is None:
                await self._init_redis()

            if self.redis:
                # Use Redis for distributed rate limiting
                pipe = self.redis.pipeline()
                pipe.incr(minute_key)
                pipe.expire(minute_key, 60)
                pipe.incr(hour_key)
                pipe.expire(hour_key, 3600)
                pipe.incrbyfloat(cost_key, estimated_cost)
                pipe.expire(cost_key, 3600)
                
                results = await pipe.execute()
                minute_count = results[0]
                hour_count = results[2]
                hour_cost = results[4]
            else:
                # Fall back to local rate limiting
                if provider not in self.local_state:
                    self.local_state[provider] = {}
                
                provider_state = self.local_state[provider]
                
                # Clean old windows
                provider_state = {
                    k: v for k, v in provider_state.items()
                    if v.get("window", 0) >= current_time - 3600
                }
                
                minute_count = len([
                    v for v in provider_state.values()
                    if v.get("window", 0) >= current_time - 60
                ])
                hour_count = len(provider_state)
                hour_cost = sum([
                    v.get("cost", 0) for v in provider_state.values()
                    if v.get("window", 0) >= current_time - 3600
                ])

            # Check limits
            config = RateLimitConfig()  # Use default config for now
            
            rate_limit_info = {
                "minute_count": minute_count,
                "hour_count": hour_count,
                "hour_cost": hour_cost,
                "limits": {
                    "requests_per_minute": config.requests_per_minute,
                    "requests_per_hour": config.requests_per_hour,
                    "cost_limit_per_hour": config.cost_limit_per_hour,
                }
            }

            # Check if limits exceeded
            if minute_count > config.requests_per_minute:
                logger.warning("Rate limit exceeded (per minute)", 
                             provider=provider, 
                             count=minute_count,
                             limit=config.requests_per_minute)
                return False, rate_limit_info

            if hour_count > config.requests_per_hour:
                logger.warning("Rate limit exceeded (per hour)", 
                             provider=provider, 
                             count=hour_count,
                             limit=config.requests_per_hour)
                return False, rate_limit_info

            if hour_cost > config.cost_limit_per_hour:
                logger.warning("Cost limit exceeded", 
                             provider=provider, 
                             cost=hour_cost,
                             limit=config.cost_limit_per_hour)
                return False, rate_limit_info

            # Record the request in local state if using local tracking
            if not self.redis:
                request_id = f"{provider}:{model_id}:{current_time}"
                self.local_state[provider][request_id] = {
                    "window": current_time,
                    "cost": estimated_cost,
                }

            return True, rate_limit_info

        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            # Fail open - allow request if rate limiting fails
            return True, {"error": str(e)}

    async def record_usage(
        self,
        provider: str,
        model_id: str,
        actual_cost: float,
        tokens_used: int,
    ) -> None:
        """Record actual usage for tracking and analytics."""
        try:
            current_time = time.time()
            hour_window = int(current_time // 3600)
            
            usage_key = f"usage:{provider}:{model_id}:{hour_window}"
            
            if self.redis:
                pipe = self.redis.pipeline()
                pipe.hincrbyfloat(usage_key, "cost", actual_cost)
                pipe.hincrby(usage_key, "tokens", tokens_used)
                pipe.hincrby(usage_key, "requests", 1)
                pipe.expire(usage_key, 86400)  # Keep for 24 hours
                await pipe.execute()
            
            logger.debug("Usage recorded", 
                        provider=provider, 
                        model=model_id,
                        cost=actual_cost, 
                        tokens=tokens_used)

        except Exception as e:
            logger.warning("Failed to record usage", error=str(e))


# Global instances
_cache = None
_rate_limiter = None


async def get_cache() -> LLMResponseCache:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        _cache = LLMResponseCache()
    return _cache


async def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter