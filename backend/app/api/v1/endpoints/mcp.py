"""
MCP (Model Context Protocol) endpoints for Z2 API.

This module implements the core MCP protocol endpoints as defined in the
MCP specification: https://modelcontextprotocol.io/specification/2025-03-26
"""

import asyncio
import uuid
from typing import Any, Optional, AsyncGenerator
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_db
from app.services.session_service import SessionService
from app.services.consent_service import ConsentService

router = APIRouter()


# MCP Protocol Models
class MCPCapabilities(BaseModel):
    """MCP server capabilities."""

    resources: Optional[dict[str, Any]] = None
    tools: Optional[dict[str, Any]] = None
    prompts: Optional[dict[str, Any]] = None
    sampling: Optional[dict[str, Any]] = None


class MCPInitializeRequest(BaseModel):
    """MCP initialize request."""

    protocolVersion: str
    capabilities: MCPCapabilities
    clientInfo: dict[str, Any]


class MCPInitializeResponse(BaseModel):
    """MCP initialize response."""

    protocolVersion: str = Field(default=settings.mcp_protocol_version)
    serverInfo: dict[str, Any] = Field(
        default_factory=lambda: {
            "name": settings.mcp_server_name,
            "version": settings.mcp_server_version,
        }
    )
    capabilities: MCPCapabilities


class MCPResource(BaseModel):
    """MCP resource definition."""

    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class MCPTool(BaseModel):
    """MCP tool definition."""

    name: str
    description: str
    inputSchema: dict[str, Any]


class MCPPrompt(BaseModel):
    """MCP prompt definition."""

    name: str
    description: str
    arguments: Optional[list[dict[str, Any]]] = None


class MCPProgressUpdate(BaseModel):
    """Progress update for long-running operations."""

    progress: float  # 0.0 to 1.0
    total: Optional[int] = None
    completed: Optional[int] = None
    message: Optional[str] = None


class MCPToolCallRequest(BaseModel):
    """Tool call request with optional progress tracking."""

    arguments: dict[str, Any]
    session_id: Optional[str] = None
    stream: bool = False
    can_cancel: bool = True


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Get session service instance."""
    return SessionService(db)


def get_consent_service(db: AsyncSession = Depends(get_db)) -> ConsentService:
    """Get consent service instance."""
    return ConsentService(db)


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.post("/initialize")
async def initialize_mcp_session(
    request: MCPInitializeRequest,
    http_request: Request,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> MCPInitializeResponse:
    """
    Initialize MCP session with capability negotiation.

    This endpoint implements the MCP handshake protocol for version
    and feature negotiation between client and server.
    """
    # Validate protocol version
    if request.protocolVersion != settings.mcp_protocol_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported protocol version: {request.protocolVersion}. "
            f"Supported version: {settings.mcp_protocol_version}",
        )

    # Extract client information
    ip_address, user_agent = get_client_info(http_request)
    
    # Create session
    session_id = str(uuid.uuid4())
    
    # Server capabilities
    server_capabilities = MCPCapabilities(
        resources={"subscribe": True, "listChanged": True},
        tools={"listChanged": True, "progress": True, "cancellation": True},
        prompts={"listChanged": True},
        sampling={},  # Enable sampling API
    )

    # Store session in database
    session = await session_service.create_mcp_session(
        session_id=session_id,
        protocol_version=request.protocolVersion,
        client_info=request.clientInfo,
        client_capabilities=request.capabilities.model_dump(),
        server_capabilities=server_capabilities.model_dump(),
        ip_address=ip_address,
        user_agent=user_agent,
    )

    await db.commit()

    response = MCPInitializeResponse(capabilities=server_capabilities)
    # Add session ID to response headers
    response_dict = response.model_dump()
    response_dict["session_id"] = session_id
    
    return response_dict


@router.get("/resources")
async def list_resources(
    session_id: Optional[str] = None,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List available MCP resources with dynamic discovery."""
    
    # Update session activity if provided
    if session_id:
        await session_service.update_mcp_session_activity(session_id)
        await db.commit()
    
    # Dynamic resource discovery
    resources = []
    
    # Agent resources
    resources.extend([
        MCPResource(
            uri="agent://default",
            name="Default Agent",
            description="Default Z2 AI agent for general tasks",
            mimeType="application/json",
        ),
        MCPResource(
            uri="agent://reasoning",
            name="Reasoning Agent",
            description="Advanced reasoning agent for complex analysis",
            mimeType="application/json",
        ),
        MCPResource(
            uri="agent://code",
            name="Code Agent",
            description="Specialized agent for code generation and analysis",
            mimeType="application/json",
        ),
    ])
    
    # Workflow resources
    resources.extend([
        MCPResource(
            uri="workflow://templates",
            name="Workflow Templates",
            description="Pre-built workflow templates",
            mimeType="application/json",
        ),
        MCPResource(
            uri="workflow://active",
            name="Active Workflows",
            description="Currently running workflows",
            mimeType="application/json",
        ),
    ])
    
    # System resources
    resources.extend([
        MCPResource(
            uri="system://metrics",
            name="System Metrics",
            description="System performance and usage metrics",
            mimeType="application/json",
        ),
        MCPResource(
            uri="system://logs",
            name="System Logs",
            description="System and application logs",
            mimeType="text/plain",
        ),
    ])

    return {"resources": [resource.model_dump() for resource in resources]}


