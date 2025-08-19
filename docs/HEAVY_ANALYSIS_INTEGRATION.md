# Heavy Analysis Integration Documentation

## Overview

The make-it-heavy integration provides Grok-Heavy style multi-agent orchestration capabilities within the Z2 AI Workforce Platform. This implementation allows users to deploy multiple AI agents in parallel for comprehensive, multi-perspective analysis.

## Key Features

### 1. Multi-Agent Orchestration
- Deploy 2-8 parallel agents for comprehensive analysis
- Dynamic question generation creates specialized research angles
- Intelligent synthesis combines all agent perspectives

### 2. Tool System
- **Web Search**: DuckDuckGo integration with content extraction
- **Calculator**: Safe mathematical expression evaluation  
- **File Operations**: Secure file reading with restrictions
- **Task Completion**: Signals when analysis is complete

### 3. API Integration
- RESTful endpoints following Z2's patterns
- Detailed progress tracking and error handling
- Compatible with Z2's authentication system

## API Endpoints

### POST `/api/v1/heavy-analysis/analyze`
Execute heavy analysis with comprehensive results.

**Request:**
```json
{
  "query": "Analyze the impact of AI on software development",
  "num_agents": 4
}
```

**Response:**
```json
{
  "task_id": "uuid",
  "result": "Comprehensive analysis combining multiple agent perspectives...",
  "execution_time": 45.2,
  "num_agents": 4,
  "status": "completed"
}
```

### POST `/api/v1/heavy-analysis/analyze/detailed`
Execute heavy analysis with individual agent breakdowns.

**Additional Response Fields:**
```json
{
  "agent_results": [
    {
      "agent_id": 0,
      "status": "success",
      "response": "Agent-specific analysis...",
      "execution_time": 12.3
    }
  ]
}
```

### GET `/api/v1/heavy-analysis/capabilities`
Get information about heavy analysis capabilities and configuration.

## Architecture Integration

### Z2 Framework Integration
- **MIL Integration**: Uses Z2's Model Integration Layer for LLM provider abstraction
- **Agent Architecture**: Extends BasicAIAgent with tool capabilities
- **Error Handling**: Follows Z2's error handling patterns
- **Authentication**: Integrates with Z2's auth system

### Tool Framework
- **Base Classes**: `HeavyAnalysisTool` provides standard interface
- **Registry System**: `HeavyAnalysisToolRegistry` manages tool discovery
- **Security**: File operations and calculations include safety restrictions
- **Extensibility**: Easy to add new tools following the base pattern

## Configuration

### Tool Configuration
```python
tool_config = {
    'search': {
        'user_agent': 'Mozilla/5.0 (compatible; Z2-HeavyAnalysis)',
        'timeout': 10
    },
    'file': {
        'allowed_extensions': ['.txt', '.md', '.json'],
        'max_file_size': 1024 * 1024  # 1MB
    }
}
```

### Service Configuration
```python
service_config = {
    'default_num_agents': 4,
    'task_timeout': 300,  # 5 minutes
    'max_iterations': 10
}
```

## Usage Examples

### Basic Heavy Analysis
```python
from app.services.heavy_analysis import HeavyAnalysisService

service = HeavyAnalysisService()
result = await service.execute_heavy_analysis(
    "What are the environmental impacts of electric vehicles?",
    num_agents=4
)
print(result['result'])
```

### Tool Usage
```python
from app.services.heavy_analysis_tools import HeavyAnalysisToolRegistry

registry = HeavyAnalysisToolRegistry()

# Web search
search_results = await registry.execute_tool(
    'search_web', 
    query='renewable energy trends', 
    max_results=5
)

# Calculator
calc_result = await registry.execute_tool(
    'calculate', 
    expression='2 + 3 * 4'
)
```

### Enhanced Agent
```python
from app.agents.heavy_analysis_agent import HeavyAnalysisAgent

agent = HeavyAnalysisAgent('ResearchAgent', 'research_analyst')
response = await agent.process_with_tools(
    "Analyze the future of quantum computing"
)
```

## Workflow

1. **Question Generation**: AI creates 4 specialized research questions
2. **Parallel Execution**: Agents run simultaneously with different perspectives
3. **Tool Usage**: Agents use web search, calculations, and file operations
4. **Progress Tracking**: Real-time status updates for each agent
5. **Synthesis**: AI combines all perspectives into comprehensive answer

## Error Handling

- **Graceful Fallbacks**: System continues even if some agents fail
- **Provider Abstraction**: Works with any LLM provider configured in Z2
- **Tool Safety**: Secure execution with validation and restrictions
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Security Considerations

- **File Access**: Restricted to safe file types and sizes
- **Calculation Safety**: Only allows mathematical operations, prevents code execution
- **Web Requests**: Uses safe HTTP libraries with timeouts
- **Input Validation**: All API inputs are validated using Pydantic models

## Performance

- **Parallel Execution**: Multiple agents run simultaneously for faster results
- **Timeout Management**: Configurable timeouts prevent hanging operations
- **Resource Limits**: File size and result limits prevent resource exhaustion
- **Caching Integration**: Compatible with Z2's caching system

## Dependencies

New dependencies added:
- `requests`: HTTP requests for web search
- `beautifulsoup4`: HTML parsing for content extraction
- `ddgs`: DuckDuckGo search API
- `lxml`: XML/HTML parsing support

## Testing

Run the demo script to test functionality:
```bash
cd backend
python heavy_analysis_demo.py
```

The demo tests:
- Tool system functionality
- Question generation (with fallbacks)
- Agent initialization
- API schema validation

## Future Enhancements

Potential improvements:
- WebSocket support for real-time progress updates
- Additional tools (image analysis, data processing)
- Custom tool plugin system
- Advanced agent coordination patterns
- Performance optimization and caching

## Troubleshooting

### Common Issues

1. **No LLM Providers**: System falls back to default question templates
2. **Tool Failures**: Individual tool failures don't stop the overall analysis
3. **Timeout Issues**: Adjust `task_timeout` in service configuration
4. **File Access**: Ensure file paths are accessible and file types are allowed

### Debugging

Enable debug logging:
```python
import structlog
logger = structlog.get_logger(__name__)
logger.setLevel("DEBUG")
```

Check tool registry:
```python
registry = HeavyAnalysisToolRegistry()
print(f"Available tools: {list(registry.get_all_tools().keys())}")
```