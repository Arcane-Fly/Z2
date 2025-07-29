"""
Quantum Agent Manager Service

Service layer for managing quantum computing tasks, parallel agent execution,
result collection, and collapse strategies.
"""

import asyncio
import time
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

import structlog
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.basic_agent import BasicAIAgent
from app.models.quantum import (
    QuantumTask,
    QuantumThreadResult,
    Variation,
    CollapseStrategy,
    TaskStatus,
    ThreadStatus,
)
from app.models.user import User
from app.schemas.quantum import (
    QuantumTaskCreate,
    MetricsConfiguration,
)

logger = structlog.get_logger(__name__)


class QuantumAgentManager:
    """Service class for quantum task management and execution."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.active_tasks: Dict[UUID, asyncio.Task] = {}

    async def create_task(
        self,
        user_id: UUID,
        task_data: QuantumTaskCreate,
    ) -> QuantumTask:
        """Create a new quantum task with variations."""
        logger.info(
            "Creating quantum task",
            user_id=str(user_id),
            task_name=task_data.name,
            variations_count=len(task_data.variations),
        )

        # Create the main task
        task = QuantumTask(
            name=task_data.name,
            description=task_data.description,
            task_description=task_data.task_description,
            collapse_strategy=task_data.collapse_strategy,
            metrics_config=task_data.metrics_config,
            max_parallel_executions=min(task_data.max_parallel_executions, 20),
            timeout_seconds=task_data.timeout_seconds,
            user_id=user_id,
        )

        self.db.add(task)
        await self.db.flush()

        # Create variations
        for var_data in task_data.variations:
            variation = Variation(
                task_id=task.id,
                name=var_data.name,
                description=var_data.description,
                agent_type=var_data.agent_type,
                provider=var_data.provider,
                model=var_data.model,
                prompt_modifications=var_data.prompt_modifications,
                parameters=var_data.parameters,
                weight=var_data.weight,
            )
            self.db.add(variation)

        await self.db.commit()
        await self.db.refresh(task)

        logger.info(
            "Quantum task created",
            task_id=str(task.id),
            variations_count=len(task_data.variations),
        )

        return task

    async def get_task(self, task_id: UUID, user_id: Optional[UUID] = None) -> Optional[QuantumTask]:
        """Get a quantum task by ID."""
        query = select(QuantumTask).where(QuantumTask.id == task_id)
        
        if user_id:
            query = query.where(QuantumTask.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_tasks(
        self,
        user_id: Optional[UUID] = None,
        status: Optional[TaskStatus] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[QuantumTask], int]:
        """List quantum tasks with filtering and pagination."""
        query = select(QuantumTask)
        count_query = select(func.count(QuantumTask.id))

        # Apply filters
        if user_id:
            query = query.where(QuantumTask.user_id == user_id)
            count_query = count_query.where(QuantumTask.user_id == user_id)

        if status:
            query = query.where(QuantumTask.status == status)
            count_query = count_query.where(QuantumTask.status == status)

        # Get total count
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(QuantumTask.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total_count

    async def execute_task(
        self, 
        task_id: UUID,
        force_restart: bool = False,
        custom_metrics: Optional[Dict] = None,
    ) -> QuantumTask:
        """Execute a quantum task with parallel agent executions."""
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Check if task is already running
        if task.status == TaskStatus.RUNNING and not force_restart:
            raise ValueError(f"Task {task_id} is already running")

        # Cancel existing execution if force restart
        if force_restart and task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            del self.active_tasks[task_id]

        # Update task status
        await self._update_task_status(
            task_id, TaskStatus.RUNNING, started_at=datetime.now(UTC)
        )

        # Start async execution
        execution_task = asyncio.create_task(
            self._execute_task_async(task_id, custom_metrics)
        )
        self.active_tasks[task_id] = execution_task

        logger.info("Quantum task execution started", task_id=str(task_id))

        # Return updated task
        return await self.get_task(task_id)

    async def _execute_task_async(
        self, task_id: UUID, custom_metrics: Optional[Dict] = None
    ) -> None:
        """Internal async execution method."""
        start_time = time.time()
        
        try:
            task = await self.get_task(task_id)
            if not task:
                logger.error("Task not found during execution", task_id=str(task_id))
                return

            # Get task variations
            variations = await self._get_task_variations(task_id)
            if not variations:
                await self._complete_task_with_error(
                    task_id, "No variations found for task"
                )
                return

            logger.info(
                "Starting parallel execution",
                task_id=str(task_id),
                variations_count=len(variations),
                max_parallel=task.max_parallel_executions,
            )

            # Execute variations in parallel with semaphore for concurrency control
            semaphore = asyncio.Semaphore(task.max_parallel_executions)
            execution_tasks = []

            for variation in variations:
                exec_task = asyncio.create_task(
                    self._execute_variation(task, variation, semaphore)
                )
                execution_tasks.append(exec_task)

            # Wait for all executions to complete with timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(*execution_tasks, return_exceptions=True),
                    timeout=task.timeout_seconds,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "Task execution timed out", 
                    task_id=str(task_id),
                    timeout=task.timeout_seconds
                )
                # Cancel remaining tasks
                for exec_task in execution_tasks:
                    if not exec_task.done():
                        exec_task.cancel()

            # Collect results and apply collapse strategy
            await self._finalize_task_execution(task_id, custom_metrics, start_time)

        except Exception as e:
            logger.error(
                "Error during task execution",
                task_id=str(task_id),
                error=str(e),
                exc_info=True,
            )
            await self._complete_task_with_error(task_id, str(e))
        finally:
            # Clean up
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]

    async def _execute_variation(
        self, task: QuantumTask, variation: Variation, semaphore: asyncio.Semaphore
    ) -> None:
        """Execute a single variation with proper error handling."""
        async with semaphore:
            thread_result = None
            start_time = time.time()
            
            try:
                # Create thread result record
                thread_result = QuantumThreadResult(
                    task_id=task.id,
                    variation_id=variation.id,
                    thread_name=f"{variation.name}-{variation.id}",
                    status=ThreadStatus.RUNNING,
                    started_at=datetime.now(UTC),
                )
                self.db.add(thread_result)
                await self.db.flush()

                logger.debug(
                    "Starting variation execution",
                    task_id=str(task.id),
                    variation_id=str(variation.id),
                    variation_name=variation.name,
                )

                # Create and configure agent based on variation
                agent = await self._create_agent_for_variation(variation)
                
                # Apply prompt modifications
                modified_task_description = self._apply_prompt_modifications(
                    task.task_description, variation.prompt_modifications
                )

                # Execute the agent
                execution_start = time.time()
                result = await self._execute_agent_safely(
                    agent, modified_task_description, variation.parameters
                )
                execution_time = time.time() - execution_start

                # Calculate metrics
                metrics = await self._calculate_thread_metrics(
                    result, execution_time, variation
                )

                # Update thread result
                thread_result.status = ThreadStatus.COMPLETED
                thread_result.result = result
                thread_result.execution_time = execution_time
                thread_result.success_rate = metrics.get("success_rate", 0.0)
                thread_result.completeness = metrics.get("completeness", 0.0)
                thread_result.accuracy = metrics.get("accuracy", 0.0)
                thread_result.total_score = metrics.get("total_score", 0.0)
                thread_result.detailed_metrics = metrics
                thread_result.completed_at = datetime.now(UTC)
                
                # Add provider/model info if available
                if hasattr(result, "provider"):
                    thread_result.provider_used = result.get("provider")
                if hasattr(result, "model"):
                    thread_result.model_used = result.get("model")

                await self.db.flush()

                logger.debug(
                    "Variation execution completed",
                    task_id=str(task.id),
                    variation_id=str(variation.id),
                    execution_time=execution_time,
                    score=metrics.get("total_score", 0.0),
                )

            except Exception as e:
                logger.error(
                    "Error executing variation",
                    task_id=str(task.id),
                    variation_id=str(variation.id),
                    error=str(e),
                    exc_info=True,
                )
                
                if thread_result:
                    thread_result.status = ThreadStatus.FAILED
                    thread_result.error_message = str(e)
                    thread_result.completed_at = datetime.now(UTC)
                    thread_result.execution_time = time.time() - start_time
                    await self.db.flush()

    async def _create_agent_for_variation(self, variation: Variation) -> BasicAIAgent:
        """Create an agent instance for the variation."""
        # For now, create a basic agent - can be extended to support different agent types
        agent = BasicAIAgent(
            agent_name=f"QuantumAgent-{variation.name}",
            role=variation.agent_type
        )
        
        # Apply variation parameters if available
        if variation.parameters:
            if "temperature" in variation.parameters:
                # Apply temperature if agent supports it
                pass
            if "max_tokens" in variation.parameters:
                # Apply max tokens if agent supports it
                pass
                
        return agent

    def _apply_prompt_modifications(
        self, base_prompt: str, modifications: Dict
    ) -> str:
        """Apply prompt modifications from variation."""
        modified_prompt = base_prompt
        
        if not modifications:
            return modified_prompt
            
        # Apply prefix/suffix modifications
        if "prefix" in modifications:
            modified_prompt = f"{modifications['prefix']}\n\n{modified_prompt}"
        if "suffix" in modifications:
            modified_prompt = f"{modified_prompt}\n\n{modifications['suffix']}"
            
        # Apply replacements
        if "replacements" in modifications:
            for old, new in modifications["replacements"].items():
                modified_prompt = modified_prompt.replace(old, new)
                
        # Apply style modifications
        if "style" in modifications:
            style = modifications["style"]
            modified_prompt = f"{modified_prompt}\n\nPlease respond in a {style} style."
            
        return modified_prompt

    async def _execute_agent_safely(
        self, agent: BasicAIAgent, task_description: str, parameters: Dict
    ) -> Dict:
        """Safely execute agent with error handling."""
        try:
            # For now, use basic agent execution - can be expanded
            response = await agent.process_message(task_description)
            
            # Return structured result
            return {
                "response": response,
                "success": True,
                "metadata": {
                    "agent_name": agent.name,
                    "agent_role": agent.role,
                    # Add execution context if available
                    "execution_context": parameters.get("context", {}),
                }
            }
        except Exception as e:
            logger.error(
                "Agent execution failed",
                agent_name=agent.name,
                error=str(e),
                exc_info=True,
            )
            return {
                "response": None,
                "success": False,
                "error": str(e),
                "metadata": {
                    "agent_name": agent.name,
                    "agent_role": agent.role,
                    "execution_context": parameters.get("context", {}),
                }
            }

    async def _calculate_thread_metrics(
        self, result: Dict, execution_time: float, variation: Variation
    ) -> Dict:
        """Calculate metrics for a thread result."""
        metrics = {}
        
        # Basic success rate
        metrics["success_rate"] = 1.0 if result.get("success", False) else 0.0
        
        # Execution time normalized (lower is better, normalize to 0-1 scale)
        # Assume 30 seconds is baseline, anything faster gets higher score
        max_time = 30.0
        metrics["execution_time_score"] = max(0.0, (max_time - execution_time) / max_time)
        
        # Completeness - check if response has content
        response = result.get("response", "")
        if isinstance(response, str):
            # Basic completeness based on response length
            metrics["completeness"] = min(1.0, len(response) / 100.0)  # Normalize to 100 chars
        else:
            metrics["completeness"] = 1.0 if response else 0.0
            
        # Accuracy - placeholder for now, could be enhanced with more sophisticated scoring
        metrics["accuracy"] = metrics["success_rate"] * 0.8 if result.get("success") else 0.0
        
        # Calculate total score with default weights
        weights = {
            "success_rate": 0.3,
            "execution_time_score": 0.2,
            "completeness": 0.3,
            "accuracy": 0.2,
        }
        
        total_score = sum(
            metrics.get(metric, 0.0) * weight 
            for metric, weight in weights.items()
        )
        metrics["total_score"] = total_score
        
        return metrics

    async def _get_task_variations(self, task_id: UUID) -> List[Variation]:
        """Get all variations for a task."""
        query = select(Variation).where(Variation.task_id == task_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _get_task_results(self, task_id: UUID) -> List[QuantumThreadResult]:
        """Get all thread results for a task."""
        query = select(QuantumThreadResult).where(QuantumThreadResult.task_id == task_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _finalize_task_execution(
        self, task_id: UUID, custom_metrics: Optional[Dict], start_time: float
    ) -> None:
        """Finalize task execution by applying collapse strategy."""
        task = await self.get_task(task_id)
        if not task:
            return

        results = await self._get_task_results(task_id)
        
        if not results:
            await self._complete_task_with_error(task_id, "No results generated")
            return

        logger.info(
            "Finalizing task execution",
            task_id=str(task_id),
            results_count=len(results),
            collapse_strategy=task.collapse_strategy,
        )

        # Apply collapse strategy
        collapsed_result, final_metrics = await self._apply_collapse_strategy(
            task, results, custom_metrics
        )

        # Update task with final results
        execution_time = time.time() - start_time
        execution_summary = {
            "total_variations": len(results),
            "successful_executions": len([r for r in results if r.status == ThreadStatus.COMPLETED]),
            "failed_executions": len([r for r in results if r.status == ThreadStatus.FAILED]),
            "average_execution_time": sum(r.execution_time or 0 for r in results) / len(results) if results else 0,
            "collapse_strategy_used": task.collapse_strategy,
        }

        await self._update_task_completion(
            task_id,
            collapsed_result,
            final_metrics,
            execution_summary,
            execution_time,
        )

        logger.info(
            "Task execution completed",
            task_id=str(task_id),
            execution_time=execution_time,
            final_score=final_metrics.get("final_score", 0.0),
        )

    async def _apply_collapse_strategy(
        self, task: QuantumTask, results: List[QuantumThreadResult], custom_metrics: Optional[Dict]
    ) -> Tuple[Dict, Dict]:
        """Apply the specified collapse strategy to results."""
        completed_results = [r for r in results if r.status == ThreadStatus.COMPLETED]
        
        if not completed_results:
            return {"error": "No completed results"}, {"final_score": 0.0}

        strategy = task.collapse_strategy

        if strategy == CollapseStrategy.FIRST_SUCCESS:
            return self._collapse_first_success(completed_results)
        elif strategy == CollapseStrategy.BEST_SCORE:
            return self._collapse_best_score(completed_results)
        elif strategy == CollapseStrategy.CONSENSUS:
            return self._collapse_consensus(completed_results)
        elif strategy == CollapseStrategy.COMBINED:
            return self._collapse_combined(completed_results)
        elif strategy == CollapseStrategy.WEIGHTED:
            variations = await self._get_task_variations(task.id)
            return self._collapse_weighted(completed_results, variations)
        else:
            # Default to best score
            return self._collapse_best_score(completed_results)

    def _collapse_first_success(self, results: List[QuantumThreadResult]) -> Tuple[Dict, Dict]:
        """Return the first successful result."""
        # Sort by completion time
        sorted_results = sorted(results, key=lambda r: r.completed_at or datetime.min)
        first_result = sorted_results[0]
        
        return first_result.result or {}, {
            "final_score": first_result.total_score or 0.0,
            "strategy": "first_success",
            "selected_result_id": str(first_result.id),
        }

    def _collapse_best_score(self, results: List[QuantumThreadResult]) -> Tuple[Dict, Dict]:
        """Return the result with the highest score."""
        best_result = max(results, key=lambda r: r.total_score or 0.0)
        
        return best_result.result or {}, {
            "final_score": best_result.total_score or 0.0,
            "strategy": "best_score",
            "selected_result_id": str(best_result.id),
            "score_distribution": [r.total_score or 0.0 for r in results],
        }

    def _collapse_consensus(self, results: List[QuantumThreadResult]) -> Tuple[Dict, Dict]:
        """Create consensus result (simplified implementation)."""
        # For now, use best score but could implement voting/averaging
        best_result = max(results, key=lambda r: r.total_score or 0.0)
        avg_score = sum(r.total_score or 0.0 for r in results) / len(results)
        
        return best_result.result or {}, {
            "final_score": avg_score,
            "strategy": "consensus",
            "selected_result_id": str(best_result.id),
            "consensus_confidence": len(results) / 10.0,  # Simple confidence metric
        }

    def _collapse_combined(self, results: List[QuantumThreadResult]) -> Tuple[Dict, Dict]:
        """Combine multiple results (simplified implementation)."""
        # Combine responses into a single result
        combined_responses = []
        total_score = 0.0
        
        for result in results:
            if result.result and result.result.get("response"):
                combined_responses.append({
                    "source": result.thread_name,
                    "response": result.result["response"],
                    "score": result.total_score or 0.0,
                })
                total_score += result.total_score or 0.0
        
        avg_score = total_score / len(results) if results else 0.0
        
        combined_result = {
            "combined_responses": combined_responses,
            "summary": f"Combined result from {len(results)} variations",
        }
        
        return combined_result, {
            "final_score": avg_score,
            "strategy": "combined",
            "sources_count": len(results),
        }

    def _collapse_weighted(
        self, results: List[QuantumThreadResult], variations: List[Variation]
    ) -> Tuple[Dict, Dict]:
        """Apply weighted collapse based on variation weights."""
        # Create variation weight mapping
        variation_weights = {v.id: v.weight for v in variations}
        
        weighted_score = 0.0
        total_weight = 0.0
        best_weighted_result = None
        best_weighted_score = 0.0
        
        for result in results:
            weight = variation_weights.get(result.variation_id, 1.0)
            score = (result.total_score or 0.0) * weight
            weighted_score += score
            total_weight += weight
            
            if score > best_weighted_score:
                best_weighted_score = score
                best_weighted_result = result
        
        final_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        return best_weighted_result.result or {}, {
            "final_score": final_score,
            "strategy": "weighted",
            "selected_result_id": str(best_weighted_result.id),
            "total_weight": total_weight,
        }

    async def _update_task_status(
        self,
        task_id: UUID,
        status: TaskStatus,
        progress: Optional[float] = None,
        started_at: Optional[datetime] = None,
    ) -> None:
        """Update task status and related fields."""
        update_data = {"status": status, "updated_at": datetime.now(UTC)}
        
        if progress is not None:
            update_data["progress"] = progress
        if started_at is not None:
            update_data["started_at"] = started_at
            
        query = (
            update(QuantumTask)
            .where(QuantumTask.id == task_id)
            .values(**update_data)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def _update_task_completion(
        self,
        task_id: UUID,
        collapsed_result: Dict,
        final_metrics: Dict,
        execution_summary: Dict,
        total_execution_time: float,
    ) -> None:
        """Update task with completion data."""
        query = (
            update(QuantumTask)
            .where(QuantumTask.id == task_id)
            .values(
                status=TaskStatus.COMPLETED,
                progress=1.0,
                collapsed_result=collapsed_result,
                final_metrics=final_metrics,
                execution_summary=execution_summary,
                completed_at=datetime.now(UTC),
                total_execution_time=total_execution_time,
                updated_at=datetime.now(UTC),
            )
        )
        await self.db.execute(query)
        await self.db.commit()

    async def _complete_task_with_error(self, task_id: UUID, error_message: str) -> None:
        """Complete task with error status."""
        query = (
            update(QuantumTask)
            .where(QuantumTask.id == task_id)
            .values(
                status=TaskStatus.FAILED,
                execution_summary={"error": error_message},
                completed_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )
        await self.db.execute(query)
        await self.db.commit()

    async def cancel_task(self, task_id: UUID) -> bool:
        """Cancel a running task."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            del self.active_tasks[task_id]
            
            await self._update_task_status(task_id, TaskStatus.CANCELLED)
            
            logger.info("Task cancelled", task_id=str(task_id))
            return True
        
        return False