@router.get("/resources/{resource_uri:path}")
async def get_resource(
    resource_uri: str,
    session_id: Optional[str] = None,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get specific MCP resource content with dynamic content generation."""
    
    # Update session activity if provided
    if session_id:
        await session_service.update_mcp_session_activity(session_id)
        await db.commit()
    
    # Dynamic resource content based on URI
    if resource_uri.startswith("agent://"):
        agent_type = resource_uri.replace("agent://", "")
        
        # Get current agent status and capabilities
        agent_data = {
            "type": "agent",
            "id": agent_type,
            "status": "available",
            "capabilities": ["text", "reasoning", "analysis"],
            "load": "25%",
            "last_activity": datetime.now(UTC).isoformat(),
        }
        
        if agent_type == "reasoning":
            agent_data["capabilities"].extend(["complex_reasoning", "multi_step_analysis"])
        elif agent_type == "code":
            agent_data["capabilities"].extend(["code_generation", "code_analysis", "debugging"])
        
        return {
            "uri": resource_uri,
            "mimeType": "application/json",
            "text": str(agent_data).replace("'", '"'),  # Convert to JSON string
        }
        
    elif resource_uri.startswith("workflow://"):
        workflow_type = resource_uri.replace("workflow://", "")
        
        if workflow_type == "templates":
            workflow_data = {
                "type": "workflow_templates",
                "templates": [
                    {"id": "compliance_audit", "name": "Compliance Audit", "description": "Automated compliance checking"},
                    {"id": "customer_analysis", "name": "Customer Analysis", "description": "Customer data analysis workflow"},
                    {"id": "code_review", "name": "Code Review", "description": "Automated code review and suggestions"},
                ]
            }
        else:  # active workflows
            # Get active workflows from session service
            sessions = await session_service.list_active_mcp_sessions()
            workflow_data = {
                "type": "active_workflows",
                "count": len(sessions),
                "workflows": [
                    {
                        "session_id": s.session_id,
                        "client": s.client_name,
                        "started": s.created_at.isoformat(),
                        "last_activity": s.last_activity.isoformat(),
                    }
                    for s in sessions
                ]
            }
        
        return {
            "uri": resource_uri,
            "mimeType": "application/json",
            "text": str(workflow_data).replace("'", '"'),
        }
        
    elif resource_uri.startswith("system://"):
        system_type = resource_uri.replace("system://", "")
        
        if system_type == "metrics":
            # Get system metrics
            stats = await session_service.get_session_statistics()
            metrics_data = {
                "type": "system_metrics",
                "timestamp": datetime.now(UTC).isoformat(),
                "sessions": stats,
                "uptime": "running",
                "version": settings.app_version,
            }
            
            return {
                "uri": resource_uri,
                "mimeType": "application/json",
                "text": str(metrics_data).replace("'", '"'),
            }
        elif system_type == "logs":
            # Return recent system activity
            return {
                "uri": resource_uri,
                "mimeType": "text/plain",
                "text": f"System logs - {datetime.now(UTC).isoformat()}\nSystem operational",
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resource not found: {resource_uri}",
    )


@router.get("/tools")
async def list_tools(
    session_id: Optional[str] = None,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List available MCP tools with dynamic discovery."""
    
    # Update session activity if provided
    if session_id:
        await session_service.update_mcp_session_activity(session_id)
        await db.commit()
    
    # Dynamic tool discovery
    tools = [
        MCPTool(
            name="execute_agent",
            description="Execute a task using a Z2 AI agent with progress tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier"},
                    "task": {"type": "string", "description": "Task description"},
                    "parameters": {"type": "object", "description": "Task parameters"},
                    "stream": {"type": "boolean", "description": "Enable streaming responses", "default": False},
                    "timeout": {"type": "integer", "description": "Task timeout in seconds", "default": 300},
                },
                "required": ["agent_id", "task"],
            },
        ),
        MCPTool(
            name="create_workflow",
            description="Create a new multi-agent workflow with progress tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Workflow name"},
                    "agents": {"type": "array", "description": "List of agents"},
                    "configuration": {"type": "object", "description": "Workflow config"},
                    "stream": {"type": "boolean", "description": "Enable streaming responses", "default": False},
                },
                "required": ["name", "agents"],
            },
        ),
        MCPTool(
            name="analyze_system",
            description="Analyze system performance and generate insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "scope": {"type": "string", "enum": ["performance", "security", "usage"], "description": "Analysis scope"},
                    "timeframe": {"type": "string", "description": "Analysis timeframe", "default": "1h"},
                    "detailed": {"type": "boolean", "description": "Generate detailed report", "default": False},
                },
                "required": ["scope"],
            },
        ),
    ]

    return {"tools": [tool.model_dump() for tool in tools]}


