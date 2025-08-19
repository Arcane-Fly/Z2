"""
Tool System for Heavy Analysis Agents

Integrates make-it-heavy tool capabilities with Z2's MCP framework.
Provides web search, file operations, calculations, and other utilities.
"""

import asyncio
import json
import os
import ast
import operator
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
import structlog

logger = structlog.get_logger(__name__)


class HeavyAnalysisTool(ABC):
    """Base class for heavy analysis tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for function calling."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Function parameters schema."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    def to_function_schema(self) -> Dict[str, Any]:
        """Convert tool to function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class WebSearchTool(HeavyAnalysisTool):
    """Web search tool using DuckDuckGo."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.user_agent = self.config.get('user_agent', 'Mozilla/5.0 (compatible; Z2-HeavyAnalysis)')
        self.timeout = self.config.get('timeout', 10)
    
    @property
    def name(self) -> str:
        return "search_web"
    
    @property
    def description(self) -> str:
        return "Search the web using DuckDuckGo for current information and research"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find information on the web"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web and fetch page content."""
        try:
            logger.info("Executing web search", query=query, max_results=max_results)
            
            # Use ddgs library for search
            ddgs = DDGS()
            search_results = ddgs.text(query, max_results=max_results)
            
            results = []
            
            for result in search_results:
                try:
                    # Fetch content with requests
                    response = requests.get(
                        result['href'], 
                        headers={'User-Agent': self.user_agent},
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    
                    # Parse HTML with BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text()
                    # Clean up whitespace
                    text = ' '.join(text.split())
                    
                    # Limit content length to avoid token limits
                    content_snippet = text[:1500] + "..." if len(text) > 1500 else text
                    
                    results.append({
                        "title": result['title'],
                        "url": result['href'],
                        "snippet": result['body'],
                        "content": content_snippet
                    })
                
                except Exception as e:
                    # If we can't fetch the page, still include the search result
                    logger.warning("Failed to fetch page content", url=result.get('href'), error=str(e))
                    results.append({
                        "title": result['title'],
                        "url": result['href'],
                        "snippet": result['body'],
                        "content": f"Could not fetch content: {str(e)}"
                    })
            
            logger.info("Web search completed", query=query, results_count=len(results))
            return results
        
        except Exception as e:
            logger.error("Web search failed", query=query, error=str(e))
            return [{"error": f"Search failed: {str(e)}"}]


class CalculatorTool(HeavyAnalysisTool):
    """Safe mathematical calculation tool."""
    
    # Allowed operators for safe evaluation
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
    }
    
    @property
    def name(self) -> str:
        return "calculate"
    
    @property
    def description(self) -> str:
        return "Perform safe mathematical calculations and evaluate expressions"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4', '10 ** 2', 'sqrt(16)')"
                }
            },
            "required": ["expression"]
        }
    
    def _safe_eval(self, node):
        """Safely evaluate a mathematical expression."""
        if isinstance(node, ast.Constant):  # Numbers
            return node.value
        elif isinstance(node, ast.BinOp):  # Binary operations
            left = self._safe_eval(node.left)
            right = self._safe_eval(node.right)
            if type(node.op) in self.ALLOWED_OPERATORS:
                return self.ALLOWED_OPERATORS[type(node.op)](left, right)
            else:
                raise ValueError(f"Unsupported operation: {type(node.op).__name__}")
        elif isinstance(node, ast.UnaryOp):  # Unary operations
            operand = self._safe_eval(node.operand)
            if type(node.op) in self.ALLOWED_OPERATORS:
                return self.ALLOWED_OPERATORS[type(node.op)](operand)
            else:
                raise ValueError(f"Unsupported unary operation: {type(node.op).__name__}")
        elif isinstance(node, ast.Call):  # Function calls
            if node.func.id == 'sqrt' and len(node.args) == 1:
                import math
                return math.sqrt(self._safe_eval(node.args[0]))
            elif node.func.id == 'abs' and len(node.args) == 1:
                return abs(self._safe_eval(node.args[0]))
            elif node.func.id == 'round' and len(node.args) >= 1:
                if len(node.args) == 1:
                    return round(self._safe_eval(node.args[0]))
                else:
                    return round(self._safe_eval(node.args[0]), self._safe_eval(node.args[1]))
            else:
                raise ValueError(f"Unsupported function: {node.func.id}")
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")
    
    async def execute(self, expression: str) -> Dict[str, Any]:
        """Safely evaluate a mathematical expression."""
        try:
            logger.info("Calculating expression", expression=expression)
            
            # Parse the expression
            node = ast.parse(expression, mode='eval')
            
            # Evaluate safely
            result = self._safe_eval(node.body)
            
            logger.info("Calculation completed", expression=expression, result=result)
            
            return {
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
        
        except Exception as e:
            logger.error("Calculation failed", expression=expression, error=str(e))
            return {
                "expression": expression,
                "error": f"Calculation failed: {str(e)}",
                "result": None
            }


class FileReadTool(HeavyAnalysisTool):
    """File reading tool with safety restrictions."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.allowed_extensions = self.config.get('allowed_extensions', ['.txt', '.md', '.json', '.yaml', '.yml', '.csv'])
        self.max_file_size = self.config.get('max_file_size', 1024 * 1024)  # 1MB default
    
    @property
    def name(self) -> str:
        return "read_file"
    
    @property
    def description(self) -> str:
        return "Read contents of a text file (limited to safe file types and sizes)"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read"
                },
                "head": {
                    "type": "integer",
                    "description": "Number of lines to read from the beginning (optional)",
                    "minimum": 1
                },
                "tail": {
                    "type": "integer",
                    "description": "Number of lines to read from the end (optional)",
                    "minimum": 1
                }
            },
            "required": ["path"]
        }
    
    async def execute(self, path: str, head: Optional[int] = None, tail: Optional[int] = None) -> Dict[str, Any]:
        """Read file contents with safety checks."""
        try:
            logger.info("Reading file", path=path, head=head, tail=tail)
            
            # Security checks
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}
            
            if not os.path.isfile(path):
                return {"error": f"Path is not a file: {path}"}
            
            # Check file extension
            _, ext = os.path.splitext(path)
            if ext.lower() not in self.allowed_extensions:
                return {"error": f"File type not allowed: {ext}. Allowed: {self.allowed_extensions}"}
            
            # Check file size
            file_size = os.path.getsize(path)
            if file_size > self.max_file_size:
                return {"error": f"File too large: {file_size} bytes. Max: {self.max_file_size} bytes"}
            
            # Read file
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply head/tail filters
            if head is not None:
                lines = lines[:head]
            elif tail is not None:
                lines = lines[-tail:]
            
            content = ''.join(lines)
            
            logger.info("File read successfully", path=path, lines_count=len(lines), content_length=len(content))
            
            return {
                "path": path,
                "content": content,
                "lines_count": len(lines),
                "file_size": file_size
            }
        
        except Exception as e:
            logger.error("File read failed", path=path, error=str(e))
            return {"error": f"Failed to read file: {str(e)}"}


class TaskCompletionTool(HeavyAnalysisTool):
    """Tool to signal task completion (adapted from make-it-heavy)."""
    
    @property
    def name(self) -> str:
        return "mark_task_complete"
    
    @property
    def description(self) -> str:
        return "Mark the current task as complete with a summary of what was accomplished"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_summary": {
                    "type": "string",
                    "description": "Brief summary of what was accomplished"
                },
                "completion_message": {
                    "type": "string",
                    "description": "Final message or answer for the user"
                }
            },
            "required": ["task_summary", "completion_message"]
        }
    
    async def execute(self, task_summary: str, completion_message: str) -> Dict[str, Any]:
        """Mark task as complete."""
        logger.info("Task marked as complete", summary=task_summary[:100])
        
        return {
            "status": "completed",
            "summary": task_summary,
            "message": completion_message,
            "timestamp": asyncio.get_event_loop().time()
        }


class HeavyAnalysisToolRegistry:
    """Registry for heavy analysis tools."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools."""
        try:
            # Initialize core tools
            self.tools['search_web'] = WebSearchTool(self.config.get('search', {}))
            self.tools['calculate'] = CalculatorTool()
            self.tools['read_file'] = FileReadTool(self.config.get('file', {}))
            self.tools['mark_task_complete'] = TaskCompletionTool()
            
            logger.info("Heavy analysis tools initialized", count=len(self.tools), tools=list(self.tools.keys()))
        
        except Exception as e:
            logger.error("Failed to initialize tools", error=str(e))
    
    def get_tool(self, name: str) -> Optional[HeavyAnalysisTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, HeavyAnalysisTool]:
        """Get all registered tools."""
        return self.tools.copy()
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get function schemas for all tools."""
        return [tool.to_function_schema() for tool in self.tools.values()]
    
    async def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")
        
        return await tool.execute(**kwargs)