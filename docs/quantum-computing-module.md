# Quantum Computing Module Documentation

## Overview

The Quantum Computing Module for the Z2 AI Workforce Platform enables parallel execution of multiple agent variations with intelligent result collapse strategies. This module improves reliability, quality, adaptability, and robustness by exploring multiple approaches simultaneously.

## Key Features

### 🔄 Parallel Agent Execution
- Execute multiple agent variations simultaneously
- Configurable concurrency control (1-20 parallel executions)
- Async execution with proper timeout handling
- Isolated error handling between variations

### 🎯 Collapse Strategies
- **First Success**: Returns the first successful result
- **Best Score**: Selects result with highest total score
- **Consensus**: Averages scores for consensus-based decisions
- **Combined**: Merges multiple responses into comprehensive result
- **Weighted**: Uses variation weights for intelligent selection

### 📊 Metrics & Scoring
- **Success Rate**: Execution success/failure tracking
- **Execution Time**: Performance-based scoring
- **Completeness**: Response quality assessment
- **Accuracy**: Result accuracy evaluation
- **Total Score**: Weighted combination of all metrics

### 🔧 Prompt Engineering
- Dynamic prompt modifications per variation
- Style adjustments (conservative, aggressive, analytical)
- Prefix/suffix additions for context
- Text replacements for specific targeting
- Parameter customization per variation

## API Endpoints

### Create Quantum Task
```http
POST /api/v1/multi-agent-system/quantum/tasks/create
```

**Request Body:**
```json
{
  "name": "Market Analysis Q4 2024",
  "description": "Comprehensive market analysis",
  "task_description": "Analyze market conditions and provide recommendations",
  "collapse_strategy": "weighted",
  "max_parallel_executions": 5,
  "timeout_seconds": 600,
  "metrics_config": {
    "weights": {
      "execution_time": 0.2,
      "success_rate": 0.3,
      "completeness": 0.3,
      "accuracy": 0.2
    }
  },
  "variations": [
    {
      "name": "Conservative Analysis",
      "agent_type": "analyst",
      "provider": "openai",
      "model": "gpt-4",
      "prompt_modifications": {
        "style": "conservative",
        "prefix": "As a conservative financial analyst,"
      },
      "parameters": {"temperature": 0.3},
      "weight": 1.0
    },
    {
      "name": "Growth Focus",
      "agent_type": "researcher",
      "provider": "anthropic", 
      "model": "claude-3",
      "prompt_modifications": {
        "style": "aggressive",
        "prefix": "As a growth-focused researcher,"
      },
      "parameters": {"temperature": 0.7},
      "weight": 1.5
    }
  ]
}
```

### Execute Quantum Task
```http
POST /api/v1/multi-agent-system/quantum/tasks/{task_id}/execute
```

**Request Body:**
```json
{
  "force_restart": false,
  "custom_metrics": {
    "weights": {
      "execution_time": 0.1,
      "success_rate": 0.4,
      "completeness": 0.3,
      "accuracy": 0.2
    }
  }
}
```

### Get Task Details
```http
GET /api/v1/multi-agent-system/quantum/tasks/{task_id}
```

**Query Parameters:**
- `include_results`: boolean (default: true)
- `include_variations`: boolean (default: true)

### List Tasks
```http
GET /api/v1/multi-agent-system/quantum/tasks
```

**Query Parameters:**
- `page`: int (default: 1)
- `page_size`: int (default: 10, max: 100)
- `status`: TaskStatus (pending, running, completed, failed, cancelled)

### Update Task
```http
PATCH /api/v1/multi-agent-system/quantum/tasks/{task_id}
```

### Cancel Task
```http
POST /api/v1/multi-agent-system/quantum/tasks/{task_id}/cancel
```

### Delete Task
```http
DELETE /api/v1/multi-agent-system/quantum/tasks/{task_id}
```

## Database Schema

### QuantumTask
- `id`: UUID (Primary Key)
- `name`: String(100) 
- `description`: Text (Optional)
- `task_description`: Text
- `collapse_strategy`: String(20) - Enum
- `metrics_config`: JSONB
- `max_parallel_executions`: Integer
- `timeout_seconds`: Integer
- `status`: String(20) - Enum
- `progress`: Float
- `collapsed_result`: JSONB (Optional)
- `final_metrics`: JSONB (Optional)
- `execution_summary`: JSONB (Optional)
- `started_at`: DateTime (Optional)
- `completed_at`: DateTime (Optional)
- `total_execution_time`: Float (Optional)
- `user_id`: UUID (Foreign Key)
- `created_at`: DateTime
- `updated_at`: DateTime