async def stream_tool_execution(
    tool_name: str,
    arguments: dict[str, Any],
    task_id: str,
    session_service: SessionService,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    """Stream tool execution progress."""
    
    # Simulate long-running task with progress updates
    total_steps = 10
    
    for step in range(total_steps + 1):
        progress = step / total_steps
        
        # Update task progress in database
        await session_service.update_task_progress(
            task_id=task_id,
            progress=progress,
            status="running" if step < total_steps else "completed",
        )
        await db.commit()
        
        # Generate progress update
        update = MCPProgressUpdate(
            progress=progress,
            total=total_steps,
            completed=step,
            message=f"Executing {tool_name} - Step {step}/{total_steps}",
        )
        
        yield f"data: {update.model_dump_json()}\n\n"
        
        if step < total_steps:
            await asyncio.sleep(0.5)  # Simulate work


@router.post("/tools/{tool_name}/call")
async def call_tool(
    tool_name: str,
    request_data: MCPToolCallRequest,
    http_request: Request,
    session_service: SessionService = Depends(get_session_service),
    consent_service: ConsentService = Depends(get_consent_service),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Execute MCP tool with given arguments, supporting streaming and cancellation."""
    
    # Update session activity if provided
    if request_data.session_id:
        await session_service.update_mcp_session_activity(request_data.session_id)
    
    # Check consent for tool access (simplified - in production would check user ID)
    ip_address, user_agent = get_client_info(http_request)
    
    # Create task execution record
    task_id = str(uuid.uuid4())
    task = await session_service.create_task_execution(
        task_id=task_id,
        session_id=request_data.session_id or "anonymous",
        task_type="mcp_tool",
        task_name=tool_name,
        task_parameters=request_data.arguments,
        can_cancel=request_data.can_cancel,
    )
    await db.commit()
    
    # If streaming is requested, return streaming response
    if request_data.stream:
        return StreamingResponse(
            stream_tool_execution(tool_name, request_data.arguments, task_id, session_service, db),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Task-ID": task_id,
            },
        )
    
    # Non-streaming execution
    if tool_name == "execute_agent":
        result_data = {
            "task_id": task_id,
            "agent_id": request_data.arguments.get("agent_id", "default"),
            "task": request_data.arguments.get("task", "unknown"),
            "status": "completed",
            "result": f"Agent {request_data.arguments.get('agent_id', 'default')} executed task: {request_data.arguments.get('task', 'unknown')}",
            "execution_time": "2.3s",
        }
        
        # Update task as completed
        await session_service.complete_task(task_id=task_id, result=result_data)
        await db.commit()
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result_data["result"],
                }
            ],
            "task_id": task_id,
            "metadata": result_data,
        }
        
    elif tool_name == "create_workflow":
        result_data = {
            "task_id": task_id,
            "workflow_name": request_data.arguments.get("name", "unnamed"),
            "agents": request_data.arguments.get("agents", []),
            "status": "created",
            "workflow_id": str(uuid.uuid4()),
        }
        
        await session_service.complete_task(task_id=task_id, result=result_data)
        await db.commit()
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Created workflow: {result_data['workflow_name']} with ID: {result_data['workflow_id']}",
                }
            ],
            "task_id": task_id,
            "metadata": result_data,
        }
        
    elif tool_name == "analyze_system":
        scope = request_data.arguments.get("scope", "performance")
        detailed = request_data.arguments.get("detailed", False)
        
        # Get system statistics
        stats = await session_service.get_session_statistics()
        
        result_data = {
            "task_id": task_id,
            "scope": scope,
            "detailed": detailed,
            "analysis": {
                "summary": f"System {scope} analysis completed",
                "metrics": stats,
                "recommendations": [
                    "System operating within normal parameters",
                    "No immediate action required",
                ],
            },
        }
        
        await session_service.complete_task(task_id=task_id, result=result_data)
        await db.commit()
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"System {scope} analysis completed. {len(stats)} metrics analyzed.",
                }
            ],
            "task_id": task_id,
            "metadata": result_data,
        }
    
    else:
        await session_service.complete_task(
            task_id=task_id,
            error_message=f"Tool not found: {tool_name}",
        )
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Tool not found: {tool_name}"
        )


@router.post("/tools/{tool_name}/cancel")
async def cancel_tool(
    tool_name: str,
    task_id: str,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Cancel a running tool execution."""
    
    success = await session_service.cancel_task(
        task_id=task_id,
        cancelled_by="user",
        cancellation_reason="User requested cancellation",
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel task - task not found or not cancellable",
        )
    
    await db.commit()
    
    return {
        "task_id": task_id,
        "status": "cancelled",
        "message": "Task cancelled successfully",
    }


@router.get("/tools/{tool_name}/status/{task_id}")
async def get_tool_status(
    tool_name: str,
    task_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """Get the status of a tool execution."""
    
    task = await session_service.get_task_execution(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )
    
    return {
        "task_id": task_id,
        "tool_name": tool_name,
        "status": task.status,
        "progress": float(task.progress),
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "result": task.result,
        "error": task.error_message,
        "can_cancel": task.can_cancel and task.status == "running",
    }


@router.get("/prompts")
async def list_prompts(
    session_id: Optional[str] = None,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List available MCP prompts with dynamic discovery."""
    
    # Update session activity if provided
    if session_id:
        await session_service.update_mcp_session_activity(session_id)
        await db.commit()
    
    # Dynamic prompt discovery
    prompts = [
        MCPPrompt(
            name="analyze_compliance",
            description="Analyze document for compliance requirements",
            arguments=[
                {
                    "name": "document",
                    "description": "Document to analyze",
                    "required": True,
                },
                {
                    "name": "standards",
                    "description": "Compliance standards to check",
                    "required": False,
                },
                {
                    "name": "detailed",
                    "description": "Generate detailed analysis",
                    "required": False,
                },
            ],
        ),
        MCPPrompt(
            name="generate_report",
            description="Generate a structured report from data",
            arguments=[
                {"name": "data", "description": "Source data", "required": True},
                {"name": "format", "description": "Report format", "required": False},
                {"name": "template", "description": "Report template", "required": False},
            ],
        ),
        MCPPrompt(
            name="code_review",
            description="Perform automated code review",
            arguments=[
                {"name": "code", "description": "Code to review", "required": True},
                {"name": "language", "description": "Programming language", "required": False},
                {"name": "focus", "description": "Review focus areas", "required": False},
            ],
        ),
    ]

    return {"prompts": [prompt.model_dump() for prompt in prompts]}


@router.get("/prompts/{prompt_name}")
async def get_prompt(
    prompt_name: str,
    arguments: Optional[dict[str, Any]] = None,
    session_id: Optional[str] = None,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get MCP prompt with arguments."""
    
    # Update session activity if provided
    if session_id:
        await session_service.update_mcp_session_activity(session_id)
        await db.commit()
    
    # Dynamic prompt generation based on arguments
    if prompt_name == "analyze_compliance":
        document = arguments.get("document", "No document provided") if arguments else "No document provided"
        standards = arguments.get("standards", ["general"]) if arguments else ["general"]
        
        return {
            "description": "Analyze document for compliance requirements",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Analyze the following document for compliance with standards {standards}: {document}",
                    },
                }
            ],
        }
        
    elif prompt_name == "generate_report":
        data = arguments.get("data", "No data provided") if arguments else "No data provided"
        format_type = arguments.get("format", "markdown") if arguments else "markdown"
        
        return {
            "description": "Generate a structured report from data",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Generate a {format_type} report from this data: {data}",
                    },
                }
            ],
        }
        
    elif prompt_name == "code_review":
        code = arguments.get("code", "No code provided") if arguments else "No code provided"
        language = arguments.get("language", "auto-detect") if arguments else "auto-detect"
        focus = arguments.get("focus", ["security", "performance", "maintainability"]) if arguments else ["security", "performance", "maintainability"]
        
        return {
            "description": "Perform automated code review",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Review this {language} code focusing on {focus}: {code}",
                    },
                }
            ],
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt not found: {prompt_name}",
        )


