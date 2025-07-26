"""
Workflow orchestration endpoints for Z2 API.
"""

from datetime import UTC
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.models.workflow import Workflow, WorkflowExecution
from app.schemas import (
    BaseResponse,
    PaginatedResponse,
    WorkflowCreate,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowResponse,
    WorkflowUpdate,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_workflows(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    status: Optional[str] = Query(None, description="Filter by workflow status"),
    created_by: Optional[UUID] = Query(None, description="Filter by creator"),
    is_template: Optional[bool] = Query(None, description="Filter by template status"),
    template_category: Optional[str] = Query(None, description="Filter by template category"),
    db: AsyncSession = Depends(get_db),
):
    """List all workflows with filtering and pagination."""

    # Build query
    query = select(Workflow)

    # Apply filters
    conditions = []
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                Workflow.name.ilike(search_pattern),
                Workflow.description.ilike(search_pattern),
                Workflow.goal.ilike(search_pattern)
            )
        )

    if status:
        conditions.append(Workflow.status == status)

    if created_by:
        conditions.append(Workflow.created_by == created_by)

    if is_template is not None:
        conditions.append(Workflow.is_template == is_template)

    if template_category:
        conditions.append(Workflow.template_category == template_category)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count(Workflow.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    query = query.order_by(Workflow.created_at.desc())

    # Execute query
    result = await db.execute(query)
    workflows = result.scalars().all()

    # Convert to response format
    workflow_responses = []
    for workflow in workflows:
        # Count agents and tasks
        agent_count = len(workflow.agent_team.get("agents", [])) if workflow.agent_team else 0
        task_count = len(workflow.workflow_graph.get("tasks", [])) if workflow.workflow_graph else 0

        # Calculate progress percentage
        progress_percentage = 0.0
        if workflow.status == "completed":
            progress_percentage = 100.0
        elif workflow.status == "running" and workflow.current_step:
            # Simple progress calculation based on current step
            if task_count > 0:
                progress_percentage = 50.0  # Rough estimate

        workflow_responses.append(WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            goal=workflow.goal,
            status=workflow.status,
            max_duration_seconds=3600,  # Default value
            max_cost_usd=10.0,  # Default value
            require_human_approval=False,  # Default value
            current_step=workflow.current_step,
            progress_percentage=progress_percentage,
            total_tokens_used=workflow.total_tokens_used,
            total_cost_usd=workflow.total_cost_usd,
            created_at=workflow.created_at,
            started_at=workflow.started_at,
            completed_at=workflow.completed_at,
            created_by=workflow.created_by,
            agent_count=agent_count,
            task_count=task_count
        ))

    pages = (total + limit - 1) // limit

    return PaginatedResponse(
        success=True,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        data=workflow_responses
    )


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new multi-agent workflow."""
    # TODO: Get current user from authentication
    # For now, we'll need a valid user ID - use the first user as placeholder
    stmt = select(User).limit(1)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users found. Create a user first."
        )

    # Create workflow
    new_workflow = Workflow(
        name=workflow_data.name,
        description=workflow_data.description,
        goal=workflow_data.goal,
        agent_team={"agents": [str(agent_id) for agent_id in workflow_data.agent_ids]},
        workflow_graph={"tasks": [task.model_dump() for task in workflow_data.tasks]},
        execution_policy={
            "max_duration_seconds": workflow_data.max_duration_seconds,
            "max_cost_usd": workflow_data.max_cost_usd,
            "require_human_approval": workflow_data.require_human_approval
        },
        created_by=user.id
    )

    db.add(new_workflow)
    await db.commit()
    await db.refresh(new_workflow)

    return WorkflowResponse(
        id=new_workflow.id,
        name=new_workflow.name,
        description=new_workflow.description,
        goal=new_workflow.goal,
        status=new_workflow.status,
        max_duration_seconds=workflow_data.max_duration_seconds,
        max_cost_usd=workflow_data.max_cost_usd,
        require_human_approval=workflow_data.require_human_approval,
        current_step=new_workflow.current_step,
        progress_percentage=0.0,
        total_tokens_used=new_workflow.total_tokens_used,
        total_cost_usd=new_workflow.total_cost_usd,
        created_at=new_workflow.created_at,
        started_at=new_workflow.started_at,
        completed_at=new_workflow.completed_at,
        created_by=new_workflow.created_by,
        agent_count=len(workflow_data.agent_ids),
        task_count=len(workflow_data.tasks)
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get workflow by ID with full configuration and state."""
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    # Count agents and tasks
    agent_count = len(workflow.agent_team.get("agents", [])) if workflow.agent_team else 0
    task_count = len(workflow.workflow_graph.get("tasks", [])) if workflow.workflow_graph else 0

    # Calculate progress percentage
    progress_percentage = 0.0
    if workflow.status == "completed":
        progress_percentage = 100.0
    elif workflow.status == "running" and workflow.current_step:
        progress_percentage = 50.0  # Rough estimate

    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        goal=workflow.goal,
        status=workflow.status,
        max_duration_seconds=3600,  # From execution_policy
        max_cost_usd=10.0,  # From execution_policy
        require_human_approval=False,  # From execution_policy
        current_step=workflow.current_step,
        progress_percentage=progress_percentage,
        total_tokens_used=workflow.total_tokens_used,
        total_cost_usd=workflow.total_cost_usd,
        created_at=workflow.created_at,
        started_at=workflow.started_at,
        completed_at=workflow.completed_at,
        created_by=workflow.created_by,
        agent_count=agent_count,
        task_count=task_count
    )


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update workflow configuration."""
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    # Check if workflow can be updated (not running)
    if workflow.status in ["running", "paused"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update running or paused workflow"
        )

    # Update fields if provided
    update_data = workflow_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)

    await db.commit()
    await db.refresh(workflow)

    # Count agents and tasks
    agent_count = len(workflow.agent_team.get("agents", [])) if workflow.agent_team else 0
    task_count = len(workflow.workflow_graph.get("tasks", [])) if workflow.workflow_graph else 0

    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        goal=workflow.goal,
        status=workflow.status,
        max_duration_seconds=3600,
        max_cost_usd=10.0,
        require_human_approval=False,
        current_step=workflow.current_step,
        progress_percentage=0.0,
        total_tokens_used=workflow.total_tokens_used,
        total_cost_usd=workflow.total_cost_usd,
        created_at=workflow.created_at,
        started_at=workflow.started_at,
        completed_at=workflow.completed_at,
        created_by=workflow.created_by,
        agent_count=agent_count,
        task_count=task_count
    )


@router.delete("/{workflow_id}", response_model=BaseResponse)
async def delete_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete workflow by ID."""
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    # Check if workflow can be deleted (not running)
    if workflow.status in ["running", "paused"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete running or paused workflow"
        )

    await db.delete(workflow)
    await db.commit()

    return BaseResponse(
        success=True,
        message=f"Workflow {workflow.name} has been deleted"
    )


