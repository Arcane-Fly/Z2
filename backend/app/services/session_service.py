"""
Session Service

Database service layer for MCP and A2A session management.
Handles session creation, tracking, and cleanup operations.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Any
from uuid import UUID

from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import (
    MCPSession,
    A2ASession, 
    A2ANegotiation,
    TaskExecution
)


class SessionService:
    """Service class for session management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # MCP Session Management
    async def create_mcp_session(
        self,
        session_id: str,
        protocol_version: str,
        client_info: dict,
        client_capabilities: Optional[dict] = None,
        server_capabilities: Optional[dict] = None,
        expires_in_minutes: int = 30,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MCPSession:
        """Create a new MCP session."""
        
        expires_at = datetime.now(UTC) + timedelta(minutes=expires_in_minutes)
        
        session = MCPSession(
            session_id=session_id,
            protocol_version=protocol_version,
            client_name=client_info.get("name"),
            client_version=client_info.get("version"),
            client_info=client_info,
            client_capabilities=client_capabilities,
            server_capabilities=server_capabilities,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self.db.add(session)
        return session

    async def get_mcp_session(self, session_id: str) -> Optional[MCPSession]:
        """Get an MCP session by session ID."""
        result = await self.db.execute(
            select(MCPSession).where(MCPSession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_mcp_session_activity(self, session_id: str) -> bool:
        """Update the last activity timestamp for an MCP session."""
        result = await self.db.execute(
            update(MCPSession)
            .where(MCPSession.session_id == session_id)
            .values(last_activity=datetime.now(UTC))
        )
        return result.rowcount > 0

    async def close_mcp_session(self, session_id: str) -> bool:
        """Close an MCP session."""
        result = await self.db.execute(
            update(MCPSession)
            .where(MCPSession.session_id == session_id)
            .values(
                is_active=False,
                closed_at=datetime.now(UTC)
            )
        )
        return result.rowcount > 0

    async def list_active_mcp_sessions(self) -> list[MCPSession]:
        """List all active MCP sessions."""
        now = datetime.now(UTC)
        result = await self.db.execute(
            select(MCPSession).where(
                and_(
                    MCPSession.is_active == True,
                    or_(
                        MCPSession.expires_at.is_(None),
                        MCPSession.expires_at > now
                    )
                )
            )
        )
        return list(result.scalars().all())

    # A2A Session Management
    async def create_a2a_session(
        self,
        session_id: str,
        agent_id: str,
        agent_name: str,
        agent_capabilities: list[str],
        protocol_version: str,
        expires_in_hours: int = 1,
        public_key: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> A2ASession:
        """Create a new A2A session."""
        
        expires_at = datetime.now(UTC) + timedelta(hours=expires_in_hours)
        
        session = A2ASession(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name,
            agent_capabilities=agent_capabilities,
            protocol_version=protocol_version,
            public_key=public_key,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self.db.add(session)
        return session

    async def get_a2a_session(self, session_id: str) -> Optional[A2ASession]:
        """Get an A2A session by session ID."""
        result = await self.db.execute(
            select(A2ASession).where(A2ASession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_a2a_session_activity(
        self, session_id: str, has_websocket: Optional[bool] = None
    ) -> bool:
        """Update the last activity timestamp for an A2A session."""
        values = {"last_activity": datetime.now(UTC)}
        if has_websocket is not None:
            values["has_websocket"] = has_websocket
            
        result = await self.db.execute(
            update(A2ASession)
            .where(A2ASession.session_id == session_id)
            .values(**values)
        )
        return result.rowcount > 0

    async def close_a2a_session(self, session_id: str) -> bool:
        """Close an A2A session."""
        result = await self.db.execute(
            update(A2ASession)
            .where(A2ASession.session_id == session_id)
            .values(
                is_active=False,
                has_websocket=False,
                closed_at=datetime.now(UTC)
            )
        )
        return result.rowcount > 0

    async def list_active_a2a_sessions(self) -> list[A2ASession]:
        """List all active A2A sessions."""
        now = datetime.now(UTC)
        result = await self.db.execute(
            select(A2ASession).where(
                and_(
                    A2ASession.is_active == True,
                    A2ASession.expires_at > now
                )
            )
        )
        return list(result.scalars().all())

    # A2A Negotiation Management
    async def create_a2a_negotiation(
        self,
        negotiation_id: str,
        session_id: str,
        requested_skills: list[str],
        available_skills: list[str],
        task_description: str,
        task_parameters: Optional[dict] = None,
        accepted: bool = False,
        proposed_workflow: Optional[dict] = None,
        estimated_duration: Optional[int] = None,
        cost_estimate: Optional[str] = None,
        priority: int = 5,
        timeout_seconds: Optional[int] = None,
    ) -> A2ANegotiation:
        """Create a new A2A negotiation."""
        
        negotiation = A2ANegotiation(
            negotiation_id=negotiation_id,
            session_id=session_id,
            requested_skills=requested_skills,
            available_skills=available_skills,
            task_description=task_description,
            task_parameters=task_parameters,
            accepted=accepted,
            proposed_workflow=proposed_workflow,
            estimated_duration=estimated_duration,
            cost_estimate=cost_estimate,
            priority=priority,
            timeout_seconds=timeout_seconds,
            status="accepted" if accepted else "pending",
        )
        
        self.db.add(negotiation)
        return negotiation

    async def get_a2a_negotiation(self, negotiation_id: str) -> Optional[A2ANegotiation]:
        """Get an A2A negotiation by negotiation ID."""
        result = await self.db.execute(
            select(A2ANegotiation).where(A2ANegotiation.negotiation_id == negotiation_id)
        )
        return result.scalar_one_or_none()

    async def update_negotiation_status(
        self,
        negotiation_id: str,
        status: str,
        completed_at: Optional[datetime] = None,
    ) -> bool:
        """Update the status of a negotiation."""
        values = {"status": status}
        if completed_at:
            values["completed_at"] = completed_at
        elif status in ["completed", "failed"]:
            values["completed_at"] = datetime.now(UTC)
            
        result = await self.db.execute(
            update(A2ANegotiation)
            .where(A2ANegotiation.negotiation_id == negotiation_id)
            .values(**values)
        )
        return result.rowcount > 0

    # Task Execution Management
    async def create_task_execution(
        self,
        task_id: str,
        session_id: str,
        task_type: str,
        task_name: str,
        task_parameters: Optional[dict] = None,
        negotiation_id: Optional[str] = None,
        can_cancel: bool = True,
    ) -> TaskExecution:
        """Create a new task execution record."""
        
        task = TaskExecution(
            task_id=task_id,
            session_id=session_id,
            negotiation_id=negotiation_id,
            task_type=task_type,
            task_name=task_name,
            task_parameters=task_parameters,
            can_cancel=can_cancel,
        )
        
        self.db.add(task)
        return task

    async def get_task_execution(self, task_id: str) -> Optional[TaskExecution]:
        """Get a task execution by task ID."""
        result = await self.db.execute(
            select(TaskExecution).where(TaskExecution.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def update_task_progress(
        self,
        task_id: str,
        progress: float,
        status: Optional[str] = None,
    ) -> bool:
        """Update task progress and optionally status."""
        values = {"progress": str(progress)}
        
        if status:
            values["status"] = status
            if status == "running" and not await self._task_has_started(task_id):
                values["started_at"] = datetime.now(UTC)
            elif status in ["completed", "failed", "cancelled"]:
                values["completed_at"] = datetime.now(UTC)
                
        result = await self.db.execute(
            update(TaskExecution)
            .where(TaskExecution.task_id == task_id)
            .values(**values)
        )
        return result.rowcount > 0

    async def complete_task(
        self,
        task_id: str,
        result: Optional[dict] = None,
        error_message: Optional[str] = None,
        error_details: Optional[dict] = None,
    ) -> bool:
        """Complete a task with result or error."""
        status = "failed" if error_message else "completed"
        
        values = {
            "status": status,
            "completed_at": datetime.now(UTC),
        }
        
        if result:
            values["result"] = result
        if error_message:
            values["error_message"] = error_message
        if error_details:
            values["error_details"] = error_details
            
        result = await self.db.execute(
            update(TaskExecution)
            .where(TaskExecution.task_id == task_id)
            .values(**values)
        )
        return result.rowcount > 0

    async def cancel_task(
        self,
        task_id: str,
        cancelled_by: str,
        cancellation_reason: Optional[str] = None,
    ) -> bool:
        """Cancel a running task."""
        task = await self.get_task_execution(task_id)
        if not task or not task.can_cancel or task.status in ["completed", "failed", "cancelled"]:
            return False
            
        result = await self.db.execute(
            update(TaskExecution)
            .where(TaskExecution.task_id == task_id)
            .values(
                status="cancelled",
                cancelled_by=cancelled_by,
                cancellation_reason=cancellation_reason,
                cancelled_at=datetime.now(UTC),
                completed_at=datetime.now(UTC),
            )
        )
        return result.rowcount > 0

    async def list_session_tasks(
        self, session_id: str, status: Optional[str] = None
    ) -> list[TaskExecution]:
        """List tasks for a session."""
        query = select(TaskExecution).where(TaskExecution.session_id == session_id)
        
        if status:
            query = query.where(TaskExecution.status == status)
            
        query = query.order_by(TaskExecution.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_running_tasks(self) -> list[TaskExecution]:
        """List all currently running tasks."""
        result = await self.db.execute(
            select(TaskExecution).where(TaskExecution.status == "running")
        )
        return list(result.scalars().all())

    # Cleanup Operations
    async def cleanup_expired_sessions(self) -> dict[str, int]:
        """Clean up expired sessions and return counts."""
        now = datetime.now(UTC)
        
        # Close expired MCP sessions
        mcp_result = await self.db.execute(
            update(MCPSession)
            .where(
                and_(
                    MCPSession.is_active == True,
                    MCPSession.expires_at <= now
                )
            )
            .values(
                is_active=False,
                closed_at=now
            )
        )
        
        # Close expired A2A sessions
        a2a_result = await self.db.execute(
            update(A2ASession)
            .where(
                and_(
                    A2ASession.is_active == True,
                    A2ASession.expires_at <= now
                )
            )
            .values(
                is_active=False,
                has_websocket=False,
                closed_at=now
            )
        )
        
        return {
            "mcp_sessions_closed": mcp_result.rowcount,
            "a2a_sessions_closed": a2a_result.rowcount,
        }

    async def cleanup_old_negotiations(self, days_old: int = 7) -> int:
        """Clean up old completed negotiations."""
        cutoff_date = datetime.now(UTC) - timedelta(days=days_old)
        
        result = await self.db.execute(
            select(A2ANegotiation).where(
                and_(
                    A2ANegotiation.status.in_(["completed", "failed"]),
                    A2ANegotiation.completed_at <= cutoff_date
                )
            )
        )
        
        negotiations = result.scalars().all()
        for negotiation in negotiations:
            await self.db.delete(negotiation)
            
        return len(negotiations)

    async def cleanup_old_tasks(self, days_old: int = 30) -> int:
        """Clean up old completed task executions."""
        cutoff_date = datetime.now(UTC) - timedelta(days=days_old)
        
        result = await self.db.execute(
            select(TaskExecution).where(
                and_(
                    TaskExecution.status.in_(["completed", "failed", "cancelled"]),
                    TaskExecution.completed_at <= cutoff_date
                )
            )
        )
        
        tasks = result.scalars().all()
        for task in tasks:
            await self.db.delete(task)
            
        return len(tasks)

    # Helper methods
    async def _task_has_started(self, task_id: str) -> bool:
        """Check if a task has already been marked as started."""
        result = await self.db.execute(
            select(TaskExecution.started_at).where(TaskExecution.task_id == task_id)
        )
        started_at = result.scalar_one_or_none()
        return started_at is not None

    async def get_session_statistics(self) -> dict[str, Any]:
        """Get session statistics."""
        now = datetime.now(UTC)
        
        # Count active MCP sessions
        mcp_count = await self.db.execute(
            select(func.count(MCPSession.id)).where(
                and_(
                    MCPSession.is_active == True,
                    or_(
                        MCPSession.expires_at.is_(None),
                        MCPSession.expires_at > now
                    )
                )
            )
        )
        
        # Count active A2A sessions
        a2a_count = await self.db.execute(
            select(func.count(A2ASession.id)).where(
                and_(
                    A2ASession.is_active == True,
                    A2ASession.expires_at > now
                )
            )
        )
        
        # Count WebSocket connections
        ws_count = await self.db.execute(
            select(func.count(A2ASession.id)).where(
                and_(
                    A2ASession.is_active == True,
                    A2ASession.has_websocket == True,
                    A2ASession.expires_at > now
                )
            )
        )
        
        # Count running tasks
        running_tasks = await self.db.execute(
            select(func.count(TaskExecution.id)).where(
                TaskExecution.status == "running"
            )
        )
        
        return {
            "active_mcp_sessions": mcp_count.scalar(),
            "active_a2a_sessions": a2a_count.scalar(),
            "active_websocket_connections": ws_count.scalar(),
            "running_tasks": running_tasks.scalar(),
        }