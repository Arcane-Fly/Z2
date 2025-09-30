"""
Memory Graph database models for persistent storage.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.database.types import UniversalJSON


class MemoryGraphNode(Base):
    """Database model for memory graph nodes (entities)."""

    __tablename__ = "memory_graph_nodes"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Core node properties
    node_id: Mapped[str] = mapped_column(String(200), unique=True, index=True)  # e.g., "svc:crm7"
    node_type: Mapped[str] = mapped_column(String(50), index=True)  # "Service", "EnvVar", "Incident"
    props: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    
    # Metadata
    source_info: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Add index for common queries
    __table_args__ = (
        Index('ix_node_type_created', 'node_type', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<MemoryGraphNode(node_id={self.node_id}, type={self.node_type})>"


class MemoryGraphEdge(Base):
    """Database model for memory graph edges (relationships)."""

    __tablename__ = "memory_graph_edges"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    # Core edge properties
    edge_type: Mapped[str] = mapped_column(String(100), index=True)  # "SERVICE_REQUIRES_ENVVAR"
    from_node_id: Mapped[str] = mapped_column(String(200), index=True)
    to_node_id: Mapped[str] = mapped_column(String(200), index=True)
    props: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    
    # Metadata
    source_info: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Indexes for efficient graph traversal
    __table_args__ = (
        Index('ix_edge_from_type', 'from_node_id', 'edge_type'),
        Index('ix_edge_to_type', 'to_node_id', 'edge_type'),
        Index('ix_edge_unique', 'edge_type', 'from_node_id', 'to_node_id', unique=True),
    )

    def __repr__(self) -> str:
        return f"<MemoryGraphEdge({self.from_node_id} --[{self.edge_type}]--> {self.to_node_id})>"


class MemoryGraphSession(Base):
    """Database model for memory graph sessions - groups of related nodes/edges."""

    __tablename__ = "memory_graph_sessions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Session metadata
    config: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    stats: Mapped[dict] = mapped_column(UniversalJSON, default=dict)
    
    # Ownership
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<MemoryGraphSession(id={self.id}, name={self.name})>"