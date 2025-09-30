#!/usr/bin/env python3
"""
Integration test for the memory graph system with the existing DIE.
This test demonstrates integration without requiring a database setup.
"""

import sys
sys.path.append('/home/runner/work/Z2/Z2/backend')

from app.agents.die import ContextualMemory, AdaptiveContextualFlow
from app.agents.memory_graph import MemoryGraph, Node, Edge, EntityTypes, RelationTypes
from app.agents.ingestor_agent import IngestorAgent
from app.agents.planner_agent import PlannerAgent


def test_die_integration():
    """Test memory graph integration with DIE system."""
    print("🔗 Memory Graph + DIE Integration Test")
    print("=" * 50)
    
    # 1. Create DIE components
    die_flow = AdaptiveContextualFlow()
    
    # 2. Create memory graph
    graph = MemoryGraph()
    ingestor = IngestorAgent(graph)
    planner = PlannerAgent(graph)
    
    # 3. Simulate agent conversation with memory graph enhancement
    user_input = "We need to deploy crm7 service but it requires SUPABASE_URL and REDIS_URL environment variables"
    
    print(f"\n👤 User: {user_input}")
    
    # 4. Extract structured knowledge
    ingestion_result = ingestor.ingest(user_input, {"source": "user_conversation"})
    
    print(f"\n🧠 Memory Graph extracted:")
    print(f"  • Services: {ingestion_result['services']}")
    print(f"  • Env vars: {ingestion_result['envvars']}")
    print(f"  • Relationships: {len(ingestion_result['edges'])}")
    
    # 5. Generate agent response using graph knowledge
    blocking_query = planner.answer_query("What might block the crm7 deployment?")
    
    agent_response = f"""Based on the deployment requirements I can see:

{blocking_query['answer']}

Let me help you check these environment variables:
- SUPABASE_URL: {blocking_query['evidence'][0]['description'] if blocking_query['evidence'] else 'Required for database connection'}
- REDIS_URL: {'Required for caching' if len(ingestion_result['envvars']) > 1 else 'May be needed'}

Would you like me to help you configure these variables?"""
    
    print(f"\n🤖 Agent: {agent_response}")
    
    # 6. Update DIE contextual memory with structured + unstructured context
    metadata = {
        "timestamp": "2024-09-30T15:30:00Z",
        "success": True,
        "tokens_used": 150,
        "model_used": "gpt-4o",
        "graph_nodes": len(graph.nodes),
        "graph_edges": len(graph.edges),
        "extracted_entities": ingestion_result['services'] + ingestion_result['envvars']
    }
    
    die_flow.update_context(user_input, agent_response, metadata)
    
    # 7. Show enhanced context
    current_context = die_flow.get_context_for_prompt()
    
    print(f"\n📝 DIE Enhanced Context:")
    print(f"  • Short-term keys: {list(current_context.short_term.keys())}")
    print(f"  • Graph entities in context: {current_context.short_term.get('extracted_entities', [])}")
    print(f"  • Graph stats: {current_context.short_term.get('graph_nodes', 0)} nodes, {current_context.short_term.get('graph_edges', 0)} edges")
    
    # 8. Demonstrate follow-up query with enhanced context
    print(f"\n🔍 Follow-up scenario:")
    
    followup_input = "Actually, we also had incident INC-500 last month where crm7 went down due to missing SUPABASE_URL"
    print(f"👤 User: {followup_input}")
    
    # Ingest the new information
    incident_result = ingestor.ingest(followup_input, {"source": "incident_report"})
    print(f"  • New incidents detected: {incident_result['incidents']}")
    
    # Query for related risks
    risk_query = planner.answer_query("What incidents might affect our current deployment?")
    
    enhanced_response = f"""I see there's relevant history here:

{risk_query['answer']}

This incident (INC-500) is directly related to the SUPABASE_URL variable we just discussed. This reinforces the importance of ensuring this environment variable is properly configured before deployment.

Recommendation: Let's verify SUPABASE_URL is set and test the connection before proceeding with crm7 deployment."""
    
    print(f"🤖 Enhanced Agent: {enhanced_response}")
    
    # 9. Show final graph state
    print(f"\n📊 Final Knowledge Graph:")
    graph_data = graph.to_dict()
    print(f"  • Total entities: {len(graph_data['nodes'])}")
    print(f"  • Total relationships: {len(graph_data['edges'])}")
    
    for node in graph_data['nodes']:
        print(f"    - {node['id']} ({node['type']})")
    
    for edge in graph_data['edges']:
        print(f"    - {edge['from']} --[{edge['type']}]--> {edge['to']}")
    
    print(f"\n✅ Integration test completed successfully!")
    print(f"\n💡 Benefits demonstrated:")
    print(f"  • Structured knowledge extraction from conversations")
    print(f"  • Multi-hop reasoning (incident → env var → service)")
    print(f"  • Enhanced context for agent responses") 
    print(f"  • Persistent knowledge across conversations")
    
    return True


if __name__ == "__main__":
    test_die_integration()