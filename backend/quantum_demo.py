"""
Quantum Computing Module Demonstration

This script demonstrates the quantum computing functionality of the Z2 platform,
showing how to create quantum tasks with multiple agent variations and execute
them in parallel with different collapse strategies.
"""

import asyncio
import json
from datetime import datetime
from uuid import uuid4

# Mock implementations for demonstration purposes
class MockUser:
    def __init__(self):
        self.id = uuid4()
        self.username = "demo_user"


class MockDB:
    def __init__(self):
        self.tasks = {}
        self.variations = {}
        self.results = {}
    
    async def add(self, obj):
        pass
    
    async def flush(self):
        pass
    
    async def commit(self):
        pass
    
    async def refresh(self, obj):
        pass
    
    async def execute(self, query):
        pass


async def demonstrate_quantum_task_creation():
    """Demonstrate creating a quantum task with multiple variations."""
    print("\n🚀 Z2 Quantum Computing Module Demonstration")
    print("=" * 50)
    
    # Import quantum components
    from app.models.quantum import CollapseStrategy, TaskStatus
    from app.schemas.quantum import QuantumTaskCreate, VariationCreate
    from app.services.quantum_service import QuantumAgentManager
    
    print("\n1. Creating Quantum Task with Multiple Variations")
    print("-" * 45)
    
    # Create variations for different approaches
    variations = [
        VariationCreate(
            name="Conservative Analysis",
            agent_type="analyst",
            provider="openai",
            model="gpt-4",
            prompt_modifications={
                "style": "conservative",
                "prefix": "As a conservative financial analyst,",
            },
            parameters={"temperature": 0.3},
            weight=1.0,
        ),
        VariationCreate(
            name="Aggressive Growth Focus",
            agent_type="researcher", 
            provider="anthropic",
            model="claude-3",
            prompt_modifications={
                "style": "aggressive",
                "prefix": "As a growth-focused investment researcher,",
            },
            parameters={"temperature": 0.7},
            weight=1.5,
        ),
        VariationCreate(
            name="Risk Assessment Specialist",
            agent_type="validator",
            provider="groq",
            model="llama-70b",
            prompt_modifications={
                "style": "analytical",
                "prefix": "As a risk assessment specialist,",
            },
            parameters={"temperature": 0.5},
            weight=1.2,
        ),
    ]
    
    # Create quantum task
    task_data = QuantumTaskCreate(
        name="Market Analysis Q4 2024",
        description="Comprehensive market analysis for Q4 2024 investment strategy",
        task_description="""
        Analyze the current market conditions and provide investment recommendations 
        for Q4 2024. Consider:
        1. Technology sector performance
        2. Interest rate impacts
        3. Geopolitical factors
        4. Economic indicators
        
        Provide specific stock recommendations with reasoning.
        """,
        collapse_strategy=CollapseStrategy.WEIGHTED,
        metrics_config={
            "weights": {
                "execution_time": 0.2,
                "success_rate": 0.3,
                "completeness": 0.3,
                "accuracy": 0.2
            }
        },
        max_parallel_executions=3,
        timeout_seconds=600,
        variations=variations
    )
    
    print(f"Task Name: {task_data.name}")
    print(f"Variations: {len(task_data.variations)}")
    print(f"Collapse Strategy: {task_data.collapse_strategy}")
    print(f"Max Parallel Executions: {task_data.max_parallel_executions}")
    
    for i, var in enumerate(task_data.variations, 1):
        print(f"  {i}. {var.name} ({var.agent_type}) - Weight: {var.weight}")
    
    return task_data


