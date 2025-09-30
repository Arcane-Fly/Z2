"""
Memory Graph API endpoints.

Provides RESTful API for memory graph operations including:
- Graph ingestion (text -> entities/relations)
- Graph queries (planning and reasoning)
- Graph persistence (sessions)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import structlog

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.auth_dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.agents.memory_graph import MemoryGraph
from app.agents.ingestor_agent import IngestorAgent
from app.agents.planner_agent import PlannerAgent
from app.services.memory_graph_service import MemoryGraphService

logger = structlog.get_logger(__name__)
router = APIRouter()


# Pydantic schemas for API
class IngestRequest(BaseModel):
    text: str
    source_info: Optional[Dict[str, Any]] = None
    session_id: Optional[UUID] = None


class IngestResponse(BaseModel):
    nodes_created: int
    edges_created: int
    services: List[str]
    envvars: List[str]
    incidents: List[str]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class QueryRequest(BaseModel):
    query: str
    query_type: Optional[str] = "auto"
    session_id: Optional[UUID] = None


class QueryResponse(BaseModel):
    query: str
    query_type: str
    service_name: Optional[str]
    answer: str
    evidence: List[Dict[str, Any]]
    graph_operations: List[str]


class SessionCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class SessionResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    stats: Dict[str, Any]
    created_at: str
    updated_at: str


class GraphExportResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@router.post("/ingest", response_model=IngestResponse)
async def ingest_text(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Ingest text and extract entities/relationships into the memory graph.
    
    This endpoint implements the "Ingestor" agent functionality.
    """
    try:
        # Load existing graph if session provided
        graph_service = MemoryGraphService(db)
        
        if request.session_id:
            graph = await graph_service.load_graph(
                session_id=request.session_id,
                user_id=current_user.id
            )
        else:
            graph = MemoryGraph()
        
        # Run ingestion
        ingestor = IngestorAgent(graph)
        result = ingestor.ingest(request.text, request.source_info)
        
        # Save back to database
        await graph_service.save_graph(
            graph=graph,
            session_id=request.session_id,
            user_id=current_user.id
        )
        
        logger.info(
            "Text ingestion completed",
            user_id=current_user.id,
            session_id=request.session_id,
            nodes_created=result["nodes_created"],
            edges_created=result["edges_created"]
        )
        
        return IngestResponse(**result)
        
    except Exception as e:
        logger.error("Error during text ingestion", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query_graph(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Query the memory graph for planning and reasoning.
    
    This endpoint implements the "Planner" agent functionality.
    """
    try:
        # Load graph
        graph_service = MemoryGraphService(db)
        
        if request.session_id:
            graph = await graph_service.load_graph(
                session_id=request.session_id,
                user_id=current_user.id
            )
        else:
            graph = await graph_service.load_graph(user_id=current_user.id)
        
        # Run query
        planner = PlannerAgent(graph)
        result = planner.answer_query(request.query, request.query_type)
        
        logger.info(
            "Graph query completed",
            user_id=current_user.id,
            session_id=request.session_id,
            query_type=result["query_type"],
            evidence_count=len(result["evidence"])
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error("Error during graph query", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new memory graph session."""
    try:
        graph_service = MemoryGraphService(db)
        
        session = await graph_service.create_session(
            name=request.name,
            description=request.description,
            user_id=current_user.id
        )
        
        return SessionResponse(
            id=session.id,
            name=session.name,
            description=session.description,
            stats=session.stats or {},
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error("Error creating session", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session creation failed: {str(e)}"
        )


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all memory graph sessions for the current user."""
    try:
        graph_service = MemoryGraphService(db)
        sessions = await graph_service.get_sessions(current_user.id)
        
        return [
            SessionResponse(
                id=session.id,
                name=session.name,
                description=session.description,
                stats=session.stats or {},
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat()
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error("Error listing sessions", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a memory graph session."""
    try:
        graph_service = MemoryGraphService(db)
        
        deleted = await graph_service.delete_session(session_id, current_user.id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or access denied"
            )
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting session", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/sessions/{session_id}/export", response_model=GraphExportResponse)
async def export_graph(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export a memory graph as JSON."""
    try:
        graph_service = MemoryGraphService(db)
        
        graph = await graph_service.load_graph(
            session_id=session_id,
            user_id=current_user.id
        )
        
        graph_data = graph.to_dict()
        
        return GraphExportResponse(
            nodes=graph_data["nodes"],
            edges=graph_data["edges"],
            metadata={
                "session_id": str(session_id),
                "node_count": len(graph_data["nodes"]),
                "edge_count": len(graph_data["edges"]),
                "exported_by": str(current_user.id)
            }
        )
        
    except Exception as e:
        logger.error("Error exporting graph", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export graph: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for memory graph API."""
    return {
        "status": "healthy",
        "service": "memory_graph",
        "features": [
            "text_ingestion",
            "graph_querying",
            "session_management",
            "graph_export"
        ]
    }