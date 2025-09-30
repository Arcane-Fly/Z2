#!/usr/bin/env python3
"""
Comprehensive Memory Graph System Demonstration

This demo showcases the complete 20-minute mini-experiment described in the problem statement,
plus additional features demonstrating the power of memory graphs for multi-agent workflows.
"""

import sys
import json
from datetime import datetime
sys.path.append('/home/runner/work/Z2/Z2/backend')

from app.agents.memory_graph import MemoryGraph, Node, Edge, EntityTypes, RelationTypes
from app.agents.ingestor_agent import IngestorAgent
from app.agents.planner_agent import PlannerAgent


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n🔹 {title}")
    print("-" * (len(title) + 3))


def demonstrate_memory_graph_system():
    """Complete demonstration of the memory graph system."""
    
    print_header("MEMORY GRAPH SYSTEM - COMPREHENSIVE DEMONSTRATION")
    
    print("""
🧠 Memory Graph System Overview:
• Not just a list of facts; it's a network of entities and relationships
• Enables multi-hop reasoning across connections
• Provides composable agent outputs and context compression
• Delivers explainable, traceable decisions

This demonstration follows the 20-minute mini-experiment specification
plus additional real-world scenarios.
""")
    
    # 1. Initialize the system
    print_section("1. System Initialization")
    
    graph = MemoryGraph()
    ingestor = IngestorAgent(graph)
    planner = PlannerAgent(graph)
    
    print("✓ Memory graph initialized")
    print("✓ Ingestor agent (extracts entities/relations) ready")
    print("✓ Planner agent (queries graph for reasoning) ready")
    
    # 2. Mini-experiment: Basic CRM7 scenario
    print_section("2. Mini-Experiment: Basic CRM7 Scenario")
    
    scenario1 = "crm7 on Vercel requires SUPABASE_URL, SUPABASE_ANON_KEY"
    print(f"📝 Input: '{scenario1}'")
    
    result1 = ingestor.ingest(scenario1, {"source": "readme", "timestamp": datetime.now().isoformat()})
    
    print(f"📊 Extracted:")
    print(f"   • Services: {result1['services']}")
    print(f"   • Environment Variables: {result1['envvars']}")
    print(f"   • Nodes created: {result1['nodes_created']}")
    print(f"   • Relationships: {result1['edges_created']}")
    
    # 3. Add incident information (second hop)
    print_section("3. Adding Second Hop: Incident Information")
    
    incident_text = "Incident INC-101 caused by missing SUPABASE_URL affects crm7 deployment"
    print(f"📝 Input: '{incident_text}'")
    
    result2 = ingestor.ingest(incident_text, {"source": "incident_log"})
    
    print(f"📊 Additional extraction:")
    print(f"   • New incidents: {result2['incidents']}")
    print(f"   • New relationships: {result2['edges_created']}")
    
    # 4. Query the graph - demonstrate planning agent
    print_section("4. Multi-Agent Querying and Reasoning")
    
    queries = [
        ("What's blocking crm7 rollout?", "blocking_analysis"),
        ("What environment variables are missing for crm7?", "missing_envvars"),
        ("Which incidents are related to current rollout risks?", "related_incidents"),
        ("What services are affected by INC-101?", "impact_analysis"),
    ]
    
    for query_text, query_type in queries:
        print(f"\n🤔 Query: '{query_text}'")
        
        result = planner.answer_query(query_text, query_type)
        
        print(f"   💡 Answer: {result['answer']}")
        print(f"   🔍 Query Type: {result['query_type']}")
        print(f"   📋 Evidence Count: {len(result['evidence'])}")
        
        for i, evidence in enumerate(result['evidence'][:3], 1):  # Show first 3
            print(f"      {i}. {evidence.get('type', 'unknown')}: {evidence.get('description', evidence)}")
        
        if len(result['evidence']) > 3:
            print(f"      ... and {len(result['evidence']) - 3} more")
    
    # 5. Extended scenario: Complex multi-service environment
    print_section("5. Extended Scenario: Multi-Service Environment")
    
    complex_scenarios = [
        "workforce-hub service depends on REDIS_URL and AUTH_SECRET",
        "apprentice-tracker requires DATABASE_URL, STRIPE_KEY, and SENDGRID_API_KEY", 
        "INC-200 outage affecting workforce-hub due to Redis connection timeout",
        "INC-201 payment processing failure in apprentice-tracker missing STRIPE_KEY"
    ]
    
    print("📝 Ingesting complex multi-service scenario:")
    
    for i, scenario in enumerate(complex_scenarios, 1):
        print(f"   {i}. {scenario}")
        ingestor.ingest(scenario, {"source": f"scenario_{i}"})
    
    # 6. Advanced multi-hop reasoning
    print_section("6. Advanced Multi-Hop Reasoning")
    
    advanced_queries = [
        "What services might be affected if Redis goes down?",
        "Show me all environment variable dependencies across services",
        "What incidents have occurred that could affect our current deployment pipeline?",
        "Which services have the most dependencies and highest risk?"
    ]
    
    for query in advanced_queries:
        print(f"\n🧐 Advanced Query: '{query}'")
        
        result = planner.answer_query(query)
        print(f"   💡 {result['answer']}")
        
        if result['evidence']:
            print(f"   📊 Key findings:")
            for evidence in result['evidence'][:2]:  # Show top 2
                desc = evidence.get('description', str(evidence))
                print(f"      • {desc}")
    
    # 7. Graph structure analysis
    print_section("7. Final Graph Structure Analysis")
    
    graph_data = graph.to_dict()
    
    print(f"📈 Graph Statistics:")
    print(f"   • Total Entities: {len(graph_data['nodes'])}")
    print(f"   • Total Relationships: {len(graph_data['edges'])}")
    
    # Analyze by entity type
    entity_counts = {}
    for node in graph_data['nodes']:
        entity_type = node['type']
        entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
    
    print(f"\n📊 Entity Breakdown:")
    for entity_type, count in entity_counts.items():
        print(f"   • {entity_type}: {count}")
    
    # Analyze relationship types
    relation_counts = {}
    for edge in graph_data['edges']:
        relation_type = edge['type']
        relation_counts[relation_type] = relation_counts.get(relation_type, 0) + 1
    
    print(f"\n🔗 Relationship Breakdown:")
    for relation_type, count in relation_counts.items():
        print(f"   • {relation_type}: {count}")
    
    # 8. Demonstrate key benefits
    print_section("8. Key Benefits Demonstrated")
    
    benefits = [
        ("Composability", "Agent outputs are structured nodes/edges, not just text"),
        ("Context Compression", "Query specific subgraphs vs processing entire conversation history"),  
        ("Traceability", "Every decision backed by evidence paths through the graph"),
        ("Multi-hop Reasoning", "Connect incidents → env vars → services → deployment risks"),
        ("Persistent Knowledge", "Information accumulates across conversations and agents"),
        ("Explainable AI", "Show exactly why decisions were made with evidence"),
    ]
    
    for benefit, description in benefits:
        print(f"✅ {benefit}: {description}")
    
    # 9. Sample graph export
    print_section("9. Sample Graph Export (JSON)")
    
    sample_export = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_nodes": len(graph_data['nodes']),
            "total_edges": len(graph_data['edges']),
            "experiment": "memory_graph_demo"
        },
        "graph": graph_data
    }
    
    # Show a subset for readability
    print("📄 Sample export structure:")
    print(json.dumps({
        "metadata": sample_export["metadata"],
        "nodes_sample": graph_data["nodes"][:2],
        "edges_sample": graph_data["edges"][:2]
    }, indent=2))
    
    # 10. Summary and next steps
    print_section("10. Summary & Production Readiness")
    
    print("""
🎯 What we've accomplished:

✓ Implemented the 20-minute mini-experiment specification
✓ Demonstrated multi-agent memory graph workflows
✓ Showed multi-hop reasoning capabilities  
✓ Built persistent storage and API layers
✓ Created comprehensive test coverage
✓ Integrated with existing DIE system

🚀 Ready for production use cases:

• CRM7 parity roadmap (Feature→Route→Permission mapping)
• Deploy hygiene (Service→EnvVar→Secret→Incident tracking)  
• Support flows (Ticket→Customer→Plan→Module routing)
• Risk assessment (Service→Dependency→Failure analysis)
• Capacity planning (Load→Service→Resource→Cost analysis)

🛠️  API Endpoints available:
• POST /api/v1/memory-graph/ingest - Text → Graph ingestion
• POST /api/v1/memory-graph/query - Graph querying & reasoning
• Sessions, export, and management endpoints

📊 Performance characteristics:
• Efficient graph traversal with indexed lookups
• Structured storage vs. unstructured text processing
• Composable agent outputs for downstream processing
• Context compression for improved LLM efficiency
""")
    
    print_header("DEMONSTRATION COMPLETE")
    print(f"\n🎉 Memory Graph System successfully demonstrated!")
    print(f"📈 Graph contains {len(graph_data['nodes'])} entities and {len(graph_data['edges'])} relationships")
    print(f"🧠 Ready for integration into multi-agent workflows")
    
    return graph


if __name__ == "__main__":
    demonstrate_memory_graph_system()