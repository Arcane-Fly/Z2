"""
Tests for the Memory Graph system.
"""

import pytest
from app.agents.memory_graph import MemoryGraph, Node, Edge, EntityTypes, RelationTypes
from app.agents.ingestor_agent import IngestorAgent
from app.agents.planner_agent import PlannerAgent


class TestMemoryGraph:
    """Test cases for MemoryGraph class."""
    
    def test_memory_graph_initialization(self):
        """Test that MemoryGraph initializes correctly."""
        graph = MemoryGraph()
        
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert len(graph._outgoing_edges) == 0
        assert len(graph._incoming_edges) == 0
    
    def test_node_creation_and_upsert(self):
        """Test node creation and upserting."""
        graph = MemoryGraph()
        
        # Test explicit ID
        node1 = Node(id="svc:test", type=EntityTypes.SERVICE, props={"name": "test"})
        graph.upsert_node(node1)
        
        assert "svc:test" in graph.nodes
        assert graph.nodes["svc:test"].type == EntityTypes.SERVICE
        assert graph.nodes["svc:test"].props["name"] == "test"
        
        # Test auto-generated ID
        node2 = Node(id="", type=EntityTypes.ENVVAR, props={"key": "TEST_VAR"})
        graph.upsert_node(node2)
        
        assert len(graph.nodes) == 2
        assert any(node.type == EntityTypes.ENVVAR for node in graph.nodes.values())
    
    def test_edge_creation_and_validation(self):
        """Test edge creation with validation."""
        graph = MemoryGraph()
        
        # Create nodes first
        service_node = Node(id="svc:test", type=EntityTypes.SERVICE, props={"name": "test"})
        envvar_node = Node(id="env:TEST_VAR", type=EntityTypes.ENVVAR, props={"key": "TEST_VAR"})
        
        graph.upsert_node(service_node)
        graph.upsert_node(envvar_node)
        
        # Create edge
        edge = Edge(
            type=RelationTypes.SERVICE_REQUIRES_ENVVAR,
            from_id="svc:test",
            to_id="env:TEST_VAR"
        )
        
        graph.add_edge(edge)
        
        assert len(graph.edges) == 1
        assert "svc:test" in graph._outgoing_edges
        assert "env:TEST_VAR" in graph._incoming_edges
    
    def test_edge_validation_missing_nodes(self):
        """Test that edges fail validation when nodes don't exist."""
        graph = MemoryGraph()
        
        edge = Edge(
            type=RelationTypes.SERVICE_REQUIRES_ENVVAR,
            from_id="svc:missing",
            to_id="env:missing"
        )
        
        with pytest.raises(ValueError, match="Source node svc:missing not found"):
            graph.add_edge(edge)
    
    def test_get_neighbors(self):
        """Test neighbor retrieval."""
        graph = MemoryGraph()
        
        # Setup graph
        service = Node(id="svc:test", type=EntityTypes.SERVICE)
        envvar1 = Node(id="env:VAR1", type=EntityTypes.ENVVAR)
        envvar2 = Node(id="env:VAR2", type=EntityTypes.ENVVAR)
        
        graph.upsert_node(service)
        graph.upsert_node(envvar1)
        graph.upsert_node(envvar2)
        
        edge1 = Edge(RelationTypes.SERVICE_REQUIRES_ENVVAR, "svc:test", "env:VAR1")
        edge2 = Edge(RelationTypes.SERVICE_REQUIRES_ENVVAR, "svc:test", "env:VAR2")
        
        graph.add_edge(edge1)
        graph.add_edge(edge2)
        
        # Test neighbor retrieval
        neighbors = graph.get_neighbors("svc:test", RelationTypes.SERVICE_REQUIRES_ENVVAR)
        
        assert len(neighbors) == 2
        neighbor_ids = [n.id for n in neighbors]
        assert "env:VAR1" in neighbor_ids
        assert "env:VAR2" in neighbor_ids
    
    def test_serialization(self):
        """Test graph serialization and deserialization."""
        graph = MemoryGraph()
        
        # Create sample graph
        service = Node(id="svc:test", type=EntityTypes.SERVICE, props={"name": "test"})
        envvar = Node(id="env:TEST_VAR", type=EntityTypes.ENVVAR, props={"key": "TEST_VAR"})
        
        graph.upsert_node(service)
        graph.upsert_node(envvar)
        
        edge = Edge(RelationTypes.SERVICE_REQUIRES_ENVVAR, "svc:test", "env:TEST_VAR")
        graph.add_edge(edge)
        
        # Serialize
        data = graph.to_dict()
        
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1
        
        # Deserialize
        new_graph = MemoryGraph()
        new_graph.from_dict(data)
        
        assert len(new_graph.nodes) == 2
        assert len(new_graph.edges) == 1
        assert "svc:test" in new_graph.nodes
        assert "env:TEST_VAR" in new_graph.nodes