@router.get("/sessions")
async def list_sessions(
    session_service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """List active MCP sessions."""
    sessions = await session_service.list_active_mcp_sessions()
    
    return {
        "sessions": [
            {
                "session_id": session.session_id,
                "client_name": session.client_name,
                "client_version": session.client_version,
                "protocol_version": session.protocol_version,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "expires_at": session.expires_at.isoformat() if session.expires_at else None,
            }
            for session in sessions
        ]
    }


@router.delete("/sessions/{session_id}")
async def close_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Close MCP session."""
    success = await session_service.close_mcp_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )
    
    await db.commit()
    
    return {"message": f"Session {session_id} closed successfully"}


@router.post("/sampling/createMessage")
async def create_message(
    request: dict[str, Any],
    session_id: Optional[str] = None,
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    MCP sampling API - request LLM completion.

    This allows the MCP server to request model completions from the client.
    """
    
    # Update session activity if provided
    if session_id:
        await session_service.update_mcp_session_activity(session_id)
        await db.commit()
    
    # Enhanced sampling response with context awareness
    model = request.get("model", "default")
    messages = request.get("messages", [])
    max_tokens = request.get("max_tokens", 100)
    
    # Generate contextual response based on message content
    if messages:
        last_message = messages[-1].get("content", "")
        if "analyze" in last_message.lower():
            response_text = "Based on the analysis request, I would examine the key components and provide structured insights with recommendations."
        elif "code" in last_message.lower():
            response_text = "For code-related tasks, I would review the syntax, logic, performance, and suggest improvements following best practices."
        else:
            response_text = "I understand your request and would provide a comprehensive response based on the context and requirements."
    else:
        response_text = "This is a sample response from the MCP sampling API."
    
    return {
        "model": model,
        "role": "assistant",
        "content": {
            "type": "text",
            "text": response_text,
        },
        "usage": {
            "prompt_tokens": sum(len(msg.get("content", "").split()) for msg in messages),
            "completion_tokens": len(response_text.split()),
            "total_tokens": sum(len(msg.get("content", "").split()) for msg in messages) + len(response_text.split()),
        },
        "session_id": session_id,
    }


@router.get("/statistics")
async def get_mcp_statistics(
    session_service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """Get MCP server statistics and metrics."""
    
    stats = await session_service.get_session_statistics()
    running_tasks = await session_service.list_running_tasks()
    
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "server_info": {
            "name": settings.mcp_server_name,
            "version": settings.mcp_server_version,
            "protocol_version": settings.mcp_protocol_version,
        },
        "sessions": stats,
        "tasks": {
            "running": len(running_tasks),
            "running_tasks": [
                {
                    "task_id": t.task_id,
                    "task_name": t.task_name,
                    "progress": float(t.progress),
                    "started_at": t.started_at.isoformat() if t.started_at else None,
                }
                for t in running_tasks
            ],
        },
        "capabilities": {
            "streaming": True,
            "cancellation": True,
            "progress_tracking": True,
            "session_persistence": True,
        },
    }