async def demonstrate_collapse_strategies():
    """Demonstrate different collapse strategies."""
    print("\n\n2. Collapse Strategy Demonstrations")
    print("-" * 35)
    
    from app.models.quantum import QuantumThreadResult, ThreadStatus
    from app.services.quantum_service import QuantumAgentManager
    
    # Create mock quantum manager
    quantum_manager = QuantumAgentManager(MockDB())
    
    # Create mock results with different scores
    mock_results = [
        QuantumThreadResult(
            id=uuid4(),
            thread_name="Conservative Analysis",
            status=ThreadStatus.COMPLETED,
            result={
                "response": "Conservative recommendation: Focus on blue-chip stocks and bonds.",
                "recommendations": ["AAPL", "MSFT", "BRK.B"],
                "confidence": 0.8
            },
            total_score=0.75,
            execution_time=45.2,
            task_id=uuid4(),
            variation_id=uuid4(),
        ),
        QuantumThreadResult(
            id=uuid4(),
            thread_name="Aggressive Growth",
            status=ThreadStatus.COMPLETED,
            result={
                "response": "Growth recommendation: Invest in high-growth tech and emerging markets.",
                "recommendations": ["NVDA", "TSLA", "PLTR"],
                "confidence": 0.9
            },
            total_score=0.85,
            execution_time=52.1,
            task_id=uuid4(),
            variation_id=uuid4(),
        ),
        QuantumThreadResult(
            id=uuid4(),
            thread_name="Risk Assessment",
            status=ThreadStatus.COMPLETED,
            result={
                "response": "Risk-balanced approach: Diversify across sectors with defensive positions.",
                "recommendations": ["SPY", "QQQ", "VTI"],
                "confidence": 0.85
            },
            total_score=0.80,
            execution_time=38.7,
            task_id=uuid4(),
            variation_id=uuid4(),
        ),
    ]
    
    print("\nMock Results:")
    for result in mock_results:
        print(f"  • {result.thread_name}: Score {result.total_score}, Time {result.execution_time}s")
    
    # Demonstrate different collapse strategies
    strategies = [
        ("First Success", quantum_manager._collapse_first_success),
        ("Best Score", quantum_manager._collapse_best_score),
        ("Consensus", quantum_manager._collapse_consensus),
        ("Combined", quantum_manager._collapse_combined),
    ]
    
    print("\nCollapse Strategy Results:")
    for strategy_name, strategy_func in strategies:
        collapsed_result, metrics = strategy_func(mock_results)
        print(f"\n{strategy_name}:")
        print(f"  Final Score: {metrics.get('final_score', 0.0):.3f}")
        print(f"  Strategy: {metrics.get('strategy', 'unknown')}")
        if 'selected_result_id' in metrics:
            print(f"  Selected Result: {metrics['selected_result_id']}")


async def demonstrate_metrics_calculation():
    """Demonstrate metrics calculation for thread results."""
    print("\n\n3. Metrics Calculation Demonstration")
    print("-" * 37)
    
    from app.services.quantum_service import QuantumAgentManager
    from app.models.quantum import Variation
    
    quantum_manager = QuantumAgentManager(MockDB())
    
    # Test different result scenarios
    test_cases = [
        {
            "name": "Successful Fast Execution",
            "result": {
                "response": "Comprehensive analysis with detailed market insights and actionable recommendations.",
                "success": True,
            },
            "execution_time": 15.0,
        },
        {
            "name": "Successful Slow Execution", 
            "result": {
                "response": "Good analysis",
                "success": True,
            },
            "execution_time": 45.0,
        },
        {
            "name": "Failed Execution",
            "result": {
                "response": None,
                "success": False,
                "error": "Connection timeout"
            },
            "execution_time": 30.0,
        },
    ]
    
    variation = Variation(
        id=uuid4(),
        name="Test Variation",
        agent_type="analyst",
        task_id=uuid4(),
    )
    
    print("Metrics Calculation Results:")
    for case in test_cases:
        metrics = await quantum_manager._calculate_thread_metrics(
            case["result"], case["execution_time"], variation
        )
        
        print(f"\n{case['name']}:")
        print(f"  Success Rate: {metrics['success_rate']:.3f}")
        print(f"  Execution Time Score: {metrics['execution_time_score']:.3f}")
        print(f"  Completeness: {metrics['completeness']:.3f}")
        print(f"  Accuracy: {metrics['accuracy']:.3f}")
        print(f"  Total Score: {metrics['total_score']:.3f}")


