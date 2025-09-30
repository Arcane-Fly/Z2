"""
Memory Graph Service - Database persistence layer.

Handles loading and saving memory graphs to/from the database,
bridging the in-memory graph structure with persistent storage.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import structlog

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.memory_graph import MemoryGraph, Node, Edge
from app.models.memory_graph import MemoryGraphNode, MemoryGraphEdge, MemoryGraphSession

logger = structlog.get_logger(__name__)


class MemoryGraphService:
    """Service for persistent memory graph operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(
        self, 
        name: str, 
        description: str = None,
        user_id: UUID = None,
        config: Dict[str, Any] = None
    ) -> MemoryGraphSession:
        """Create a new memory graph session."""
        session = MemoryGraphSession(
            name=name,
            description=description,
            config=config or {},
            created_by=user_id
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info("Created memory graph session", session_id=session.id, name=name)
        return session
    
    async def save_graph(
        self, 
        graph: MemoryGraph, 
        session_id: Optional[UUID] = None,
        user_id: UUID = None,
        clear_existing: bool = False
    ) -> Dict[str, int]:
        """Save an in-memory graph to the database."""
        
        if clear_existing and session_id:
            await self._clear_session_data(session_id)
        
        nodes_saved = 0
        edges_saved = 0
        
        # Save nodes
        for node in graph.nodes.values():
            db_node = await self._upsert_node(node, session_id, user_id)
            if db_node:
                nodes_saved += 1
        
        # Save edges
        for edge in graph.edges:
            db_edge = await self._upsert_edge(edge, session_id, user_id)
            if db_edge:
                edges_saved += 1
        
        await self.db.commit()
        
        # Update session stats if provided
        if session_id:
            await self._update_session_stats(session_id, nodes_saved, edges_saved)
        
        logger.info(
            "Saved memory graph", 
            session_id=session_id,
            nodes_saved=nodes_saved, 
            edges_saved=edges_saved
        )
        
        return {"nodes_saved": nodes_saved, "edges_saved": edges_saved}
    
    async def load_graph(
        self, 
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        node_types: Optional[List[str]] = None
    ) -> MemoryGraph:
        """Load a memory graph from the database."""
        graph = MemoryGraph()
        
        # Build node query
        node_query = select(MemoryGraphNode)
        
        if user_id:
            node_query = node_query.where(MemoryGraphNode.created_by == user_id)
        
        if node_types:
            node_query = node_query.where(MemoryGraphNode.node_type.in_(node_types))
        
        # Load nodes
        result = await self.db.execute(node_query)
        db_nodes = result.scalars().all()
        
        for db_node in db_nodes:
            node = Node(
                id=db_node.node_id,
                type=db_node.node_type,
                props=db_node.props or {}
            )
            graph.upsert_node(node)
        
        # Build edge query
        edge_query = select(MemoryGraphEdge)
        
        if user_id:
            edge_query = edge_query.where(MemoryGraphEdge.created_by == user_id)
        
        # Load edges (only for nodes we have)
        node_ids = set(graph.nodes.keys())
        if node_ids:
            edge_query = edge_query.where(
                and_(
                    MemoryGraphEdge.from_node_id.in_(node_ids),
                    MemoryGraphEdge.to_node_id.in_(node_ids)
                )
            )
            
            result = await self.db.execute(edge_query)
            db_edges = result.scalars().all()
            
            for db_edge in db_edges:
                try:
                    edge = Edge(
                        type=db_edge.edge_type,
                        from_id=db_edge.from_node_id,
                        to_id=db_edge.to_node_id,
                        props=db_edge.props or {}
                    )
                    graph.add_edge(edge)
                except ValueError as e:
                    logger.warning("Skipped invalid edge during load", error=str(e))
        
        logger.info(
            "Loaded memory graph",
            session_id=session_id,
            nodes_loaded=len(graph.nodes),
            edges_loaded=len(graph.edges)
        )
        
        return graph
    
    async def get_sessions(self, user_id: UUID) -> List[MemoryGraphSession]:
        """Get all memory graph sessions for a user."""
        query = select(MemoryGraphSession).where(
            MemoryGraphSession.created_by == user_id
        ).order_by(MemoryGraphSession.updated_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Delete a memory graph session and all its data."""
        
        # Verify ownership
        session_query = select(MemoryGraphSession).where(
            and_(
                MemoryGraphSession.id == session_id,
                MemoryGraphSession.created_by == user_id
            )
        )
        result = await self.db.execute(session_query)
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        # Clear session data
        await self._clear_session_data(session_id)
        
        # Delete session
        await self.db.delete(session)
        await self.db.commit()
        
        logger.info("Deleted memory graph session", session_id=session_id)
        return True
    
    async def _upsert_node(
        self, 
        node: Node, 
        session_id: Optional[UUID],
        user_id: UUID
    ) -> Optional[MemoryGraphNode]:
        """Insert or update a node in the database."""
        
        # Check if node exists
        query = select(MemoryGraphNode).where(MemoryGraphNode.node_id == node.id)
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing node
            existing.props = node.props
            existing.node_type = node.type
            db_node = existing
        else:
            # Create new node
            db_node = MemoryGraphNode(
                node_id=node.id,
                node_type=node.type,
                props=node.props,
                created_by=user_id
            )
            self.db.add(db_node)
        
        return db_node
    
    async def _upsert_edge(
        self, 
        edge: Edge, 
        session_id: Optional[UUID],
        user_id: UUID
    ) -> Optional[MemoryGraphEdge]:
        """Insert or update an edge in the database."""
        
        # Check if edge exists
        query = select(MemoryGraphEdge).where(
            and_(
                MemoryGraphEdge.edge_type == edge.type,
                MemoryGraphEdge.from_node_id == edge.from_id,
                MemoryGraphEdge.to_node_id == edge.to_id
            )
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing edge
            existing.props = edge.props
            return existing
        else:
            # Create new edge
            db_edge = MemoryGraphEdge(
                edge_type=edge.type,
                from_node_id=edge.from_id,
                to_node_id=edge.to_id,
                props=edge.props,
                created_by=user_id
            )
            self.db.add(db_edge)
            return db_edge
    
    async def _clear_session_data(self, session_id: UUID) -> None:
        """Clear all nodes and edges for a session."""
        # Note: In a more sophisticated implementation, we'd track which nodes/edges 
        # belong to which session. For now, this is a placeholder.
        pass
    
    async def _update_session_stats(
        self, 
        session_id: UUID, 
        nodes_count: int, 
        edges_count: int
    ) -> None:
        """Update session statistics."""
        query = select(MemoryGraphSession).where(MemoryGraphSession.id == session_id)
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            session.stats = {
                "nodes_count": nodes_count,
                "edges_count": edges_count,
                "last_updated": str(session.updated_at)
            }
            await self.db.commit()