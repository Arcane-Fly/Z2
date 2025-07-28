"""
Quantum computing endpoints for Z2 API.
"""

from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.quantum import TaskStatus
from app.schemas import BaseResponse
from app.schemas.quantum import (
    QuantumTaskCreate,
    QuantumTaskUpdate,
    QuantumTaskResponse,
    QuantumTaskDetailResponse,
    QuantumTaskListResponse,
    QuantumTaskExecutionRequest,
    QuantumThreadResultResponse,
    VariationResponse,
)
from app.services.quantum_service import QuantumAgentManager

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/tasks/create", response_model=QuantumTaskResponse)
async def create_quantum_task(
    task_data: QuantumTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new quantum task with variations."""
    try:
        quantum_manager = QuantumAgentManager(db)
        task = await quantum_manager.create_task(current_user.id, task_data)
        
        logger.info(
            "Quantum task created",
            task_id=str(task.id),
            user_id=str(current_user.id),
            task_name=task.name,
        )
        
        return QuantumTaskResponse.model_validate(task)
        
    except ValueError as e:
        logger.error("Invalid task creation request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating quantum task", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quantum task"
        )


@router.post("/tasks/{task_id}/execute", response_model=QuantumTaskResponse)
async def execute_quantum_task(
    task_id: UUID,
    execution_request: QuantumTaskExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a quantum task with parallel agent variations."""
    try:
        quantum_manager = QuantumAgentManager(db)
        
        # Check if user owns the task or has permissions
        task = await quantum_manager.get_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        executed_task = await quantum_manager.execute_task(
            task_id,
            force_restart=execution_request.force_restart,
            custom_metrics=execution_request.custom_metrics,
        )
        
        logger.info(
            "Quantum task execution started",
            task_id=str(task_id),
            user_id=str(current_user.id),
            force_restart=execution_request.force_restart,
        )
        
        return QuantumTaskResponse.model_validate(executed_task)
        
    except ValueError as e:
        logger.error("Invalid task execution request", task_id=str(task_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Error executing quantum task", 
            task_id=str(task_id), 
            error=str(e), 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute quantum task"
        )


@router.get("/tasks/{task_id}", response_model=QuantumTaskDetailResponse)
async def get_quantum_task(
    task_id: UUID,
    include_results: bool = Query(True, description="Include thread results"),
    include_variations: bool = Query(True, description="Include variations"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a quantum task."""
    try:
        quantum_manager = QuantumAgentManager(db)
        
        # Get the task
        task = await quantum_manager.get_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Convert to response model
        task_response = QuantumTaskDetailResponse.model_validate(task)
        
        # Add variations if requested
        if include_variations:
            variations = await quantum_manager._get_task_variations(task_id)
            task_response.variations = [
                VariationResponse.model_validate(var) for var in variations
            ]
        
        # Add thread results if requested
        if include_results:
            results = await quantum_manager._get_task_results(task_id)
            task_response.thread_results = [
                QuantumThreadResultResponse.model_validate(result) for result in results
            ]
        
        return task_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving quantum task", 
            task_id=str(task_id), 
            error=str(e), 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quantum task"
        )


@router.get("/tasks", response_model=QuantumTaskListResponse)
async def list_quantum_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List quantum tasks for the current user with filtering and pagination."""
    try:
        quantum_manager = QuantumAgentManager(db)
        
        tasks, total_count = await quantum_manager.list_tasks(
            user_id=current_user.id,
            status=status,
            page=page,
            page_size=page_size,
        )
        
        # Convert to response models
        task_responses = [
            QuantumTaskResponse.model_validate(task) for task in tasks
        ]
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        
        return QuantumTaskListResponse(
            tasks=task_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
        
    except Exception as e:
        logger.error(
            "Error listing quantum tasks", 
            user_id=str(current_user.id), 
            error=str(e), 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list quantum tasks"
        )


@router.patch("/tasks/{task_id}", response_model=QuantumTaskResponse)
async def update_quantum_task(
    task_id: UUID,
    task_update: QuantumTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a quantum task."""
    try:
        quantum_manager = QuantumAgentManager(db)
        
        # Check if user owns the task
        task = await quantum_manager.get_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Update task fields
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await db.commit()
        await db.refresh(task)
        
        logger.info(
            "Quantum task updated",
            task_id=str(task_id),
            user_id=str(current_user.id),
            updated_fields=list(update_data.keys()),
        )
        
        return QuantumTaskResponse.model_validate(task)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error updating quantum task", 
            task_id=str(task_id), 
            error=str(e), 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quantum task"
        )


@router.post("/tasks/{task_id}/cancel", response_model=BaseResponse)
async def cancel_quantum_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running quantum task."""
    try:
        quantum_manager = QuantumAgentManager(db)
        
        # Check if user owns the task
        task = await quantum_manager.get_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check if task can be cancelled
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel task with status: {task.status}"
            )
        
        success = await quantum_manager.cancel_task(task_id)
        
        if success:
            logger.info(
                "Quantum task cancelled",
                task_id=str(task_id),
                user_id=str(current_user.id),
            )
            return BaseResponse(
                success=True,
                message="Task cancelled successfully"
            )
        else:
            return BaseResponse(
                success=False,
                message="Task was not running"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error cancelling quantum task", 
            task_id=str(task_id), 
            error=str(e), 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel quantum task"
        )


@router.delete("/tasks/{task_id}", response_model=BaseResponse)
async def delete_quantum_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a quantum task and all related data."""
    try:
        quantum_manager = QuantumAgentManager(db)
        
        # Check if user owns the task
        task = await quantum_manager.get_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Can't delete running tasks
        if task.status == TaskStatus.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete running task. Cancel it first."
            )
        
        # Cancel if still pending
        if task.status == TaskStatus.PENDING:
            await quantum_manager.cancel_task(task_id)
        
        # Delete the task (cascade should handle related records)
        await db.delete(task)
        await db.commit()
        
        logger.info(
            "Quantum task deleted",
            task_id=str(task_id),
            user_id=str(current_user.id),
        )
        
        return BaseResponse(
            success=True,
            message="Task deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error deleting quantum task", 
            task_id=str(task_id), 
            error=str(e), 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete quantum task"
        )


@router.get("/tasks/{task_id}/results", response_model=list[QuantumThreadResultResponse])
async def get_task_results(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all thread results for a quantum task."""
    try:
        quantum_manager = QuantumAgentManager(db)
        
        # Check if user owns the task
        task = await quantum_manager.get_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        results = await quantum_manager._get_task_results(task_id)
        
        return [
            QuantumThreadResultResponse.model_validate(result) for result in results
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving task results", 
            task_id=str(task_id), 
            error=str(e), 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task results"
        )


@router.get("/tasks/{task_id}/variations", response_model=list[VariationResponse])
async def get_task_variations(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all variations for a quantum task."""
    try:
        quantum_manager = QuantumAgentManager(db)
        
        # Check if user owns the task
        task = await quantum_manager.get_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        variations = await quantum_manager._get_task_variations(task_id)
        
        return [
            VariationResponse.model_validate(variation) for variation in variations
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving task variations", 
            task_id=str(task_id), 
            error=str(e), 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task variations"
        )