def demonstrate_prompt_modifications():
    """Demonstrate prompt modification functionality."""
    print("\n\n4. Prompt Modification Demonstration")
    print("-" * 35)
    
    from app.services.quantum_service import QuantumAgentManager
    
    quantum_manager = QuantumAgentManager(MockDB())
    
    base_prompt = "Analyze the following market data and provide investment recommendations."
    
    modification_examples = [
        {
            "name": "Style Modification",
            "modifications": {"style": "conservative"}
        },
        {
            "name": "Prefix Addition",
            "modifications": {"prefix": "As a senior financial advisor with 20 years of experience,"}
        },
        {
            "name": "Suffix Addition", 
            "modifications": {"suffix": "Please provide specific reasoning for each recommendation."}
        },
        {
            "name": "Text Replacement",
            "modifications": {"replacements": {"market data": "quarterly earnings reports"}}
        },
        {
            "name": "Combined Modifications",
            "modifications": {
                "prefix": "You are an expert financial analyst.",
                "style": "detailed",
                "replacements": {"investment": "stock"},
                "suffix": "Include risk assessment for each recommendation."
            }
        },
    ]
    
    print(f"Base Prompt: {base_prompt}")
    
    for example in modification_examples:
        modified = quantum_manager._apply_prompt_modifications(
            base_prompt, example["modifications"]
        )
        print(f"\n{example['name']}:")
        print(f"  Modified: {modified}")


async def demonstrate_api_usage():
    """Demonstrate API usage patterns."""
    print("\n\n5. API Usage Examples")
    print("-" * 22)
    
    print("API Endpoints Available:")
    endpoints = [
        "POST /api/v1/multi-agent-system/quantum/tasks/create",
        "POST /api/v1/multi-agent-system/quantum/tasks/{task_id}/execute", 
        "GET /api/v1/multi-agent-system/quantum/tasks/{task_id}",
        "GET /api/v1/multi-agent-system/quantum/tasks",
        "PATCH /api/v1/multi-agent-system/quantum/tasks/{task_id}",
        "POST /api/v1/multi-agent-system/quantum/tasks/{task_id}/cancel",
        "DELETE /api/v1/multi-agent-system/quantum/tasks/{task_id}",
    ]
    
    for endpoint in endpoints:
        print(f"  • {endpoint}")
    
    print("\nExample API Request (Create Task):")
    example_request = {
        "name": "Market Analysis",
        "task_description": "Analyze current market trends",
        "collapse_strategy": "best_score",
        "max_parallel_executions": 3,
        "timeout_seconds": 300,
        "variations": [
            {
                "name": "Conservative Approach",
                "agent_type": "analyst",
                "weight": 1.0
            },
            {
                "name": "Aggressive Approach", 
                "agent_type": "researcher",
                "weight": 1.5
            }
        ]
    }
    
    print(json.dumps(example_request, indent=2))


async def main():
    """Run the complete demonstration."""
    print("🔮 Z2 Platform - Quantum Computing Module")
    print("Parallel Agent Execution with Intelligent Result Collapse")
    
    try:
        # Run demonstrations
        await demonstrate_quantum_task_creation()
        await demonstrate_collapse_strategies()
        await demonstrate_metrics_calculation()
        demonstrate_prompt_modifications()
        await demonstrate_api_usage()
        
        print("\n\n✨ Demonstration Complete!")
        print("=" * 50)
        print("The quantum computing module provides:")
        print("• Parallel execution of multiple agent variations")
        print("• Intelligent result collapse strategies")
        print("• Comprehensive metrics and scoring")
        print("• Flexible prompt modifications")
        print("• RESTful API interface")
        print("• Async execution with proper error handling")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())