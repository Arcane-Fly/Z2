"""
A2A (Agent-to-Agent) Protocol Endpoints

This module implements the A2A protocol for agent-to-agent communication,
including handshake, negotiation, communication, and streaming capabilities.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.utils.logging import get_logger
from app.database.session import get_db
from app.services.session_service import SessionService

logger = get_logger(__name__)
router = APIRouter()


# A2A Protocol Models
class A2AHandshakeRequest(BaseModel):
    """A2A handshake request model."""

    agent_id: str = Field(..., description="Requesting agent ID")
    agent_name: str = Field(..., description="Requesting agent name")
    capabilities: list[str] = Field(..., description="Agent capabilities")
    protocol_version: str = Field(default="1.0.0", description="A2A protocol version")
    public_key: Optional[str] = Field(
        None, description="Agent's public key for encryption"
    )


class A2AHandshakeResponse(BaseModel):
    """A2A handshake response model."""

    session_id: str = Field(..., description="Established session ID")
    agent_id: str = Field(..., description="Our agent ID")
    agent_name: str = Field(..., description="Our agent name")
    capabilities: list[str] = Field(..., description="Our capabilities")
    protocol_version: str = Field(..., description="Supported protocol version")
    expires_at: datetime = Field(..., description="Session expiration time")
    public_key: Optional[str] = Field(None, description="Our public key")


class A2ANegotiationRequest(BaseModel):
    """A2A skill negotiation request model."""

    session_id: str = Field(..., description="Session ID from handshake")
    requested_skills: list[str] = Field(..., description="Skills needed for task")
    task_description: str = Field(..., description="Description of the task")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Task parameters"
    )
    priority: int = Field(default=5, ge=1, le=10, description="Task priority (1-10)")
    timeout_seconds: Optional[int] = Field(None, description="Task timeout")


class A2ANegotiationResponse(BaseModel):
    """A2A skill negotiation response model."""

    negotiation_id: str = Field(..., description="Negotiation ID")
    available_skills: list[str] = Field(..., description="Skills we can provide")
    proposed_workflow: dict[str, Any] = Field(
        ..., description="Proposed execution workflow"
    )
    estimated_duration: int = Field(..., description="Estimated duration in seconds")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost")
    accepted: bool = Field(..., description="Whether we accept the task")


class A2ACommunicationMessage(BaseModel):
    """A2A communication message model."""

    session_id: str = Field(..., description="Session ID")
    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Message ID"
    )
    message_type: str = Field(..., description="Message type")
    payload: dict[str, Any] = Field(..., description="Message payload")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Message timestamp"
    )


class A2AStateUpdate(BaseModel):
    """A2A state update model."""

    session_id: str = Field(..., description="Session ID")
    state: str = Field(..., description="Current state")
    progress: float = Field(ge=0.0, le=1.0, description="Progress percentage")
    metadata: dict[str, Any] = Field(default_factory=dict, description="State metadata")


# WebSocket connection manager
class A2AConnectionManager:
    """Manages WebSocket connections for A2A protocol."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """Remove WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        """Send message to specific session."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
                return True
            except Exception as e:
                logger.error("Failed to send WebSocket message", session_id=session_id, error=str(e))
                self.disconnect(session_id)
                return False
        return False

    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        disconnected = []
        for session_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(session_id)

        # Clean up disconnected sessions
        for session_id in disconnected:
            self.disconnect(session_id)


# Global connection manager
connection_manager = A2AConnectionManager()


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Get session service instance."""
    return SessionService(db)


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.post("/handshake", response_model=A2AHandshakeResponse)
async def a2a_handshake(
    request: A2AHandshakeRequest,
    http_request: Request,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
):
    """
    A2A protocol handshake endpoint.

    Establishes a communication session between agents.
    """
    logger.info(
        "A2A handshake request",
        agent_id=request.agent_id,
        agent_name=request.agent_name,
    )

    # Validate protocol version
    if request.protocol_version != "1.0.0":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported protocol version: {request.protocol_version}",
        )

    # Extract client information
    ip_address, user_agent = get_client_info(http_request)

    # Generate session
    session_id = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    # Our capabilities (from config or registry)
    our_capabilities = [
        "workflow-orchestration",
        "dynamic-reasoning", 
        "code-generation",
        "data-analysis",
        "multi-agent-coordination",
        "streaming-communication",
        "task-cancellation",
        "progress-reporting",
    ]

    # Store session in database
    await session_service.create_a2a_session(
        session_id=session_id,
        agent_id=request.agent_id,
        agent_name=request.agent_name,
        agent_capabilities=request.capabilities,
        protocol_version=request.protocol_version,
        public_key=request.public_key,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    await db.commit()

    response = A2AHandshakeResponse(
        session_id=session_id,
        agent_id=settings.app_name.lower().replace(" ", "-"),
        agent_name=settings.app_name,
        capabilities=our_capabilities,
        protocol_version="1.0.0",
        expires_at=expires_at,
        public_key=None,  # Could implement key exchange here
    )

    logger.info("A2A handshake successful", session_id=session_id)
    return response


@router.post("/negotiate", response_model=A2ANegotiationResponse)
async def a2a_negotiate(
    request: A2ANegotiationRequest,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
):
    """
    A2A skill negotiation endpoint.

    Negotiates task execution between agents.
    """
    logger.info("A2A negotiation request", session_id=request.session_id)

    # Validate session
    session = await session_service.get_a2a_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.is_active or datetime.now(UTC) > session.expires_at:
        raise HTTPException(status_code=401, detail="Session expired")

    # Update session activity
    await session_service.update_a2a_session_activity(request.session_id)

    # Analyze requested skills vs our capabilities
    our_capabilities = [
        "workflow-orchestration",
        "dynamic-reasoning",
        "code-generation",
        "data-analysis",
        "multi-agent-coordination",
    ]

    available_skills = [
        skill for skill in request.requested_skills if skill in our_capabilities
    ]

    # Enhanced skill matching with confidence scoring
    skill_confidence = {}
    for skill in available_skills:
        if skill == "workflow-orchestration":
            skill_confidence[skill] = 0.95
        elif skill == "dynamic-reasoning":
            skill_confidence[skill] = 0.90
        elif skill == "code-generation":
            skill_confidence[skill] = 0.85
        else:
            skill_confidence[skill] = 0.75

    # Decide if we can handle the task
    can_handle = len(available_skills) > 0 and all(
        skill_confidence.get(skill, 0) >= 0.7 for skill in available_skills
    )

    # Generate negotiation ID
    negotiation_id = str(uuid.uuid4())

    # Calculate estimated duration based on task complexity
    base_duration = 300  # 5 minutes default
    complexity_factor = 1.0

    if "workflow-orchestration" in available_skills:
        complexity_factor += 0.5
    if len(available_skills) > 2:
        complexity_factor += 0.3
    if request.priority >= 8:
        complexity_factor += 0.2

    estimated_duration = int(base_duration * complexity_factor)

    # Propose enhanced workflow
    proposed_workflow = {
        "steps": [],
        "agents": [settings.app_name],
        "estimated_duration": estimated_duration,
        "parallel_execution": len(available_skills) > 1,
        "skill_confidence": skill_confidence,
        "fallback_plan": "Use general reasoning if specific skills unavailable",
    }

    # Build workflow steps based on available skills
    if "workflow-orchestration" in available_skills:
        proposed_workflow["steps"].append({
            "step": "orchestrate",
            "agent": settings.app_name,
            "skills": ["workflow-orchestration"],
            "confidence": skill_confidence["workflow-orchestration"],
        })

    if "dynamic-reasoning" in available_skills:
        proposed_workflow["steps"].append({
            "step": "analyze",
            "agent": settings.app_name,
            "skills": ["dynamic-reasoning"],
            "confidence": skill_confidence["dynamic-reasoning"],
        })

    if "code-generation" in available_skills:
        proposed_workflow["steps"].append({
            "step": "generate",
            "agent": settings.app_name,
            "skills": ["code-generation"],
            "confidence": skill_confidence["code-generation"],
        })

    # Store negotiation in database
    await session_service.create_a2a_negotiation(
        negotiation_id=negotiation_id,
        session_id=request.session_id,
        requested_skills=request.requested_skills,
        available_skills=available_skills,
        task_description=request.task_description,
        task_parameters=request.parameters,
        accepted=can_handle,
        proposed_workflow=proposed_workflow,
        estimated_duration=estimated_duration,
        priority=request.priority,
        timeout_seconds=request.timeout_seconds,
    )

    await db.commit()

    response = A2ANegotiationResponse(
        negotiation_id=negotiation_id,
        available_skills=available_skills,
        proposed_workflow=proposed_workflow,
        estimated_duration=estimated_duration,
        cost_estimate=None,  # Could implement cost calculation
        accepted=can_handle,
    )

    logger.info(
        "A2A negotiation completed", 
        negotiation_id=negotiation_id, 
        accepted=can_handle,
        available_skills=available_skills,
    )

    return response


@router.post("/communicate")
async def a2a_communicate(
    message: A2ACommunicationMessage,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
):
    """
    A2A communication endpoint.

    Handles point-to-point messaging between agents.
    """
    logger.info(
        "A2A communication",
        session_id=message.session_id,
        message_type=message.message_type,
    )

    # Validate session
    session = await session_service.get_a2a_session(message.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.is_active or datetime.now(UTC) > session.expires_at:
        raise HTTPException(status_code=401, detail="Session expired")

    # Update session activity
    await session_service.update_a2a_session_activity(message.session_id)

    # Enhanced message processing based on type
    response_payload = {}

    if message.message_type == "task_request":
        task_id = str(uuid.uuid4())
        
        # Create task execution record
        await session_service.create_task_execution(
            task_id=task_id,
            session_id=message.session_id,
            task_type="a2a_task",
            task_name=message.payload.get("task_name", "A2A Task"),
            task_parameters=message.payload,
        )
        
        response_payload = {
            "status": "acknowledged",
            "task_id": task_id,
            "estimated_completion": (
                datetime.now(UTC) + timedelta(minutes=5)
            ).isoformat(),
            "can_cancel": True,
            "progress_endpoint": f"/api/v1/a2a/tasks/{task_id}/progress",
        }

    elif message.message_type == "status_inquiry":
        # Get session statistics
        stats = await session_service.get_session_statistics()
        running_tasks = await session_service.list_session_tasks(
            message.session_id, status="running"
        )
        
        response_payload = {
            "status": "active",
            "current_tasks": len(running_tasks),
            "load_percentage": min(25.0 + len(running_tasks) * 10, 90.0),
            "capabilities_available": True,
            "session_stats": stats,
        }

    elif message.message_type == "result_request":
        task_id = message.payload.get("task_id")
        if task_id:
            task = await session_service.get_task_execution(task_id)
            if task:
                response_payload = {
                    "status": task.status,
                    "progress": float(task.progress),
                    "result": task.result,
                    "error": task.error_message,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                }
            else:
                response_payload = {
                    "status": "not_found",
                    "error": f"Task {task_id} not found",
                }
        else:
            response_payload = {
                "status": "error",
                "error": "task_id required for result_request",
            }

    elif message.message_type == "heartbeat":
        response_payload = {
            "status": "alive",
            "timestamp": datetime.now(UTC).isoformat(),
            "session_active": True,
        }

    elif message.message_type == "capability_inquiry":
        response_payload = {
            "capabilities": [
                "workflow-orchestration",
                "dynamic-reasoning",
                "code-generation", 
                "data-analysis",
                "multi-agent-coordination",
                "streaming-communication",
                "task-cancellation",
                "progress-reporting",
            ],
            "protocol_version": "1.0.0",
            "features": {
                "streaming": True,
                "cancellation": True,
                "progress_tracking": True,
                "websocket_support": True,
            },
        }

    else:
        response_payload = {
            "status": "unsupported_message_type",
            "supported_types": [
                "task_request", 
                "status_inquiry", 
                "result_request", 
                "heartbeat",
                "capability_inquiry",
            ],
        }

    # Send to WebSocket if connected
    websocket_sent = await connection_manager.send_message(
        message.session_id,
        {
            "type": "communication",
            "message": message.model_dump(),
            "response": response_payload,
        }
    )

    await db.commit()

    return {
        "message_id": str(uuid.uuid4()),
        "response_to": message.message_id,
        "status": "processed",
        "payload": response_payload,
        "timestamp": datetime.now(UTC).isoformat(),
        "websocket_delivered": websocket_sent,
    }


@router.websocket("/stream/{session_id}")
async def a2a_stream(
    websocket: WebSocket, 
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
):
    """
    A2A streaming communication via WebSocket.

    Provides real-time bidirectional communication between agents.
    """
    # Validate session exists in database
    try:
        # We need to create a database session for this WebSocket connection
        from app.database.session import SessionLocal
        async with SessionLocal() as db:
            session_srv = SessionService(db)
            session = await session_srv.get_a2a_session(session_id)
            
            if not session:
                await websocket.close(code=4004, reason="Session not found")
                return

            if not session.is_active or datetime.now(UTC) > session.expires_at:
                await websocket.close(code=4001, reason="Session expired")
                return

            # Update session to indicate WebSocket connection
            await session_srv.update_a2a_session_activity(session_id, has_websocket=True)
            await db.commit()

    except Exception as e:
        logger.error("Session validation failed", session_id=session_id, error=str(e))
        await websocket.close(code=4000, reason="Session validation failed")
        return

    # Accept WebSocket connection
    await connection_manager.connect(websocket, session_id)
    logger.info("A2A stream connected", session_id=session_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "agent_id": settings.app_name.lower().replace(" ", "-"),
            "timestamp": datetime.now(UTC).isoformat(),
            "capabilities": [
                "streaming-communication",
                "task-cancellation", 
                "progress-reporting",
                "real-time-updates",
            ],
        })

        while True:
            try:
                data = await websocket.receive_json()
                
                # Process incoming message
                message_type = data.get("type", "unknown")
                logger.info("A2A stream message", session_id=session_id, type=message_type)

                if message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(UTC).isoformat(),
                    })

                elif message_type == "state_update":
                    # Handle state update
                    state = data.get("state", "unknown")
                    progress = data.get("progress", 0.0)
                    
                    await websocket.send_json({
                        "type": "state_acknowledged", 
                        "state": state,
                        "progress": progress,
                        "timestamp": datetime.now(UTC).isoformat(),
                    })

                elif message_type == "task_progress":
                    # Handle progress updates and store in database
                    task_id = data.get("task_id")
                    progress = data.get("progress", 0)
                    
                    if task_id:
                        async with SessionLocal() as db:
                            session_srv = SessionService(db)
                            await session_srv.update_task_progress(task_id, progress)
                            await db.commit()
                    
                    # Echo back progress acknowledgment
                    await websocket.send_json({
                        "type": "progress_acknowledged",
                        "task_id": task_id,
                        "progress": progress,
                        "timestamp": datetime.now(UTC).isoformat(),
                    })

                elif message_type == "subscribe_updates":
                    # Subscribe to specific update types
                    update_types = data.get("update_types", [])
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "update_types": update_types,
                        "timestamp": datetime.now(UTC).isoformat(),
                    })

                elif message_type == "cancel_task":
                    # Handle task cancellation
                    task_id = data.get("task_id")
                    if task_id:
                        async with SessionLocal() as db:
                            session_srv = SessionService(db)
                            success = await session_srv.cancel_task(
                                task_id=task_id,
                                cancelled_by="websocket_client",
                                cancellation_reason="Cancelled via WebSocket",
                            )
                            await db.commit()
                            
                            await websocket.send_json({
                                "type": "cancellation_result",
                                "task_id": task_id,
                                "success": success,
                                "timestamp": datetime.now(UTC).isoformat(),
                            })

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unsupported message type: {message_type}",
                        "supported_types": [
                            "ping", 
                            "state_update", 
                            "task_progress",
                            "subscribe_updates",
                            "cancel_task",
                        ],
                        "timestamp": datetime.now(UTC).isoformat(),
                    })

            except Exception as e:
                logger.error("Error processing WebSocket message", session_id=session_id, error=str(e))
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to process message",
                    "timestamp": datetime.now(UTC).isoformat(),
                })

    except WebSocketDisconnect:
        logger.info("A2A stream disconnected", session_id=session_id)
    except Exception as e:
        logger.error("A2A stream error", session_id=session_id, error=str(e))
    finally:
        # Cleanup
        connection_manager.disconnect(session_id)
        
        # Update session to indicate WebSocket disconnection
        try:
            async with SessionLocal() as db:
                session_srv = SessionService(db)
                await session_srv.update_a2a_session_activity(session_id, has_websocket=False)
                await db.commit()
        except Exception as e:
            logger.error("Failed to update session on disconnect", session_id=session_id, error=str(e))