### Variation
- `id`: UUID (Primary Key)
- `name`: String(100)
- `description`: Text (Optional)
- `agent_type`: String(50)
- `provider`: String(50) (Optional)
- `model`: String(100) (Optional)
- `prompt_modifications`: JSONB
- `parameters`: JSONB
- `weight`: Float
- `task_id`: UUID (Foreign Key)
- `created_at`: DateTime

### QuantumThreadResult
- `id`: UUID (Primary Key)
- `thread_name`: String(100)
- `status`: String(20) - Enum
- `result`: JSONB (Optional)
- `error_message`: Text (Optional)
- `execution_time`: Float (Optional)
- `success_rate`: Float (Optional)
- `completeness`: Float (Optional)
- `accuracy`: Float (Optional)
- `total_score`: Float (Optional)
- `detailed_metrics`: JSONB
- `tokens_used`: Integer (Optional)
- `cost`: Float (Optional)
- `provider_used`: String(50) (Optional)
- `model_used`: String(100) (Optional)
- `started_at`: DateTime (Optional)
- `completed_at`: DateTime (Optional)
- `task_id`: UUID (Foreign Key)
- `variation_id`: UUID (Foreign Key)
- `created_at`: DateTime
- `updated_at`: DateTime

## Usage Examples

### Basic Task Creation
```python
from app.schemas.quantum import QuantumTaskCreate, VariationCreate
from app.models.quantum import CollapseStrategy

# Create variations
variations = [
    VariationCreate(
        name="Conservative Analysis",
        agent_type="analyst",
        weight=1.0
    ),
    VariationCreate(
        name="Aggressive Analysis", 
        agent_type="researcher",
        weight=1.5
    )
]

# Create task
task = QuantumTaskCreate(
    name="Market Analysis",
    task_description="Analyze current market trends",
    collapse_strategy=CollapseStrategy.WEIGHTED,
    variations=variations
)
```

### Advanced Configuration
```python
# Advanced variation with prompt modifications
variation = VariationCreate(
    name="Risk Assessment",
    agent_type="validator",
    provider="openai",
    model="gpt-4",
    prompt_modifications={
        "prefix": "As a risk assessment specialist,",
        "style": "analytical",
        "replacements": {
            "investment": "portfolio allocation"
        },
        "suffix": "Include specific risk metrics."
    },
    parameters={
        "temperature": 0.5,
        "max_tokens": 2000
    },
    weight=1.2
)
```

## Architecture Integration

### Service Layer
The `QuantumAgentManager` service handles:
- Task lifecycle management
- Parallel execution coordination
- Result collection and aggregation
- Collapse strategy application
- Metrics calculation

### Database Integration
- Uses SQLAlchemy ORM with async support
- Alembic migrations for schema management
- PostgreSQL JSONB for flexible data storage
- Proper foreign key relationships and indexes

### API Layer
- FastAPI endpoints with Pydantic validation
- Authentication integration
- Comprehensive error handling
- Structured JSON responses

### Error Handling
- Isolated error handling per variation
- Graceful degradation on partial failures
- Comprehensive logging with structlog
- Timeout management for long-running tasks

## Benefits

### 🔒 Reliability
- Multiple execution paths reduce single points of failure
- Isolated error handling prevents cascade failures
- Timeout management prevents resource exhaustion

### 🎯 Quality
- Multiple perspectives improve result quality
- Intelligent scoring and selection
- Comprehensive metrics for evaluation

### 🔄 Adaptability
- Flexible prompt modifications
- Multiple model/provider support
- Configurable collapse strategies

### 💪 Robustness
- Async execution with proper resource management
- Graceful error handling and recovery
- Comprehensive monitoring and logging

## Performance Considerations

- **Concurrency**: Semaphore-controlled parallel execution
- **Memory**: Efficient result storage with JSONB
- **Timeouts**: Configurable per-task timeout management
- **Resource Management**: Proper cleanup of async tasks
- **Database**: Optimized queries with proper indexing

## Security

- **Authentication**: Integration with existing auth system
- **Authorization**: User-based task ownership
- **Input Validation**: Comprehensive Pydantic validation
- **Rate Limiting**: Configurable execution limits
- **Data Isolation**: User-scoped data access

## Monitoring & Observability

- **Structured Logging**: Comprehensive logging with structlog
- **Metrics Collection**: Execution time, success rates, scores
- **Progress Tracking**: Real-time task progress updates
- **Error Tracking**: Detailed error reporting and analysis
- **Performance Monitoring**: Execution time and resource usage

## Future Enhancements

- **Frontend UI**: Web interface for task management
- **Advanced Metrics**: Machine learning-based scoring
- **Custom Agents**: Support for specialized agent types
- **Result Caching**: Intelligent caching of results
- **Batch Operations**: Bulk task management
- **Webhooks**: Real-time notifications
- **Export/Import**: Task template management