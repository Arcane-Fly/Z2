"""
A2A (Agent-to-Agent) Protocol Endpoints

This module implements the A2A protocol for agent-to-agent communication,
including handshake, negotiation, communication, and streaming capabilities.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.core.config import settings
from app.utils.logging import get_logger

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


# In-memory session storage (in production, use Redis or database)
active_sessions: dict[str, dict[str, Any]] = {}
active_negotiations: dict[str, dict[str, Any]] = {}
active_websockets: dict[str, WebSocket] = {}


@router.post("/handshake", response_model=A2AHandshakeResponse)
async def a2a_handshake(request: A2AHandshakeRequest):
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

    # Generate session
    session_id = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    # Store session
    active_sessions[session_id] = {
        "agent_id": request.agent_id,
        "agent_name": request.agent_name,
        "capabilities": request.capabilities,
        "created_at": datetime.now(UTC),
        "expires_at": expires_at,
        "active": True,
    }

    # Our capabilities (from config or registry)
    our_capabilities = [
        "workflow-orchestration",
        "dynamic-reasoning",
        "code-generation",
        "data-analysis",
        "multi-agent-coordination",
    ]

    response = A2AHandshakeResponse(
        session_id=session_id,
        agent_id=settings.app_name.lower().replace(" ", "-"),
        agent_name=settings.app_name,
        capabilities=our_capabilities,
        protocol_version="1.0.0",
        expires_at=expires_at,
    )

    logger.info("A2A handshake successful", session_id=session_id)
    return response


@router.post("/negotiate", response_model=A2ANegotiationResponse)
async def a2a_negotiate(request: A2ANegotiationRequest):
    """
    A2A skill negotiation endpoint.

    Negotiates task execution between agents.
    """
    logger.info("A2A negotiation request", session_id=request.session_id)

    # Validate session
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[request.session_id]
    if not session["active"] or datetime.now(UTC) > session["expires_at"]:
        raise HTTPException(status_code=401, detail="Session expired")

    # Analyze requested skills vs our capabilities
    our_capabilities = [
        "workflow-orchestration",
        "dynamic-reasoning",
        "code-generation",
        "data-analysis",
    ]

    available_skills = [
        skill for skill in request.requested_skills if skill in our_capabilities
    ]

    # Decide if we can handle the task
    can_handle = len(available_skills) > 0

    # Generate negotiation ID
    negotiation_id = str(uuid.uuid4())

    # Store negotiation
    active_negotiations[negotiation_id] = {
        "session_id": request.session_id,
        "requested_skills": request.requested_skills,
        "available_skills": available_skills,
        "task_description": request.task_description,
        "parameters": request.parameters,
        "accepted": can_handle,
        "created_at": datetime.now(UTC),
    }

    # Propose workflow
    proposed_workflow = {
        "steps": [],
        "agents": [settings.app_name],
        "estimated_duration": 300,  # 5 minutes default
        "parallel_execution": False,
    }

    if "workflow-orchestration" in available_skills:
        proposed_workflow["steps"].append(
            {
                "step": "orchestrate",
                "agent": settings.app_name,
                "skills": ["workflow-orchestration"],
            }
        )

    if "dynamic-reasoning" in available_skills:
        proposed_workflow["steps"].append(
            {
                "step": "analyze",
                "agent": settings.app_name,
                "skills": ["dynamic-reasoning"],
            }
        )

    response = A2ANegotiationResponse(
        negotiation_id=negotiation_id,
        available_skills=available_skills,
        proposed_workflow=proposed_workflow,
        estimated_duration=proposed_workflow["estimated_duration"],
        accepted=can_handle,
    )

    logger.info(
        "A2A negotiation completed", negotiation_id=negotiation_id, accepted=can_handle
    )

    return response


@router.post("/communicate")
async def a2a_communicate(message: A2ACommunicationMessage):
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
    if message.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[message.session_id]
    if not session["active"] or datetime.now(UTC) > session["expires_at"]:
        raise HTTPException(status_code=401, detail="Session expired")

    # Process message based on type
    response_payload = {}

    if message.message_type == "task_request":
        response_payload = {
            "status": "acknowledged",
            "task_id": str(uuid.uuid4()),
            "estimated_completion": (
                datetime.now(UTC) + timedelta(minutes=5)
            ).isoformat(),
        }

    elif message.message_type == "status_inquiry":
        response_payload = {
            "status": "active",
            "current_tasks": [],
            "load_percentage": 25.0,
        }

    elif message.message_type == "result_request":
        response_payload = {
            "status": "completed",
            "result": "Task completed successfully",
            "output_data": {},
        }

    else:
        response_payload = {
            "status": "unsupported_message_type",
            "supported_types": ["task_request", "status_inquiry", "result_request"],
        }

    # Send to WebSocket if connected
    if message.session_id in active_websockets:
        try:
            await active_websockets[message.session_id].send_json(
                {
                    "type": "communication",
                    "message": message.dict(),
                    "response": response_payload,
                }
            )
        except Exception as e:
            logger.error("Failed to send WebSocket message", error=str(e))

    return {
        "message_id": str(uuid.uuid4()),
        "response_to": message.message_id,
        "status": "processed",
        "payload": response_payload,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.websocket("/stream/{session_id}")
async def a2a_stream(websocket: WebSocket, session_id: str):
    """
    A2A streaming communication via WebSocket.

    Provides real-time bidirectional communication between agents.
    """
    # Validate session
    if session_id not in active_sessions:
        await websocket.close(code=4004, reason="Session not found")
        return

    session = active_sessions[session_id]
    if not session["active"] or datetime.now(UTC) > session["expires_at"]:
        await websocket.close(code=4001, reason="Session expired")
        return

    await websocket.accept()
    active_websockets[session_id] = websocket

    logger.info("A2A stream connected", session_id=session_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connection_established",
                "session_id": session_id,
                "agent_id": settings.app_name.lower().replace(" ", "-"),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        while True:
            data = await websocket.receive_json()

            # Process incoming message
            message_type = data.get("type", "unknown")
            logger.info("A2A stream message", session_id=session_id, type=message_type)

            if message_type == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now(UTC).isoformat()}
                )

            elif message_type == "state_update":
                # Handle state update
                await websocket.send_json(
                    {
                        "type": "state_acknowledged",
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )

            elif message_type == "task_progress":
                # Echo back progress updates
                await websocket.send_json(
                    {
                        "type": "progress_acknowledged",
                        "progress": data.get("progress", 0),
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )

            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unsupported message type: {message_type}",
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )

    except WebSocketDisconnect:
        logger.info("A2A stream disconnected", session_id=session_id)
    except Exception as e:
        logger.error("A2A stream error", session_id=session_id, error=str(e))
    finally:
        # Cleanup
        if session_id in active_websockets:
            del active_websockets[session_id]


@router.get("/sessions")
async def list_a2a_sessions():
    """List active A2A sessions."""
    current_time = datetime.now(UTC)

    # Clean up expired sessions
    expired_sessions = [
        sid
        for sid, session in active_sessions.items()
        if current_time > session["expires_at"]
    ]

    for sid in expired_sessions:
        del active_sessions[sid]
        if sid in active_websockets:
            del active_websockets[sid]

    return {
        "active_sessions": len(active_sessions),
        "active_streams": len(active_websockets),
        "sessions": [
            {
                "session_id": sid,
                "agent_id": session["agent_id"],
                "agent_name": session["agent_name"],
                "created_at": session["created_at"].isoformat(),
                "expires_at": session["expires_at"].isoformat(),
                "has_stream": sid in active_websockets,
            }
            for sid, session in active_sessions.items()
        ],
    }


@router.delete("/sessions/{session_id}")
async def terminate_a2a_session(session_id: str):
    """Terminate an A2A session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Close WebSocket if active
    if session_id in active_websockets:
        try:
            await active_websockets[session_id].close()
        except Exception:
            pass
        del active_websockets[session_id]

    # Remove session
    del active_sessions[session_id]

    # Remove associated negotiations
    expired_negotiations = [
        nid
        for nid, negotiation in active_negotiations.items()
        if negotiation["session_id"] == session_id
    ]
    for nid in expired_negotiations:
        del active_negotiations[nid]

    logger.info("A2A session terminated", session_id=session_id)

    return {"status": "terminated", "session_id": session_id}