class TestIngestorAgent:
    """Test cases for IngestorAgent class."""
    
    def test_ingestor_basic_extraction(self):
        """Test basic entity extraction."""
        graph = MemoryGraph()
        ingestor = IngestorAgent(graph)
        
        text = "crm7 service requires SUPABASE_URL and REDIS_URL"
        result = ingestor.ingest(text)
        
        assert "crm7" in result["services"]
        assert "SUPABASE_URL" in result["envvars"]
        assert "REDIS_URL" in result["envvars"]
        assert result["nodes_created"] >= 3  # service + 2 env vars
        assert result["edges_created"] >= 2  # service -> env vars
    
    def test_ingestor_incident_extraction(self):
        """Test incident extraction."""
        graph = MemoryGraph()
        ingestor = IngestorAgent(graph)
        
        text = "Incident INC-101 caused by missing environment variable"
        result = ingestor.ingest(text)
        
        assert "INC-101" in result["incidents"]
        assert len(result["nodes"]) >= 1
    
    def test_ingestor_relationship_extraction(self):
        """Test relationship extraction."""
        graph = MemoryGraph()
        ingestor = IngestorAgent(graph)
        
        # First ingest services and env vars
        text1 = "crm7 service requires DATABASE_URL"
        ingestor.ingest(text1)
        
        # Then ingest incident relationship
        text2 = "Incident INC-100 affects crm7 service"
        result = ingestor.ingest(text2)
        
        # Check that relationships were created
        service_neighbors = graph.get_neighbors("svc:crm7", RelationTypes.SERVICE_REQUIRES_ENVVAR)
        assert len(service_neighbors) >= 1
        
        # Check for incident relationship
        incident_edges = [e for e in graph.edges if e.type == RelationTypes.INCIDENT_IMPACTS_SERVICE]
        assert len(incident_edges) >= 1


class TestPlannerAgent:
    """Test cases for PlannerAgent class."""
    
    def setup_test_graph(self):
        """Setup a test graph with known structure."""
        graph = MemoryGraph()
        
        # Create nodes
        service = Node(id="svc:crm7", type=EntityTypes.SERVICE, props={"name": "crm7"})
        envvar1 = Node(id="env:DB_URL", type=EntityTypes.ENVVAR, props={"key": "DB_URL"})
        envvar2 = Node(id="env:API_KEY", type=EntityTypes.ENVVAR, props={"key": "API_KEY", "value": "set"})
        incident = Node(id="inc:INC-100", type=EntityTypes.INCIDENT, props={"id": "INC-100"})
        
        graph.upsert_node(service)
        graph.upsert_node(envvar1)
        graph.upsert_node(envvar2)
        graph.upsert_node(incident)
        
        # Create relationships
        edge1 = Edge(RelationTypes.SERVICE_REQUIRES_ENVVAR, "svc:crm7", "env:DB_URL")
        edge2 = Edge(RelationTypes.SERVICE_REQUIRES_ENVVAR, "svc:crm7", "env:API_KEY")
        edge3 = Edge(RelationTypes.INCIDENT_IMPACTS_SERVICE, "inc:INC-100", "svc:crm7")
        
        graph.add_edge(edge1)
        graph.add_edge(edge2)
        graph.add_edge(edge3)
        
        return graph
    
    def test_planner_blocking_analysis(self):
        """Test blocking analysis functionality."""
        graph = self.setup_test_graph()
        planner = PlannerAgent(graph)
        
        result = planner.answer_query("What's blocking crm7 rollout?")
        
        assert result["query_type"] == "blocking_analysis"
        assert result["service_name"] == "crm7"
        assert len(result["evidence"]) >= 1  # Should find missing env var and incident
        
        # Should find missing DB_URL and incident
        blocking_types = [evidence["type"] for evidence in result["evidence"]]
        assert "missing_envvar" in blocking_types
        assert "related_incident" in blocking_types
    
    def test_planner_missing_envvars(self):
        """Test missing environment variables analysis."""
        graph = self.setup_test_graph()
        planner = PlannerAgent(graph)
        
        result = planner.answer_query("What env vars are missing for crm7?", "missing_envvars")
        
        assert result["query_type"] == "missing_envvars"
        assert result["service_name"] == "crm7"
        
        # Should find DB_URL as missing (no value set)
        missing_vars = [evidence["key"] for evidence in result["evidence"]]
        assert "DB_URL" in missing_vars
    
    def test_planner_impact_analysis(self):
        """Test incident impact analysis."""
        graph = self.setup_test_graph()
        planner = PlannerAgent(graph)
        
        result = planner.answer_query("What services are affected by INC-100?", "impact_analysis")
        
        assert result["query_type"] == "impact_analysis"
        assert len(result["evidence"]) >= 1
        
        affected_services = [evidence["service_name"] for evidence in result["evidence"]]
        assert "crm7" in affected_services
    
    def test_planner_query_type_detection(self):
        """Test automatic query type detection."""
        graph = self.setup_test_graph()
        planner = PlannerAgent(graph)
        
        # Test different query patterns
        blocking_result = planner.answer_query("What's blocking the deployment?")
        assert blocking_result["query_type"] == "blocking_analysis"
        
        missing_result = planner.answer_query("What environment variables are missing?")
        assert missing_result["query_type"] == "missing_envvars"
        
        incident_result = planner.answer_query("Which incidents are related?")
        assert incident_result["query_type"] == "related_incidents"