"""
Activity and monitoring endpoints for real-time system observability.
"""

from datetime import UTC, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_dependencies import get_current_active_user
from app.database.session import get_db
from app.models.agent import Agent
from app.models.workflow import Workflow, WorkflowExecution
from app.models.session import MCPSession
from app.models.user import User
from app.schemas import BaseResponse
from app.utils.monitoring import health_checker, metrics_collector
import json
import asyncio
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


class ActivityManager:
    """Manages real-time activity broadcasting."""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection for activity monitoring."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info("Activity monitoring connected", user_id=user_id)
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info("Activity monitoring disconnected", user_id=user_id)
    
    async def broadcast_activity(self, activity_data: dict):
        """Broadcast activity to all connected clients."""
        if not self.active_connections:
            return
        
        message = json.dumps(activity_data)
        disconnected = []
        
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning("Failed to send activity update", user_id=user_id, error=str(e))
                disconnected.append(user_id)
        
        # Clean up disconnected clients
        for user_id in disconnected:
            self.disconnect(user_id)


activity_manager = ActivityManager()


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(50, ge=1, le=100, description="Number of activities to return"),
    since: Optional[datetime] = Query(None, description="Get activities since this timestamp"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get recent system activity and events."""
    try:
        # Calculate time filter
        time_filter = since or (datetime.now(UTC) - timedelta(hours=24))
        
        activities = []
        
        # Recent agent creations and updates
        agent_query = (
            select(Agent)
            .where(Agent.updated_at >= time_filter)
            .order_by(desc(Agent.updated_at))
            .limit(limit // 4)
        )
        agent_result = await db.execute(agent_query)
        agents = agent_result.scalars().all()
        
        for agent in agents:
            activities.append({
                "id": f"agent_{agent.id}",
                "type": "agent_update",
                "timestamp": agent.updated_at.isoformat(),
                "title": f"Agent '{agent.name}' updated",
                "description": f"Agent {agent.name} ({agent.role}) was updated",
                "metadata": {
                    "agent_id": str(agent.id),
                    "agent_name": agent.name,
                    "agent_role": agent.role,
                    "status": agent.status,
                },
                "user_id": str(agent.created_by) if agent.created_by else None,
            })
        
        # Recent workflow executions
        workflow_query = (
            select(Workflow)
            .where(Workflow.updated_at >= time_filter)
            .order_by(desc(Workflow.updated_at))
            .limit(limit // 4)
        )
        workflow_result = await db.execute(workflow_query)
        workflows = workflow_result.scalars().all()
        
        for workflow in workflows:
            activities.append({
                "id": f"workflow_{workflow.id}",
                "type": "workflow_update",
                "timestamp": workflow.updated_at.isoformat(),
                "title": f"Workflow '{workflow.name}' updated",
                "description": f"Workflow {workflow.name} status: {workflow.status}",
                "metadata": {
                    "workflow_id": str(workflow.id),
                    "workflow_name": workflow.name,
                    "status": workflow.status,
                    "progress": workflow.progress or 0,
                },
                "user_id": str(workflow.created_by) if workflow.created_by else None,
            })
        
        # Recent MCP sessions
        session_query = (
            select(MCPSession)
            .where(MCPSession.last_activity >= time_filter)
            .order_by(desc(MCPSession.last_activity))
            .limit(limit // 4)
        )
        session_result = await db.execute(session_query)
        sessions = session_result.scalars().all()
        
        for session in sessions:
            activities.append({
                "id": f"session_{session.session_id}",
                "type": "mcp_session",
                "timestamp": session.last_activity.isoformat(),
                "title": f"MCP session activity",
                "description": f"Session {session.client_name} active",
                "metadata": {
                    "session_id": session.session_id,
                    "client_name": session.client_name,
                    "protocol_version": session.protocol_version,
                },
                "user_id": None,  # MCPSession doesn't have user_id
            })
        
        # Sort all activities by timestamp (newest first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply activity type filter if specified
        if activity_type:
            activities = [a for a in activities if a["type"] == activity_type]
        
        # Limit results
        activities = activities[:limit]
        
        return {
            "success": True,
            "data": activities,
            "total": len(activities),
            "since": time_filter.isoformat(),
            "activity_types": ["agent_update", "workflow_update", "mcp_session"]
        }
        
    except Exception as e:
        logger.error("Failed to get activity", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "total": 0
        }


@router.get("/system-status")
async def get_system_status(
    current_user: User = Depends(get_current_active_user),
):
    """Get comprehensive system status and metrics."""
    try:
        # Get health status
        health_status = await health_checker.comprehensive_health_check()
        
        # Get metrics
        metrics = metrics_collector.get_metrics()
        
        # Get system counts
        return {
            "success": True,
            "timestamp": datetime.now(UTC).isoformat(),
            "health": health_status,
            "metrics": metrics,
            "prometheus_available": True,
        }
        
    except Exception as e:
        logger.error("Failed to get system status", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@router.get("/performance")
async def get_performance_metrics(
    timespan: str = Query("1h", description="Time span: 5m, 15m, 1h, 6h, 24h"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get performance metrics for the specified time span."""
    try:
        # Parse timespan
        timespan_mapping = {
            "5m": timedelta(minutes=5),
            "15m": timedelta(minutes=15),
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
        }
        
        if timespan not in timespan_mapping:
            timespan = "1h"
        
        time_filter = datetime.now(UTC) - timespan_mapping[timespan]
        
        # Get agent activity
        agent_count_query = select(func.count(Agent.id)).where(Agent.status == "active")
        agent_count_result = await db.execute(agent_count_query)
        active_agents = agent_count_result.scalar() or 0
        
        # Get workflow activity
        workflow_count_query = select(func.count(Workflow.id)).where(
            Workflow.status.in_(["running", "paused"])
        )
        workflow_count_result = await db.execute(workflow_count_query)
        active_workflows = workflow_count_result.scalar() or 0
        
        # Get recent session activity
        session_count_query = select(func.count(MCPSession.id)).where(
            MCPSession.last_activity >= time_filter
        )
        session_count_result = await db.execute(session_count_query)
        recent_sessions = session_count_result.scalar() or 0
        
        # Update Prometheus metrics
        metrics_collector.set_active_agents(active_agents)
        
        return {
            "success": True,
            "timespan": timespan,
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": {
                "active_agents": active_agents,
                "active_workflows": active_workflows,
                "recent_sessions": recent_sessions,
                "system_health": (await health_checker.comprehensive_health_check())["status"],
            },
            "performance": metrics_collector.get_metrics(),
        }
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@router.websocket("/activity/stream")
async def activity_stream(
    websocket: WebSocket,
    user_id: str = Query(..., description="User ID for authentication"),
):
    """Real-time activity stream via WebSocket."""
    try:
        await activity_manager.connect(websocket, user_id)
        
        # Send initial status
        initial_status = {
            "type": "connection_established",
            "timestamp": datetime.now(UTC).isoformat(),
            "message": "Activity stream connected"
        }
        await websocket.send_text(json.dumps(initial_status))
        
        # Keep connection alive and send periodic updates
        while True:
            await asyncio.sleep(30)  # Send keepalive every 30 seconds
            
            # Send system status update
            try:
                health_status = await health_checker.comprehensive_health_check()
                status_update = {
                    "type": "system_status",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status": health_status["status"],
                    "uptime": health_status["app"]["uptime_seconds"],
                }
                await websocket.send_text(json.dumps(status_update))
            except Exception as e:
                logger.warning("Failed to send status update", error=str(e))
                break
                
    except WebSocketDisconnect:
        activity_manager.disconnect(user_id)
        logger.info("Activity stream disconnected", user_id=user_id)
    except Exception as e:
        logger.error("Activity stream error", error=str(e), user_id=user_id)
        activity_manager.disconnect(user_id)


async def broadcast_activity_update(activity_type: str, data: dict):
    """Helper function to broadcast activity updates to connected clients."""
    activity_data = {
        "type": activity_type,
        "timestamp": datetime.now(UTC).isoformat(),
        "data": data
    }
    await activity_manager.broadcast_activity(activity_data)