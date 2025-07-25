"""
Model Integration Layer endpoints for Z2 API.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

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

router = APIRouter()


@router.get("/")
async def list_available_models(
    provider: Optional[str] = None,
    capability: Optional[str] = None,
    reasoning_only: bool = False,
    multimodal_only: bool = False,
    max_cost: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
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
):
    """List all configured LLM providers and their status."""
    providers_info = {}

    for provider in ProviderType:
        provider_models = get_models_by_provider(provider)
        providers_info[provider.value] = {
            "name": provider.value.title(),
            "model_count": len(provider_models),
            "available_models": list(provider_models.keys()),
            "capabilities": list(
                set().union(*[model.capabilities for model in provider_models.values()])
            ),
            "status": "available",  # TODO: Add actual health check
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
):
    """Get current model routing policy configuration."""
    return {
        "routing_policy": DEFAULT_MODEL_ROUTING,
        "description": "Default model routing configuration for automatic model selection",
        "registry_version": MODEL_REGISTRY_VERSION,
    }


@router.put("/routing/policy")
async def update_routing_policy(
    new_routing: dict[str, str],
    db: AsyncSession = Depends(get_db),
):
    """Update model routing policy configuration."""
    # Validate that all specified models exist
    for task_type, model_id in new_routing.items():
        if not get_model_by_id(model_id):
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model_id}' not found for task type '{task_type}'",
            )

    # TODO: Implement persistent routing policy storage
    return {
        "message": "Routing policy updated successfully",
        "new_routing": new_routing,
        "registry_version": MODEL_REGISTRY_VERSION,
    }


@router.get("/metrics")
async def get_model_metrics(
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get model usage metrics and performance statistics."""
    # TODO: Implement actual metrics collection
    return {
        "message": "Model metrics endpoint - Implementation pending",
        "filters": {
            "model_id": model_id,
            "provider": provider,
        },
        "registry_version": MODEL_REGISTRY_VERSION,
    }


@router.post("/recommend")
async def recommend_optimal_model(
    task_type: str,
    required_capabilities: list[str],
    max_cost: Optional[float] = None,
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
