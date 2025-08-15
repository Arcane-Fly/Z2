"""
Model Integration Layer endpoints for Z2 API.
"""

from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_dependencies import get_current_active_user
from app.core.models_registry import (
    ALL_MODELS,
    DEFAULT_MODEL_ROUTING,
    MODEL_REGISTRY_VERSION,
    ModelCapability,
    ProviderType,
    get_model_by_id,
    get_models_by_capability,
    get_models_by_provider,
    validate_model_support,
)
from app.database.session import get_db
from app.models.user import User
from app.services.model_routing import ModelRoutingService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/")
async def list_available_models(
    provider: str | None = None,
    capability: str | None = None,
    reasoning_only: bool = False,
    multimodal_only: bool = False,
    max_cost: float | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all available LLM models across providers with filtering options."""
    models = ALL_MODELS.copy()

    # Apply filters
    if provider:
        try:
            provider_enum = ProviderType(provider.lower())
            models = get_models_by_provider(provider_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    if capability:
        try:
            capability_enum = ModelCapability(capability.lower())
            models = get_models_by_capability(capability_enum)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid capability: {capability}"
            )

    if reasoning_only:
        models = {k: v for k, v in models.items() if v.is_reasoning_model}

    if multimodal_only:
        models = {k: v for k, v in models.items() if v.is_multimodal}

    if max_cost is not None:
        models = {
            k: v
            for k, v in models.items()
            if v.cost_per_input_token is None or v.cost_per_input_token <= max_cost
        }

    # Convert to response format
    response_models = []
    for model_id, spec in models.items():
        response_models.append(
            {
                "model_id": model_id,
                "provider": spec.provider.value,
                "name": spec.name,
                "description": spec.description,
                "capabilities": [cap.value for cap in spec.capabilities],
                "input_token_limit": spec.input_token_limit,
                "output_token_limit": spec.output_token_limit,
                "supports_streaming": spec.supports_streaming,
                "cost_per_input_token": spec.cost_per_input_token,
                "cost_per_output_token": spec.cost_per_output_token,
                "is_reasoning_model": spec.is_reasoning_model,
                "is_multimodal": spec.is_multimodal,
                "knowledge_cutoff": spec.knowledge_cutoff,
                "model_card_url": spec.model_card_url,
            }
        )

    return {
        "models": response_models,
        "total_count": len(response_models),
        "registry_version": MODEL_REGISTRY_VERSION,
        "filters_applied": {
            "provider": provider,
            "capability": capability,
            "reasoning_only": reasoning_only,
            "multimodal_only": multimodal_only,
            "max_cost": max_cost,
        },
    }


@router.get("/providers")
async def list_providers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all configured LLM providers and their status."""
    from app.agents.mil import ModelIntegrationLayer

    providers_info = {}

    # Try to get real provider status from MIL
    try:
        mil = ModelIntegrationLayer()
        provider_status = mil.get_provider_status()
    except Exception as e:
        logger.warning("Could not get MIL provider status", error=str(e))
        provider_status = {}

    for provider in ProviderType:
        provider_models = get_models_by_provider(provider)

        # Get real status from MIL if available
        status = "unknown"
        if provider.value in provider_status:
            status = provider_status[provider.value].get("status", "unknown")
        elif provider_models:  # If we have models defined, assume configured
            status = "configured"

        providers_info[provider.value] = {
            "name": provider.value.title(),
            "model_count": len(provider_models),
            "available_models": list(provider_models.keys()),
            "capabilities": list(
                set().union(*[model.capabilities for model in provider_models.values()])
            ),
            "status": status,
        }

    return {
        "providers": providers_info,
        "total_providers": len(providers_info),
        "registry_version": MODEL_REGISTRY_VERSION,
    }


@router.get("/{model_id}")
async def get_model_info(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get detailed information about a specific model."""
    spec = get_model_by_id(model_id)

    if not spec:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

    return {
        "model_id": model_id,
        "provider": spec.provider.value,
        "name": spec.name,
        "description": spec.description,
        "capabilities": [cap.value for cap in spec.capabilities],
        "input_token_limit": spec.input_token_limit,
        "output_token_limit": spec.output_token_limit,
        "supports_streaming": spec.supports_streaming,
        "supports_system_message": spec.supports_system_message,
        "cost_per_input_token": spec.cost_per_input_token,
        "cost_per_output_token": spec.cost_per_output_token,
        "context_window": spec.context_window,
        "is_reasoning_model": spec.is_reasoning_model,
        "is_multimodal": spec.is_multimodal,
        "knowledge_cutoff": spec.knowledge_cutoff,
        "model_card_url": spec.model_card_url,
    }


@router.post("/validate")
async def validate_model_configuration(
    model_id: str,
    required_capabilities: list[str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Validate that a model supports all required capabilities."""
    try:
        capabilities = [ModelCapability(cap.lower()) for cap in required_capabilities]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid capability: {e}")

    is_valid = validate_model_support(model_id, capabilities)

    if not is_valid:
        spec = get_model_by_id(model_id)
        if not spec:
            raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

        missing_capabilities = [
            cap.value for cap in capabilities if cap not in spec.capabilities
        ]

        return {
            "valid": False,
            "model_id": model_id,
            "missing_capabilities": missing_capabilities,
            "available_capabilities": [cap.value for cap in spec.capabilities],
        }

    return {
        "valid": True,
        "model_id": model_id,
        "supported_capabilities": required_capabilities,
    }


@router.get("/routing/policy")
async def get_routing_policy(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current model routing policy configuration."""
    routing_service = ModelRoutingService(db)
    policies = await routing_service.list_routing_policies(active_only=True)

    # Convert to the expected format
    routing_config = {}
    for policy in policies:
        routing_config[policy.task_type] = policy.model_id

    # Merge with defaults for any missing task types
    merged_routing = {**DEFAULT_MODEL_ROUTING, **routing_config}

    return {
        "routing_policy": merged_routing,
        "active_policies": [
            {
                "id": str(policy.id),
                "name": policy.name,
                "task_type": policy.task_type,
                "model_id": policy.model_id,
                "fallback_models": policy.fallback_models,
                "priority": policy.priority,
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat(),
            }
            for policy in policies
        ],
        "description": "Current model routing configuration with persistent policies",
        "registry_version": MODEL_REGISTRY_VERSION,
    }


@router.put("/routing/policy")
async def update_routing_policy(
    new_routing: dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update model routing policy configuration."""
    routing_service = ModelRoutingService(db)

    # Validate that all specified models exist
    for task_type, model_id in new_routing.items():
        if not get_model_by_id(model_id):
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model_id}' not found for task type '{task_type}'",
            )

    # Update or create routing policies
    updated_policies = []
    for task_type, model_id in new_routing.items():
        # Check if policy exists for this task type
        existing_policy = await routing_service.get_routing_policy_for_task(task_type)

        if existing_policy:
            # Update existing policy
            updated_policy = await routing_service.update_routing_policy(
                existing_policy.id,
                model_id=model_id,
                updated_at=datetime.utcnow(),
            )
            updated_policies.append(updated_policy)
        else:
            # Create new policy
            policy = await routing_service.create_routing_policy(
                name=f"Auto-generated policy for {task_type}",
                task_type=task_type,
                model_id=model_id,
                description=f"Automatically created routing policy for {task_type} tasks",
                created_by=current_user.username,
            )
            updated_policies.append(policy)

    return {
        "message": "Routing policy updated successfully",
        "new_routing": new_routing,
        "updated_policies": [
            {
                "id": str(policy.id),
                "task_type": policy.task_type,
                "model_id": policy.model_id,
            }
            for policy in updated_policies
        ],
        "registry_version": MODEL_REGISTRY_VERSION,
    }


@router.post("/estimate-cost")
async def estimate_request_cost(
    prompt: str,
    model_id: str,
    max_tokens: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Estimate cost for a potential LLM request."""
    spec = get_model_by_id(model_id)

    if not spec:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

    if spec.cost_per_input_token is None:
        raise HTTPException(
            status_code=400,
            detail=f"Cost information not available for model '{model_id}'"
        )

    # Estimate input tokens (rough approximation: 1 token ≈ 4 characters)
    estimated_input_tokens = len(prompt) // 4
    estimated_output_tokens = max_tokens or 150

    # Calculate costs
    input_cost = (estimated_input_tokens / 1_000_000) * spec.cost_per_input_token
    output_cost = (estimated_output_tokens / 1_000_000) * spec.cost_per_output_token
    total_cost = input_cost + output_cost

    return {
        "model_id": model_id,
        "estimated_input_tokens": estimated_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "estimated_total_tokens": estimated_input_tokens + estimated_output_tokens,
        "cost_breakdown": {
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
        },
        "cost_per_million_tokens": {
            "input": spec.cost_per_input_token,
            "output": spec.cost_per_output_token,
        },
    }


@router.get("/usage/stats")
async def get_usage_statistics(
    provider: str | None = None,
    model_id: str | None = None,
    hours_back: int = 24,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get usage statistics and cost tracking."""
    routing_service = ModelRoutingService(db)

    try:
        stats = await routing_service.get_usage_statistics(
            provider=provider,
            model_id=model_id,
            hours_back=hours_back,
        )

        # Add registry version and additional metadata
        stats["registry_version"] = MODEL_REGISTRY_VERSION
        stats["data_source"] = "persistent_database"

        return stats

    except Exception as e:
        logger.error("Failed to get usage statistics", error=str(e))

        # Fallback to mock response if there's an error
        return {
            "message": "Usage statistics - using fallback data due to error",
            "error": str(e),
            "filters": {
                "provider": provider,
                "model_id": model_id,
                "hours_back": hours_back,
            },
            "fallback_structure": {
                "total_requests": 0,
                "total_cost_usd": 0.0,
                "total_tokens": 0,
                "average_latency_ms": 0.0,
                "cost_by_model": {},
                "cache_hit_rate": 0.0,
                "success_rate": 0.0,
            },
            "registry_version": MODEL_REGISTRY_VERSION,
        }


@router.post("/recommend")
async def recommend_optimal_model(
    task_type: str,
    required_capabilities: list[str],
    max_cost: float | None = None,
    prefer_speed: bool = False,
    prefer_accuracy: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get optimal model recommendation for a given task."""
    try:
        capabilities = [ModelCapability(cap.lower()) for cap in required_capabilities]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid capability: {e}")

    # Get models that support all required capabilities
    suitable_models = {}
    for model_id, spec in ALL_MODELS.items():
        if all(cap in spec.capabilities for cap in capabilities):
            if max_cost is None or (
                spec.cost_per_input_token is not None
                and spec.cost_per_input_token <= max_cost
            ):
                suitable_models[model_id] = spec

    if not suitable_models:
        return {
            "recommended_model": None,
            "reason": "No models found that meet the requirements",
            "suggestions": [
                "Consider relaxing cost constraints",
                "Check if all required capabilities are necessary",
            ],
        }

    # Simple recommendation logic (can be enhanced)
    if task_type in DEFAULT_MODEL_ROUTING:
        default_model = DEFAULT_MODEL_ROUTING[task_type]
        if default_model in suitable_models:
            recommended = default_model
        else:
            # Fallback to first suitable model
            recommended = next(iter(suitable_models))
    else:
        recommended = next(iter(suitable_models))

    return {
        "recommended_model": recommended,
        "model_info": {
            "name": suitable_models[recommended].name,
            "provider": suitable_models[recommended].provider.value,
            "cost_per_input_token": suitable_models[recommended].cost_per_input_token,
            "capabilities": [
                cap.value for cap in suitable_models[recommended].capabilities
            ],
        },
        "alternatives": [
            {
                "model_id": model_id,
                "name": spec.name,
                "provider": spec.provider.value,
                "cost_per_input_token": spec.cost_per_input_token,
            }
            for model_id, spec in list(suitable_models.items())[:5]
            if model_id != recommended
        ],
        "task_type": task_type,
        "required_capabilities": required_capabilities,
    }


@router.post("/routing/policy")
async def create_routing_policy(
    name: str,
    task_type: str,
    model_id: str,
    description: str | None = None,
    fallback_models: list[str] | None = None,
    max_cost_per_request: float | None = None,
    max_latency_ms: int | None = None,
    required_capabilities: list[str] | None = None,
    priority: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new routing policy."""
    routing_service = ModelRoutingService(db)

    # Validate model exists
    if not get_model_by_id(model_id):
        raise HTTPException(status_code=400, detail=f"Model '{model_id}' not found")

    # Validate fallback models if provided
    if fallback_models:
        for fallback_model in fallback_models:
            if not get_model_by_id(fallback_model):
                raise HTTPException(
                    status_code=400,
                    detail=f"Fallback model '{fallback_model}' not found"
                )

    policy = await routing_service.create_routing_policy(
        name=name,
        task_type=task_type,
        model_id=model_id,
        description=description,
        fallback_models=fallback_models,
        max_cost_per_request=max_cost_per_request,
        max_latency_ms=max_latency_ms,
        required_capabilities=required_capabilities,
        priority=priority,
        created_by=current_user.username,
    )

    return {
        "id": str(policy.id),
        "name": policy.name,
        "task_type": policy.task_type,
        "model_id": policy.model_id,
        "fallback_models": policy.fallback_models,
        "priority": policy.priority,
        "created_at": policy.created_at.isoformat(),
        "message": "Routing policy created successfully",
    }


@router.get("/optimization/recommendations")
async def get_cost_optimization_recommendations(
    hours_back: int = 168,  # 1 week default
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get cost optimization recommendations based on usage patterns."""
    routing_service = ModelRoutingService(db)

    try:
        recommendations = await routing_service.get_cost_optimization_recommendations(
            hours_back=hours_back
        )

        recommendations["registry_version"] = MODEL_REGISTRY_VERSION
        recommendations["generated_at"] = datetime.utcnow().isoformat()

        return recommendations

    except Exception as e:
        logger.error("Failed to generate optimization recommendations", error=str(e))

        return {
            "message": "Cost optimization recommendations - analysis failed",
            "error": str(e),
            "recommendations": [],
            "analysis_period_hours": hours_back,
            "total_cost_analyzed": 0.0,
            "total_requests_analyzed": 0,
            "registry_version": MODEL_REGISTRY_VERSION,
        }