@router.get("/sessions")
async def list_a2a_sessions(
    session_service: SessionService = Depends(get_session_service),
):
    """List active A2A sessions."""
    sessions = await session_service.list_active_a2a_sessions()
    
    # Clean up expired sessions
    cleanup_results = await session_service.cleanup_expired_sessions()
    
    return {
        "active_sessions": len(sessions),
        "active_streams": len([s for s in sessions if s.has_websocket]),
        "cleanup_results": cleanup_results,
        "sessions": [
            {
                "session_id": session.session_id,
                "agent_id": session.agent_id,
                "agent_name": session.agent_name,
                "capabilities": session.agent_capabilities,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "has_stream": session.has_websocket,
                "protocol_version": session.protocol_version,
            }
            for session in sessions
        ],
    }


@router.delete("/sessions/{session_id}")
async def terminate_a2a_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
):
    """Terminate an A2A session."""
    
    # Close WebSocket if active
    await connection_manager.send_message(
        session_id,
        {
            "type": "session_terminated",
            "reason": "Session terminated by server",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )
    connection_manager.disconnect(session_id)

    # Close session in database
    success = await session_service.close_a2a_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.commit()
    logger.info("A2A session terminated", session_id=session_id)

    return {"status": "terminated", "session_id": session_id}


@router.get("/negotiations/{negotiation_id}")
async def get_negotiation_status(
    negotiation_id: str,
    session_service: SessionService = Depends(get_session_service),
):
    """Get the status of a negotiation."""
    negotiation = await session_service.get_a2a_negotiation(negotiation_id)
    
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")

    return {
        "negotiation_id": negotiation.negotiation_id,
        "session_id": negotiation.session_id,
        "status": negotiation.status,
        "requested_skills": negotiation.requested_skills,
        "available_skills": negotiation.available_skills,
        "accepted": negotiation.accepted,
        "proposed_workflow": negotiation.proposed_workflow,
        "estimated_duration": negotiation.estimated_duration,
        "created_at": negotiation.created_at.isoformat(),
        "updated_at": negotiation.updated_at.isoformat(),
        "completed_at": negotiation.completed_at.isoformat() if negotiation.completed_at else None,
    }


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    session_service: SessionService = Depends(get_session_service),
):
    """Get the status of a task execution."""
    task = await session_service.get_task_execution(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.task_id,
        "session_id": task.session_id,
        "task_type": task.task_type,
        "task_name": task.task_name,
        "status": task.status,
        "progress": float(task.progress),
        "can_cancel": task.can_cancel and task.status == "running",
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "result": task.result,
        "error": task.error_message,
    }


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running task."""
    success = await session_service.cancel_task(
        task_id=task_id,
        cancelled_by="api_request",
        cancellation_reason="Cancelled via API",
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel task - task not found or not cancellable",
        )

    await db.commit()

    return {
        "task_id": task_id,
        "status": "cancelled",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/statistics")
async def get_a2a_statistics(
    session_service: SessionService = Depends(get_session_service),
):
    """Get A2A protocol statistics."""
    stats = await session_service.get_session_statistics()
    running_tasks = await session_service.list_running_tasks()
    
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "protocol_version": "1.0.0",
        "sessions": stats,
        "active_websockets": len(connection_manager.active_connections),
        "running_tasks": len(running_tasks),
        "capabilities": [
            "workflow-orchestration",
            "dynamic-reasoning",
            "code-generation",
            "data-analysis", 
            "multi-agent-coordination",
            "streaming-communication",
            "task-cancellation",
            "progress-reporting",
        ],
        "features": {
            "websocket_streaming": True,
            "task_cancellation": True,
            "progress_tracking": True,
            "session_persistence": True,
            "negotiation_framework": True,
        },
    }
