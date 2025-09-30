"""
Memory Graph System for Multi-Agent Workflows

Implements a network of entities and relationships that allows agents to reason
across connections and maintain structured knowledge rather than just raw text.

Based on the mini-experiment specification:
- Entities: Service, EnvVar, Incident
- Relations: SERVICE_REQUIRES_ENVVAR, INCIDENT_IMPACTS_SERVICE
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union
from uuid import uuid4
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Node:
    """Represents an entity in the memory graph."""
    
    id: str
    type: str  # "Service", "EnvVar", "Incident"
    props: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"{self.type.lower()}:{uuid4().hex[:8]}"


@dataclass 
class Edge:
    """Represents a relationship between entities in the memory graph."""
    
    type: str  # "SERVICE_REQUIRES_ENVVAR", "INCIDENT_IMPACTS_SERVICE"
    from_id: str
    to_id: str
    props: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.from_id or not self.to_id:
            raise ValueError("Edge must have valid from_id and to_id")


class MemoryGraph:
    """Core memory graph that stores nodes and edges with query capabilities."""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        # Index for fast lookups
        self._outgoing_edges: Dict[str, List[Edge]] = {}
        self._incoming_edges: Dict[str, List[Edge]] = {}
    
    def upsert_node(self, node: Node) -> None:
        """Add or update a node in the graph."""
        self.nodes[node.id] = node
        logger.debug("Upserted node", node_id=node.id, node_type=node.type)
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        # Validate that nodes exist
        if edge.from_id not in self.nodes:
            raise ValueError(f"Source node {edge.from_id} not found")
        if edge.to_id not in self.nodes:
            raise ValueError(f"Target node {edge.to_id} not found")
        
        # Check for duplicates
        for existing_edge in self.edges:
            if (existing_edge.type == edge.type and 
                existing_edge.from_id == edge.from_id and 
                existing_edge.to_id == edge.to_id):
                logger.debug("Edge already exists, skipping", edge=edge)
                return
        
        self.edges.append(edge)
        
        # Update indexes
        if edge.from_id not in self._outgoing_edges:
            self._outgoing_edges[edge.from_id] = []
        self._outgoing_edges[edge.from_id].append(edge)
        
        if edge.to_id not in self._incoming_edges:
            self._incoming_edges[edge.to_id] = []
        self._incoming_edges[edge.to_id].append(edge)
        
        logger.debug("Added edge", edge_type=edge.type, from_id=edge.from_id, to_id=edge.to_id)
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[Node]:
        """Get all nodes of a specific type."""
        return [node for node in self.nodes.values() if node.type == node_type]
    
    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[Node]:
        """Get neighboring nodes connected via specific edge type."""
        neighbors = []
        
        # Outgoing edges
        for edge in self._outgoing_edges.get(node_id, []):
            if edge_type is None or edge.type == edge_type:
                target_node = self.nodes.get(edge.to_id)
                if target_node:
                    neighbors.append(target_node)
        
        # Incoming edges
        for edge in self._incoming_edges.get(node_id, []):
            if edge_type is None or edge.type == edge_type:
                source_node = self.nodes.get(edge.from_id)
                if source_node:
                    neighbors.append(source_node)
        
        return neighbors
    
    def query_path(self, start_node_id: str, target_type: str, max_hops: int = 2) -> List[List[Node]]:
        """Find paths from start node to nodes of target type within max_hops."""
        paths = []
        visited = set()
        
        def dfs(current_id: str, path: List[Node], hops: int):
            if hops > max_hops:
                return
            
            current_node = self.nodes.get(current_id)
            if not current_node:
                return
            
            path = path + [current_node]
            
            if current_node.type == target_type and len(path) > 1:
                paths.append(path)
                return
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            
            # Explore neighbors
            for edge in self._outgoing_edges.get(current_id, []):
                dfs(edge.to_id, path, hops + 1)
            
            visited.remove(current_id)
        
        dfs(start_node_id, [], 0)
        return paths
    
    def get_subgraph(self, center_node_id: str, hops: int = 1) -> 'MemoryGraph':
        """Extract a subgraph within N hops of the center node."""
        subgraph = MemoryGraph()
        
        # BFS to collect nodes within hops
        visited = set()
        queue = [(center_node_id, 0)]
        
        while queue:
            node_id, distance = queue.pop(0)
            
            if node_id in visited or distance > hops:
                continue
            
            visited.add(node_id)
            node = self.nodes.get(node_id)
            if node:
                subgraph.upsert_node(node)
            
            if distance < hops:
                # Add neighbors to queue
                for edge in self._outgoing_edges.get(node_id, []):
                    queue.append((edge.to_id, distance + 1))
                for edge in self._incoming_edges.get(node_id, []):
                    queue.append((edge.from_id, distance + 1))
        
        # Add edges between included nodes
        for edge in self.edges:
            if edge.from_id in visited and edge.to_id in visited:
                subgraph.add_edge(edge)
        
        return subgraph
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary."""
        return {
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type, 
                    "props": node.props
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "type": edge.type,
                    "from": edge.from_id,
                    "to": edge.to_id,
                    "props": edge.props
                }
                for edge in self.edges
            ]
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load graph from dictionary."""
        self.nodes.clear()
        self.edges.clear()
        self._outgoing_edges.clear()
        self._incoming_edges.clear()
        
        # Load nodes first
        for node_data in data.get("nodes", []):
            node = Node(
                id=node_data["id"],
                type=node_data["type"],
                props=node_data.get("props", {})
            )
            self.upsert_node(node)
        
        # Then load edges
        for edge_data in data.get("edges", []):
            edge = Edge(
                type=edge_data["type"],
                from_id=edge_data["from"],
                to_id=edge_data["to"],
                props=edge_data.get("props", {})
            )
            self.add_edge(edge)


# Entity type constants
class EntityTypes:
    SERVICE = "Service"
    ENVVAR = "EnvVar"
    INCIDENT = "Incident"


# Relation type constants  
class RelationTypes:
    SERVICE_REQUIRES_ENVVAR = "SERVICE_REQUIRES_ENVVAR"
    INCIDENT_IMPACTS_SERVICE = "INCIDENT_IMPACTS_SERVICE"