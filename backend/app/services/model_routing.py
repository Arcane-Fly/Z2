"""
Model Routing Service for persistent storage and management of routing policies.
Implements agent-os specifications for model routing and usage tracking.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_routing import ModelRoutingPolicy, ModelUsageTracking

logger = structlog.get_logger(__name__)


class ModelRoutingService:
    """Service for managing model routing policies and usage tracking."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_routing_policy(
        self,
        name: str,
        task_type: str,
        model_id: str,
        description: str | None = None,
        fallback_models: list[str] | None = None,
        max_cost_per_request: float | None = None,
        max_latency_ms: int | None = None,
        required_capabilities: list[str] | None = None,
        priority: int = 100,
        created_by: str | None = None,
    ) -> ModelRoutingPolicy:
        """Create a new routing policy."""
        policy = ModelRoutingPolicy(
            name=name,
            description=description,
            task_type=task_type,
            model_id=model_id,
            fallback_models=fallback_models or [],
            max_cost_per_request=max_cost_per_request,
            max_latency_ms=max_latency_ms,
            required_capabilities=required_capabilities or [],
            priority=priority,
            created_by=created_by,
        )

        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)

        logger.info(
            "Created routing policy",
            policy_id=str(policy.id),
            task_type=task_type,
            model_id=model_id,
        )

        return policy

    async def get_routing_policy(self, policy_id: UUID) -> ModelRoutingPolicy | None:
        """Get a routing policy by ID."""
        result = await self.db.execute(
            select(ModelRoutingPolicy).where(ModelRoutingPolicy.id == policy_id)
        )
        return result.scalar_one_or_none()

    async def get_routing_policy_for_task(
        self, task_type: str
    ) -> ModelRoutingPolicy | None:
        """Get the highest priority active routing policy for a task type."""
        result = await self.db.execute(
            select(ModelRoutingPolicy)
            .where(
                and_(
                    ModelRoutingPolicy.task_type == task_type,
                    ModelRoutingPolicy.is_active is True,
                )
            )
            .order_by(ModelRoutingPolicy.priority.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_routing_policies(
        self, active_only: bool = True
    ) -> list[ModelRoutingPolicy]:
        """List all routing policies."""
        query = select(ModelRoutingPolicy)
        if active_only:
            query = query.where(ModelRoutingPolicy.is_active is True)

        query = query.order_by(ModelRoutingPolicy.priority.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_routing_policy(
        self,
        policy_id: UUID,
        **updates: Any,
    ) -> ModelRoutingPolicy | None:
        """Update a routing policy."""
        policy = await self.get_routing_policy(policy_id)
        if not policy:
            return None

        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)

        policy.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(policy)

        logger.info("Updated routing policy", policy_id=str(policy_id), updates=updates)
        return policy

    async def delete_routing_policy(self, policy_id: UUID) -> bool:
        """Delete (deactivate) a routing policy."""
        policy = await self.get_routing_policy(policy_id)
        if not policy:
            return False

        policy.is_active = False
        policy.updated_at = datetime.utcnow()
        await self.db.commit()

        logger.info("Deactivated routing policy", policy_id=str(policy_id))
        return True

    async def track_model_usage(
        self,
        model_id: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: int,
        task_type: str | None = None,
        user_id: str | None = None,
        was_cached: bool = False,
        success: bool = True,
        error_type: str | None = None,
        request_metadata: dict[str, Any] | None = None,
    ) -> ModelUsageTracking:
        """Track model usage for analytics and cost monitoring."""
        usage = ModelUsageTracking(
            model_id=model_id,
            provider=provider,
            task_type=task_type,
            user_id=user_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            was_cached=was_cached,
            success=success,
            error_type=error_type,
            request_metadata=request_metadata or {},
        )

        self.db.add(usage)
        await self.db.commit()
        await self.db.refresh(usage)

        logger.debug(
            "Tracked model usage",
            model_id=model_id,
            provider=provider,
            tokens=input_tokens + output_tokens,
            cost_usd=cost_usd,
        )

        return usage

    async def get_usage_statistics(
        self,
        provider: str | None = None,
        model_id: str | None = None,
        task_type: str | None = None,
        user_id: str | None = None,
        hours_back: int = 24,
    ) -> dict[str, Any]:
        """Get comprehensive usage statistics."""
        # Build the base query
        base_query = select(ModelUsageTracking).where(
            ModelUsageTracking.created_at >= datetime.utcnow() - timedelta(hours=hours_back)
        )

        # Apply filters
        if provider:
            base_query = base_query.where(ModelUsageTracking.provider == provider)
        if model_id:
            base_query = base_query.where(ModelUsageTracking.model_id == model_id)
        if task_type:
            base_query = base_query.where(ModelUsageTracking.task_type == task_type)
        if user_id:
            base_query = base_query.where(ModelUsageTracking.user_id == user_id)

        # Get aggregate statistics
        stats_query = select(
            func.count(ModelUsageTracking.id).label("total_requests"),
            func.sum(ModelUsageTracking.cost_usd).label("total_cost"),
            func.sum(ModelUsageTracking.total_tokens).label("total_tokens"),
            func.avg(ModelUsageTracking.latency_ms).label("avg_latency"),
            func.sum(
                func.case((ModelUsageTracking.was_cached is True, 1), else_=0)
            ).label("cache_hits"),
            func.sum(
                func.case((ModelUsageTracking.success is True, 1), else_=0)
            ).label("successful_requests"),
        ).where(
            ModelUsageTracking.created_at >= datetime.utcnow() - timedelta(hours=hours_back)
        )

        # Apply same filters to stats query
        if provider:
            stats_query = stats_query.where(ModelUsageTracking.provider == provider)
        if model_id:
            stats_query = stats_query.where(ModelUsageTracking.model_id == model_id)
        if task_type:
            stats_query = stats_query.where(ModelUsageTracking.task_type == task_type)
        if user_id:
            stats_query = stats_query.where(ModelUsageTracking.user_id == user_id)

        result = await self.db.execute(stats_query)
        stats = result.first()

        # Get cost breakdown by model
        cost_by_model_query = (
            select(
                ModelUsageTracking.model_id,
                func.sum(ModelUsageTracking.cost_usd).label("total_cost"),
                func.count(ModelUsageTracking.id).label("request_count"),
            )
            .where(
                ModelUsageTracking.created_at >= datetime.utcnow() - timedelta(hours=hours_back)
            )
            .group_by(ModelUsageTracking.model_id)
            .order_by(desc("total_cost"))
        )

        # Apply same filters
        if provider:
            cost_by_model_query = cost_by_model_query.where(
                ModelUsageTracking.provider == provider
            )
        if model_id:
            cost_by_model_query = cost_by_model_query.where(
                ModelUsageTracking.model_id == model_id
            )
        if task_type:
            cost_by_model_query = cost_by_model_query.where(
                ModelUsageTracking.task_type == task_type
            )
        if user_id:
            cost_by_model_query = cost_by_model_query.where(
                ModelUsageTracking.user_id == user_id
            )

        cost_result = await self.db.execute(cost_by_model_query)
        cost_by_model = {
            row.model_id: {
                "total_cost": float(row.total_cost) if row.total_cost else 0.0,
                "request_count": row.request_count,
            }
            for row in cost_result
        }

        # Calculate cache hit rate
        total_requests = stats.total_requests if stats.total_requests else 0
        cache_hits = stats.cache_hits if stats.cache_hits else 0
        cache_hit_rate = (cache_hits / total_requests) if total_requests > 0 else 0.0

        # Calculate success rate
        successful_requests = stats.successful_requests if stats.successful_requests else 0
        success_rate = (successful_requests / total_requests) if total_requests > 0 else 0.0

        return {
            "total_requests": total_requests,
            "total_cost_usd": float(stats.total_cost) if stats.total_cost else 0.0,
            "total_tokens": stats.total_tokens if stats.total_tokens else 0,
            "average_latency_ms": float(stats.avg_latency) if stats.avg_latency else 0.0,
            "cache_hit_rate": cache_hit_rate,
            "success_rate": success_rate,
            "cost_by_model": cost_by_model,
            "filters": {
                "provider": provider,
                "model_id": model_id,
                "task_type": task_type,
                "user_id": user_id,
                "hours_back": hours_back,
            },
        }

    async def get_cost_optimization_recommendations(
        self, hours_back: int = 168  # 1 week
    ) -> dict[str, Any]:
        """Get recommendations for cost optimization based on usage patterns."""
        # Get usage data for analysis
        usage_stats = await self.get_usage_statistics(hours_back=hours_back)

        recommendations = []

        # Analyze cost by model
        cost_by_model = usage_stats.get("cost_by_model", {})
        total_cost = usage_stats.get("total_cost_usd", 0.0)

        if total_cost > 0:
            # Find expensive models
            expensive_threshold = total_cost * 0.3  # Models that cost >30% of total
            for model_id, data in cost_by_model.items():
                if data["total_cost"] > expensive_threshold:
                    recommendations.append({
                        "type": "cost_optimization",
                        "priority": "high",
                        "model_id": model_id,
                        "message": f"Model {model_id} accounts for ${data['total_cost']:.2f} ({data['total_cost']/total_cost*100:.1f}%) of total costs",
                        "suggestion": "Consider using a more cost-effective alternative for non-critical tasks",
                    })

        # Check cache hit rate
        cache_hit_rate = usage_stats.get("cache_hit_rate", 0.0)
        if cache_hit_rate < 0.3:  # Less than 30% cache hit rate
            recommendations.append({
                "type": "caching",
                "priority": "medium",
                "message": f"Cache hit rate is {cache_hit_rate*100:.1f}%",
                "suggestion": "Consider implementing better caching strategies to reduce costs and latency",
            })

        # Check success rate
        success_rate = usage_stats.get("success_rate", 0.0)
        if success_rate < 0.95:  # Less than 95% success rate
            recommendations.append({
                "type": "reliability",
                "priority": "high",
                "message": f"Success rate is {success_rate*100:.1f}%",
                "suggestion": "Investigate and fix reliability issues to improve system performance",
            })

        return {
            "recommendations": recommendations,
            "analysis_period_hours": hours_back,
            "total_cost_analyzed": total_cost,
            "total_requests_analyzed": usage_stats.get("total_requests", 0),
        }
