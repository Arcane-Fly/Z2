"""
Agent management endpoints for Z2 API.
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_dependencies import (
    get_current_active_user,
)
from app.database.session import get_db
from app.models.agent import Agent
from app.models.user import User
from app.schemas import (
    AgentCreate,
    AgentExecutionRequest,
    AgentExecutionResponse,
    AgentResponse,
    AgentUpdate,
    BaseResponse,
    PaginatedResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_agents(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by name or description"),
    role: str | None = Query(None, description="Filter by agent role"),
    status: str | None = Query(None, description="Filter by agent status"),
    created_by: UUID | None = Query(None, description="Filter by creator"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all agents with filtering and pagination."""

    # Build query
    query = select(Agent)

    # Apply filters
    conditions = []
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                Agent.name.ilike(search_pattern),
                Agent.description.ilike(search_pattern)
            )
        )

    if role:
        conditions.append(Agent.role == role)

    if status:
        conditions.append(Agent.status == status)

    if created_by:
        conditions.append(Agent.created_by == created_by)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count(Agent.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    query = query.order_by(Agent.created_at.desc())

    # Execute query
    result = await db.execute(query)
    agents = result.scalars().all()

    # Convert to response format
    agent_responses = []
    for agent in agents:
        agent_responses.append(AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            role=agent.role,
            system_prompt=agent.system_prompt,
            status=agent.status,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
            timeout_seconds=agent.timeout_seconds,
            total_executions=agent.total_executions,
            total_tokens_used=agent.total_tokens_used,
            average_response_time=agent.average_response_time,
            created_by=agent.created_by,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            last_used=agent.last_used
        ))

    pages = (total + limit - 1) // limit

    return PaginatedResponse(
        success=True,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        data=agent_responses
    )


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new agent."""
    # Create agent with authenticated user
    new_agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        role=agent_data.role,
        system_prompt=agent_data.system_prompt,
        temperature=agent_data.temperature,
        max_tokens=agent_data.max_tokens,
        timeout_seconds=agent_data.timeout_seconds,
        tools={"tools": agent_data.tools},
        skills={"skills": agent_data.skills},
        model_preferences={"preferred_models": agent_data.preferred_models},
        created_by=current_user.id
    )

    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)

    return AgentResponse(
        id=new_agent.id,
        name=new_agent.name,
        description=new_agent.description,
        role=new_agent.role,
        system_prompt=new_agent.system_prompt,
        status=new_agent.status,
        temperature=new_agent.temperature,
        max_tokens=new_agent.max_tokens,
        timeout_seconds=new_agent.timeout_seconds,
        total_executions=new_agent.total_executions,
        total_tokens_used=new_agent.total_tokens_used,
        average_response_time=new_agent.average_response_time,
        created_by=new_agent.created_by,
        created_at=new_agent.created_at,
        updated_at=new_agent.updated_at,
        last_used=new_agent.last_used
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get agent by ID."""
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        role=agent.role,
        system_prompt=agent.system_prompt,
        status=agent.status,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        timeout_seconds=agent.timeout_seconds,
        total_executions=agent.total_executions,
        total_tokens_used=agent.total_tokens_used,
        average_response_time=agent.average_response_time,
        created_by=agent.created_by,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        last_used=agent.last_used
    )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update agent configuration."""
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Check if user owns the agent or is superuser
    if agent.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this agent"
        )

    # Update fields if provided
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        role=agent.role,
        system_prompt=agent.system_prompt,
        status=agent.status,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        timeout_seconds=agent.timeout_seconds,
        total_executions=agent.total_executions,
        total_tokens_used=agent.total_tokens_used,
        average_response_time=agent.average_response_time,
        created_by=agent.created_by,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        last_used=agent.last_used
    )


@router.delete("/{agent_id}", response_model=BaseResponse)
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete agent by ID."""
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Check if user owns the agent or is superuser
    if agent.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this agent"
        )

    await db.delete(agent)
    await db.commit()

    return BaseResponse(
        success=True,
        message=f"Agent {agent.name} has been deleted"
    )


@router.post("/{agent_id}/execute", response_model=AgentExecutionResponse)
async def execute_agent_task(
    agent_id: UUID,
    execution_request: AgentExecutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Execute a task with the specified agent."""
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Create a BasicAIAgent instance from the database agent
    import time
    from datetime import UTC, datetime

    from app.agents.basic_agent import BasicAIAgent

    basic_agent = BasicAIAgent(
        name=agent.name,
        role=agent.role
    )

    # Configure agent with database settings
    basic_agent.temperature = execution_request.temperature or agent.temperature
    basic_agent.max_tokens = execution_request.max_tokens or agent.max_tokens

    # Execute the task
    start_time = time.time()

    try:
        # Create enhanced context for the task
        task_context = {
            "task_description": execution_request.task_description,
            "input_data": execution_request.input_data,
            "expected_output_format": execution_request.expected_output_format,
            "agent_specialization": agent.role,
            "execution_constraints": {
                "max_tokens": execution_request.max_tokens or agent.max_tokens,
                "temperature": execution_request.temperature or agent.temperature
            }
        }

        # Use enhanced prompt processing for superior results
        response = await basic_agent.process_message_enhanced(
            user_message=execution_request.task_description,
            context=task_context,
            model_preference=execution_request.preferred_model
        )

        execution_time_ms = (time.time() - start_time) * 1000

        # Update agent statistics in database
        agent.total_executions += 1
        agent.last_used = datetime.now(UTC)

        # Estimate token usage and cost (basic estimation)
        estimated_tokens = len(execution_request.task_description.split()) + len(response.split())
        estimated_cost = estimated_tokens * 0.00001  # Rough estimate

        agent.total_tokens_used += estimated_tokens

        # Update average response time
        if agent.average_response_time:
            agent.average_response_time = (agent.average_response_time + execution_time_ms) / 2
        else:
            agent.average_response_time = execution_time_ms

        await db.commit()

        from uuid import uuid4
        return AgentExecutionResponse(
            task_id=uuid4(),
            status="completed",
            output={
                "result": response,
                "input": execution_request.input_data,
                "task": execution_request.task_description
            },
            tokens_used=estimated_tokens,
            cost_usd=estimated_cost,
            execution_time_ms=execution_time_ms,
            model_used="dynamic"  # Would be set by actual MIL integration
        )

    except Exception as e:
        logger.error("Agent execution failed", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/{agent_id}/status")
async def get_agent_status(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current agent status and performance metrics."""
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return {
        "id": agent.id,
        "name": agent.name,
        "status": agent.status,
        "total_executions": agent.total_executions,
        "total_tokens_used": agent.total_tokens_used,
        "average_response_time": agent.average_response_time,
        "last_used": agent.last_used,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at
    }
