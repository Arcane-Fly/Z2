#!/usr/bin/env python3
"""
Simple test script for the memory graph system.
This demonstrates the 20-minute mini-experiment from the problem statement.
"""

import sys
sys.path.append('/home/runner/work/Z2/Z2/backend')

from app.agents.memory_graph import MemoryGraph, Node, Edge, EntityTypes, RelationTypes
from app.agents.ingestor_agent import IngestorAgent
from app.agents.planner_agent import PlannerAgent


def run_memory_graph_demo():
    """Run the memory graph demonstration."""
    print("🧠 Memory Graph System Demo")
    print("=" * 50)
    
    # 1. Create memory graph
    graph = MemoryGraph()
    
    # 2. Create agents
    ingestor = IngestorAgent(graph)
    planner = PlannerAgent(graph)
    
    # 3. Demo text (from problem statement example)
    demo_text = "crm7 on Vercel requires SUPABASE_URL, SUPABASE_ANON_KEY"
    
    print(f"\n📝 Ingesting text: '{demo_text}'")
    
    # 4. Ingest data
    result = ingestor.ingest(demo_text, {"source": "readme"})
    
    print(f"\n📊 Ingestion Results:")
    print(f"  • Nodes created: {result['nodes_created']}")
    print(f"  • Edges created: {result['edges_created']}")
    print(f"  • Services found: {result['services']}")
    print(f"  • Env vars found: {result['envvars']}")
    
    # 5. Add a second hop - simulate an incident
    incident_text = "Incident INC-101 caused by missing SUPABASE_URL affects crm7 deployment"
    print(f"\n📝 Adding incident: '{incident_text}'")
    
    incident_result = ingestor.ingest(incident_text, {"source": "incident_log"})
    print(f"  • Additional nodes: {incident_result['nodes_created']}")
    print(f"  • Additional edges: {incident_result['edges_created']}")
    
    # 6. Query the graph
    print(f"\n🤔 Querying: 'What's blocking crm7 rollout?'")
    
    query_result = planner.answer_query("What's blocking crm7 rollout?")
    print(f"  • Answer: {query_result['answer']}")
    print(f"  • Query type: {query_result['query_type']}")
    print(f"  • Evidence found: {len(query_result['evidence'])} items")
    
    for evidence in query_result['evidence']:
        print(f"    - {evidence['type']}: {evidence['description']}")
    
    # 7. Multi-hop query
    print(f"\n🔗 Multi-hop query: 'Which incidents are related to current rollout risks?'")
    
    incidents_result = planner.answer_query("Which incidents are related to current rollout risks?")
    print(f"  • Answer: {incidents_result['answer']}")
    print(f"  • Related incidents: {len(incidents_result['evidence'])}")
    
    for incident in incidents_result['evidence']:
        print(f"    - {incident['incident_id']} ({incident['relationship']})")
    
    # 7b. Test direct incident query
    print(f"\n🔍 Direct incident impact query:")
    impact_result = planner.answer_query("What services are affected by INC-101?", "impact_analysis")
    print(f"  • Answer: {impact_result['answer']}")
    print(f"  • Affected services: {len(impact_result['evidence'])}")
    
    for service in impact_result['evidence']:
        print(f"    - {service['service_name']}")
    
    # 7c. Test blocking analysis with incident detection
    print(f"\n🚫 Enhanced blocking analysis:")
    enhanced_result = planner.answer_query("What's blocking crm7 rollout including incidents?")
    print(f"  • Answer: {enhanced_result['answer']}")
    print(f"  • Graph operations: {enhanced_result['graph_operations']}")
    
    for evidence in enhanced_result['evidence']:
        print(f"    - {evidence['type']}: {evidence['description']}")
    
    # 8. Show graph structure
    print(f"\n📈 Final Graph Structure:")
    graph_data = graph.to_dict()
    print(f"  • Total nodes: {len(graph_data['nodes'])}")
    print(f"  • Total edges: {len(graph_data['edges'])}")
    
    print("\n  Nodes:")
    for node in graph_data['nodes']:
        print(f"    - {node['id']} ({node['type']})")
    
    print("\n  Relationships:")
    for edge in graph_data['edges']:
        print(f"    - {edge['from']} --[{edge['type']}]--> {edge['to']}")
    
    print("\n✅ Demo completed successfully!")
    return True


if __name__ == "__main__":
    run_memory_graph_demo()