@router.post("/{workflow_id}/start", response_model=WorkflowExecutionResponse)
async def start_workflow(
    workflow_id: UUID,
    execution_request: WorkflowExecutionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Start workflow execution."""
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    if workflow.status in ["running", "paused"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is already running or paused"
        )

    # TODO: Implement actual workflow execution
    # For now, return a mock response
    from datetime import datetime
    from uuid import uuid4

    # Update workflow status
    workflow.status = "running"
    workflow.started_at = datetime.now(UTC)
    await db.commit()

    return WorkflowExecutionResponse(
        execution_id=uuid4(),
        workflow_id=workflow_id,
        status="running",
        started_at=workflow.started_at,
        estimated_completion=None,
        progress={"current_step": "initialization", "completion_percentage": 0}
    )


@router.post("/{workflow_id}/stop", response_model=BaseResponse)
async def stop_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Stop workflow execution."""
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    if workflow.status not in ["running", "paused"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not running"
        )

    # Update workflow status
    workflow.status = "draft"
    await db.commit()

    return BaseResponse(
        success=True,
        message=f"Workflow {workflow.name} has been stopped"
    )


@router.post("/{workflow_id}/pause", response_model=BaseResponse)
async def pause_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Pause workflow execution."""
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    if workflow.status != "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not running"
        )

    # Update workflow status
    workflow.status = "paused"
    await db.commit()

    return BaseResponse(
        success=True,
        message=f"Workflow {workflow.name} has been paused"
    )


@router.post("/{workflow_id}/resume", response_model=BaseResponse)
async def resume_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Resume paused workflow execution."""
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    if workflow.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not paused"
        )

    # Update workflow status
    workflow.status = "running"
    await db.commit()

    return BaseResponse(
        success=True,
        message=f"Workflow {workflow.name} has been resumed"
    )


@router.get("/{workflow_id}/status")
async def get_workflow_status(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get current workflow status and execution metrics."""
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    return {
        "id": workflow.id,
        "name": workflow.name,
        "status": workflow.status,
        "current_step": workflow.current_step,
        "started_at": workflow.started_at,
        "completed_at": workflow.completed_at,
        "execution_duration_seconds": workflow.execution_duration_seconds,
        "total_tokens_used": workflow.total_tokens_used,
        "total_cost_usd": workflow.total_cost_usd,
        "success_rate": workflow.success_rate
    }


@router.get("/{workflow_id}/logs")
async def get_workflow_logs(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get workflow execution logs and agent traces."""
    # Get workflow executions
    stmt = select(WorkflowExecution).where(WorkflowExecution.workflow_id == workflow_id)
    result = await db.execute(stmt)
    executions = result.scalars().all()

    return {
        "workflow_id": workflow_id,
        "total_executions": len(executions),
        "executions": [
            {
                "id": execution.id,
                "status": execution.status,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "duration_seconds": execution.duration_seconds,
                "tokens_used": execution.tokens_used,
                "cost_usd": execution.cost_usd,
                "execution_log": execution.execution_log
            }
            for execution in executions
        ]
    }
