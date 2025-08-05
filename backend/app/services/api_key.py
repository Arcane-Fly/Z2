"""
API Key Management Service for Z2 platform.
Provides secure API key generation, validation, and usage tracking.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

import structlog
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import APIKey, APIKeyUsage
from app.models.user import User

logger = structlog.get_logger(__name__)


class APIKeyService:
    """Service for managing API keys and their usage."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_api_key(
        self,
        user_id: UUID,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        allowed_endpoints: Optional[List[str]] = None,
        rate_limit_per_hour: int = 1000,
        expires_in_days: Optional[int] = None,
    ) -> tuple[APIKey, str]:
        """Create a new API key and return the key and model."""
        
        # Generate secure API key
        api_key_string, key_hash = APIKey.generate_key()
        key_prefix = api_key_string[:10]  # Store first 10 chars for identification
        
        # Set expiration if specified
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key model
        api_key = APIKey(
            name=name,
            description=description,
            key_hash=key_hash,
            key_prefix=key_prefix,
            user_id=user_id,
            permissions=permissions or [],
            allowed_endpoints=allowed_endpoints or [],
            rate_limit_per_hour=rate_limit_per_hour,
            expires_at=expires_at,
        )
        
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        
        logger.info(
            "Created API key",
            api_key_id=str(api_key.id),
            user_id=str(user_id),
            name=name,
            permissions=permissions,
            expires_at=expires_at.isoformat() if expires_at else None,
        )
        
        return api_key, api_key_string

    async def validate_api_key(self, api_key_string: str) -> Optional[APIKey]:
        """Validate an API key and return the associated key model if valid."""
        if not api_key_string or not api_key_string.startswith("z2_"):
            return None
        
        # Hash the provided key
        key_hash = APIKey.hash_key(api_key_string)
        
        # Find the API key in database
        result = await self.db.execute(
            select(APIKey).where(
                and_(
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True,
                )
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key or not api_key.is_valid():
            return None
        
        # Update last used timestamp
        api_key.last_used_at = datetime.utcnow()
        api_key.usage_count += 1
        await self.db.commit()
        
        return api_key

    async def list_user_api_keys(self, user_id: UUID) -> List[APIKey]:
        """List all API keys for a user."""
        result = await self.db.execute(
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .order_by(desc(APIKey.created_at))
        )
        return list(result.scalars().all())

    async def get_api_key(self, api_key_id: UUID, user_id: UUID) -> Optional[APIKey]:
        """Get a specific API key belonging to a user."""
        result = await self.db.execute(
            select(APIKey).where(
                and_(
                    APIKey.id == api_key_id,
                    APIKey.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_api_key(
        self,
        api_key_id: UUID,
        user_id: UUID,
        **updates: Any,
    ) -> Optional[APIKey]:
        """Update an API key."""
        api_key = await self.get_api_key(api_key_id, user_id)
        if not api_key:
            return None

        for key, value in updates.items():
            if hasattr(api_key, key) and key not in ["id", "key_hash", "user_id", "created_at"]:
                setattr(api_key, key, value)

        api_key.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(api_key)

        logger.info("Updated API key", api_key_id=str(api_key_id), updates=updates)
        return api_key

    async def revoke_api_key(self, api_key_id: UUID, user_id: UUID) -> bool:
        """Revoke (deactivate) an API key."""
        api_key = await self.get_api_key(api_key_id, user_id)
        if not api_key:
            return False

        api_key.is_active = False
        api_key.updated_at = datetime.utcnow()
        await self.db.commit()

        logger.info("Revoked API key", api_key_id=str(api_key_id), user_id=str(user_id))
        return True

    async def record_api_key_usage(
        self,
        api_key: APIKey,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        request_size_bytes: Optional[int] = None,
        response_size_bytes: Optional[int] = None,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> APIKeyUsage:
        """Record API key usage for monitoring and rate limiting."""
        
        usage = APIKeyUsage(
            api_key_id=api_key.id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            user_agent=user_agent,
            ip_address=ip_address,
            request_size_bytes=request_size_bytes,
            response_size_bytes=response_size_bytes,
            error_type=error_type,
            error_message=error_message,
        )

        self.db.add(usage)
        await self.db.commit()
        await self.db.refresh(usage)

        logger.debug(
            "Recorded API key usage",
            api_key_id=str(api_key.id),
            endpoint=endpoint,
            status_code=status_code,
            response_time_ms=response_time_ms,
        )

        return usage

    async def check_rate_limit(
        self, api_key: APIKey, window_hours: int = 1
    ) -> Dict[str, Any]:
        """Check if API key is within rate limits."""
        if not api_key.rate_limit_per_hour:
            return {"allowed": True, "limit": None, "usage": 0, "remaining": None}

        # Count usage in the last window
        cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
        
        result = await self.db.execute(
            select(func.count(APIKeyUsage.id))
            .where(
                and_(
                    APIKeyUsage.api_key_id == api_key.id,
                    APIKeyUsage.created_at >= cutoff_time,
                )
            )
        )
        usage_count = result.scalar() or 0

        limit = api_key.rate_limit_per_hour * window_hours
        remaining = max(0, limit - usage_count)
        allowed = usage_count < limit

        return {
            "allowed": allowed,
            "limit": limit,
            "usage": usage_count,
            "remaining": remaining,
            "window_hours": window_hours,
            "reset_time": (datetime.utcnow() + timedelta(hours=window_hours)).isoformat(),
        }

    async def get_api_key_usage_stats(
        self,
        api_key_id: UUID,
        user_id: UUID,
        days_back: int = 7,
    ) -> Dict[str, Any]:
        """Get usage statistics for an API key."""
        
        # Verify ownership
        api_key = await self.get_api_key(api_key_id, user_id)
        if not api_key:
            return {}

        # Calculate time window
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)

        # Get aggregate statistics
        stats_query = select(
            func.count(APIKeyUsage.id).label("total_requests"),
            func.avg(APIKeyUsage.response_time_ms).label("avg_response_time"),
            func.sum(
                func.case((APIKeyUsage.status_code < 400, 1), else_=0)
            ).label("successful_requests"),
            func.sum(
                func.case((APIKeyUsage.status_code >= 400, 1), else_=0)
            ).label("failed_requests"),
            func.sum(APIKeyUsage.request_size_bytes).label("total_request_bytes"),
            func.sum(APIKeyUsage.response_size_bytes).label("total_response_bytes"),
        ).where(
            and_(
                APIKeyUsage.api_key_id == api_key_id,
                APIKeyUsage.created_at >= cutoff_time,
            )
        )

        result = await self.db.execute(stats_query)
        stats = result.first()

        # Get endpoint usage breakdown
        endpoint_query = select(
            APIKeyUsage.endpoint,
            func.count(APIKeyUsage.id).label("request_count"),
            func.avg(APIKeyUsage.response_time_ms).label("avg_response_time"),
        ).where(
            and_(
                APIKeyUsage.api_key_id == api_key_id,
                APIKeyUsage.created_at >= cutoff_time,
            )
        ).group_by(
            APIKeyUsage.endpoint
        ).order_by(
            desc("request_count")
        ).limit(10)

        endpoint_result = await self.db.execute(endpoint_query)
        endpoint_stats = [
            {
                "endpoint": row.endpoint,
                "request_count": row.request_count,
                "avg_response_time_ms": float(row.avg_response_time) if row.avg_response_time else 0,
            }
            for row in endpoint_result
        ]

        # Calculate success rate
        total_requests = stats.total_requests if stats.total_requests else 0
        successful_requests = stats.successful_requests if stats.successful_requests else 0
        success_rate = (successful_requests / total_requests) if total_requests > 0 else 0

        return {
            "api_key_id": str(api_key_id),
            "period_days": days_back,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": stats.failed_requests if stats.failed_requests else 0,
            "success_rate": success_rate,
            "avg_response_time_ms": float(stats.avg_response_time) if stats.avg_response_time else 0,
            "total_request_bytes": stats.total_request_bytes if stats.total_request_bytes else 0,
            "total_response_bytes": stats.total_response_bytes if stats.total_response_bytes else 0,
            "endpoint_breakdown": endpoint_stats,
            "rate_limit_info": await self.check_rate_limit(api_key),
        }

    async def cleanup_expired_keys(self) -> int:
        """Clean up expired API keys by deactivating them."""
        
        # Find expired keys that are still active
        result = await self.db.execute(
            select(APIKey).where(
                and_(
                    APIKey.is_active == True,
                    APIKey.expires_at < datetime.utcnow(),
                )
            )
        )
        expired_keys = list(result.scalars().all())

        # Deactivate expired keys
        count = 0
        for key in expired_keys:
            key.is_active = False
            key.updated_at = datetime.utcnow()
            count += 1

        if count > 0:
            await self.db.commit()
            logger.info("Deactivated expired API keys", count=count)

        return count