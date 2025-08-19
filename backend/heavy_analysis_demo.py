"""
Heavy Analysis Demo Script

Demonstrates the make-it-heavy integration functionality.
This script shows how to use the heavy analysis system even without full LLM provider setup.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

async def demo_tools():
    """Demonstrate the tool system functionality."""
    print("🔧 Heavy Analysis Tools Demo")
    print("=" * 50)
    
    try:
        from app.services.heavy_analysis_tools import HeavyAnalysisToolRegistry
        
        # Initialize tool registry
        registry = HeavyAnalysisToolRegistry()
        print(f"✅ Initialized {len(registry.get_all_tools())} tools")
        
        # List available tools
        print("\n📋 Available Tools:")
        for name, tool in registry.get_all_tools().items():
            print(f"   • {name}: {tool.description}")
        
        # Demo calculator
        print("\n🧮 Calculator Demo:")
        calc_tool = registry.get_tool('calculate')
        expressions = ["2 + 3 * 4", "sqrt(16)", "10 ** 2", "abs(-42)"]
        
        for expr in expressions:
            try:
                result = await calc_tool.execute(expr)
                if 'error' in result:
                    print(f"   {expr} = ERROR: {result['error']}")
                else:
                    print(f"   {expr} = {result['result']}")
            except Exception as e:
                print(f"   {expr} = ERROR: {e}")
        
        # Demo web search (if available)
        print("\n🔍 Web Search Demo:")
        search_tool = registry.get_tool('search_web')
        try:
            results = await search_tool.execute("Python programming", max_results=2)
            if results and isinstance(results, list):
                print(f"   Found {len(results)} results:")
                for i, result in enumerate(results[:2], 1):
                    if isinstance(result, dict) and 'title' in result:
                        title = result['title'][:60] + ("..." if len(result['title']) > 60 else "")
                        print(f"   {i}. {title}")
                    else:
                        print(f"   {i}. {result}")
            else:
                print("   Search returned no results")
        except Exception as e:
            print(f"   Search failed: {e}")
        
        print("\n✅ Tool demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Tool demo failed: {e}")
        import traceback
        traceback.print_exc()


async def demo_question_generation():
    """Demonstrate question generation for heavy analysis."""
    print("\n🤔 Question Generation Demo")
    print("=" * 50)
    
    try:
        from app.services.heavy_analysis import HeavyAnalysisService
        
        service = HeavyAnalysisService()
        
        # Test queries
        test_queries = [
            "What is artificial intelligence?",
            "How does climate change affect global economies?",
            "What are the benefits and risks of cryptocurrency?"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            questions = await service.decompose_task(query, 4)
            
            print("   Generated research questions:")
            for i, question in enumerate(questions, 1):
                print(f"   {i}. {question}")
        
        print("\n✅ Question generation demo completed!")
        
    except Exception as e:
        print(f"❌ Question generation demo failed: {e}")


async def demo_agent():
    """Demonstrate the heavy analysis agent."""
    print("\n🤖 Heavy Analysis Agent Demo") 
    print("=" * 50)
    
    try:
        from app.agents.heavy_analysis_agent import HeavyAnalysisAgent
        
        agent = HeavyAnalysisAgent("DemoAgent", "research_analyst")
        print(f"✅ Agent '{agent.name}' initialized with {len(agent.tools)} tools")
        
        # Show system prompt
        system_prompt = agent._create_system_prompt()
        print(f"\n📋 System Prompt (first 200 chars):")
        print(f"   {system_prompt[:200]}...")
        
        # Note about LLM providers
        print("\n⚠️  Note: Full agent functionality requires LLM providers to be configured")
        print("   When providers are available, the agent will:")
        print("   • Use dynamic question generation")
        print("   • Execute tools for research and analysis")
        print("   • Provide comprehensive multi-perspective responses")
        
        print("\n✅ Agent demo completed!")
        
    except Exception as e:
        print(f"❌ Agent demo failed: {e}")


async def demo_api_schemas():
    """Demonstrate API schemas and endpoints."""
    print("\n🌐 API Schema Demo")
    print("=" * 50)
    
    try:
        from app.api.v1.endpoints.heavy_analysis import HeavyAnalysisRequest, HeavyAnalysisResponse
        
        # Demo request
        sample_request = {
            "query": "Analyze the future of renewable energy technology",
            "num_agents": 4
        }
        
        print("📨 Sample API Request:")
        print(json.dumps(sample_request, indent=2))
        
        # Show available endpoints
        print("\n🛠️  Available Endpoints:")
        print("   • POST /api/v1/heavy-analysis/analyze")
        print("   • POST /api/v1/heavy-analysis/analyze/detailed") 
        print("   • GET  /api/v1/heavy-analysis/capabilities")
        
        print("\n📊 Response Features:")
        print("   • Comprehensive analysis result")
        print("   • Execution time and performance metrics")
        print("   • Individual agent results (detailed endpoint)")
        print("   • Error handling and status reporting")
        
        print("\n✅ API schema demo completed!")
        
    except Exception as e:
        print(f"❌ API schema demo failed: {e}")


async def main():
    """Main demo function."""
    print("🚀 Make-It-Heavy Integration Demo")
    print("🔗 Z2 AI Workforce Platform")
    print("=" * 50)
    print("This demo showcases the integrated make-it-heavy functionality")
    print("that provides Grok-Heavy style multi-agent orchestration.\n")
    
    # Run all demos
    await demo_tools()
    await demo_question_generation()
    await demo_agent()
    await demo_api_schemas()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("\nTo use in production:")
    print("1. Configure LLM providers in Z2's MIL")
    print("2. Start the FastAPI server")
    print("3. Send requests to /api/v1/heavy-analysis/analyze")
    print("4. Enjoy comprehensive multi-agent analysis! 🤖✨")


if __name__ == "__main__":
    asyncio.run(main())