"""
Heavy Analysis Agent with Tool Support

Enhanced agent that integrates make-it-heavy tool capabilities with Z2's BasicAIAgent.
Provides multi-step reasoning and tool execution for comprehensive analysis.
"""

import json
from typing import Any, Dict, List, Optional

import structlog

from app.agents.basic_agent import BasicAIAgent
from app.agents.mil import LLMRequest, RoutingPolicy
from app.services.heavy_analysis_tools import HeavyAnalysisToolRegistry

logger = structlog.get_logger(__name__)


class HeavyAnalysisAgent(BasicAIAgent):
    """
    Enhanced agent for heavy analysis with tool support.
    
    Extends BasicAIAgent to include:
    - Tool execution capabilities
    - Multi-step reasoning loops
    - Task completion detection
    """
    
    def __init__(self, agent_name: str, role: str = "research_analyst", config: Optional[Dict] = None):
        super().__init__(agent_name, role)
        
        # Initialize tools
        self.tool_registry = HeavyAnalysisToolRegistry(config)
        self.tools = self.tool_registry.get_all_tools()
        self.function_schemas = self.tool_registry.get_function_schemas()
        
        # Agent configuration
        self.max_iterations = 10
        self.tool_enabled = True
        
        logger.info("Heavy analysis agent initialized", 
                   agent_name=agent_name, 
                   role=role, 
                   tools_count=len(self.tools))
    
    def _create_system_prompt(self) -> str:
        """Create enhanced system prompt with tool instructions."""
        tools_description = ""
        if self.tool_enabled and self.function_schemas:
            tool_names = [schema["function"]["name"] for schema in self.function_schemas]
            tools_description = f"""

Available Tools:
{', '.join(tool_names)}

When you need to gather information, perform calculations, read files, or complete other tasks, use the appropriate tools. 
Always use search_web for current information and research queries.
Use calculate for mathematical operations.
Use read_file for accessing file contents.
When you have fully completed the task and provided a comprehensive answer, use mark_task_complete."""

        return f"""You are {self.name}, a {self.role} specializing in comprehensive research and analysis.

Your role is to:
1. Thoroughly analyze the given task or question
2. Use available tools to gather information and perform analysis
3. Provide detailed, well-researched responses
4. Combine multiple sources and perspectives
5. Verify information when possible
6. Mark tasks as complete when fully satisfied

{tools_description}

Always think step by step and be thorough in your analysis. Provide comprehensive responses that combine multiple perspectives and sources when available."""

    async def process_with_tools(self, user_input: str, max_iterations: Optional[int] = None) -> str:
        """
        Process a request using tool-enhanced multi-step reasoning.
        
        This method implements the core heavy analysis loop:
        1. Generate initial response
        2. Check if tools are needed
        3. Execute tools and incorporate results
        4. Continue until task is complete or max iterations reached
        """
        if max_iterations is None:
            max_iterations = self.max_iterations
        
        # Initialize conversation with system prompt and user input
        messages = [
            {"role": "system", "content": self._create_system_prompt()},
            {"role": "user", "content": user_input}
        ]
        
        # Track accumulated responses for comprehensive output
        accumulated_responses = []
        
        for iteration in range(max_iterations):
            logger.debug("Heavy analysis iteration", 
                        agent=self.name, 
                        iteration=iteration + 1, 
                        max_iterations=max_iterations)
            
            try:
                # Create LLM request with tool schemas
                llm_request = LLMRequest(
                    prompt=self._format_messages_as_prompt(messages),
                    temperature=0.7,
                    max_tokens=2000,
                    # Note: Tool schemas would be passed here in a full implementation
                    # For now, we'll simulate tool calling in the response
                )
                
                # Route to optimal model
                routing_policy = RoutingPolicy(
                    cost_weight=0.3,
                    quality_weight=0.7,
                    max_cost_per_request=0.02
                )
                
                # Generate response
                response = await self.mil.generate_response(llm_request, routing_policy)
                assistant_content = response.content
                
                # Add to accumulated responses
                if assistant_content:
                    accumulated_responses.append(assistant_content)
                
                # Check if response contains tool calls (simulated)
                tool_calls = self._extract_tool_calls(assistant_content)
                
                if tool_calls:
                    # Execute tools and add results to conversation
                    tool_results = []
                    
                    for tool_call in tool_calls:
                        try:
                            result = await self.tool_registry.execute_tool(
                                tool_call["name"], 
                                **tool_call["arguments"]
                            )
                            tool_results.append({
                                "tool": tool_call["name"],
                                "result": result
                            })
                            
                            logger.info("Tool executed", 
                                       agent=self.name,
                                       tool=tool_call["name"],
                                       success=True)
                        
                        except Exception as e:
                            error_result = {"error": f"Tool execution failed: {str(e)}"}
                            tool_results.append({
                                "tool": tool_call["name"],
                                "result": error_result
                            })
                            
                            logger.error("Tool execution failed", 
                                        agent=self.name,
                                        tool=tool_call["name"],
                                        error=str(e))
                    
                    # Add tool results to conversation
                    if tool_results:
                        tool_summary = self._format_tool_results(tool_results)
                        messages.append({"role": "assistant", "content": assistant_content})
                        messages.append({"role": "user", "content": f"Tool results:\n{tool_summary}\n\nPlease continue your analysis with this information."})
                    
                    # Check if task completion was called
                    completion_calls = [tc for tc in tool_calls if tc["name"] == "mark_task_complete"]
                    if completion_calls:
                        logger.info("Task completion detected", agent=self.name, iteration=iteration + 1)
                        break
                
                else:
                    # No tool calls, add response and continue
                    messages.append({"role": "assistant", "content": assistant_content})
                    
                    # Check if response seems complete (fallback)
                    if self._is_response_complete(assistant_content):
                        logger.info("Response appears complete", agent=self.name, iteration=iteration + 1)
                        break
            
            except Exception as e:
                logger.error("Error in heavy analysis iteration", 
                           agent=self.name, 
                           iteration=iteration + 1, 
                           error=str(e))
                accumulated_responses.append(f"Error in analysis: {str(e)}")
                break
        
        # Return accumulated responses
        final_response = "\n\n".join(accumulated_responses) if accumulated_responses else "Analysis could not be completed."
        
        logger.info("Heavy analysis completed", 
                   agent=self.name, 
                   iterations=iteration + 1,
                   response_length=len(final_response))
        
        return final_response
    
    def _format_messages_as_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format message list as a single prompt."""
        formatted = []
        for msg in messages:
            role = msg["role"].title()
            content = msg["content"]
            formatted.append(f"{role}: {content}")
        
        return "\n\n".join(formatted)
    
    def _extract_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls from response content.
        
        This is a simplified implementation that looks for tool call patterns.
        In a full implementation, this would use the LLM's function calling features.
        """
        tool_calls = []
        
        # Simple pattern matching for tool calls
        # Look for patterns like "search_web(query='...')" or "calculate(expression='...')"
        import re
        
        # Pattern for tool calls
        pattern = r'(\w+)\s*\(\s*(.+?)\s*\)'
        matches = re.findall(pattern, content)
        
        for tool_name, args_str in matches:
            if tool_name in self.tools:
                try:
                    # Simple argument parsing (this could be more sophisticated)
                    args = {}
                    # Handle simple key=value patterns
                    arg_pattern = r'(\w+)=[\'"]([^\'"]*)[\'"]'
                    arg_matches = re.findall(arg_pattern, args_str)
                    
                    for key, value in arg_matches:
                        args[key] = value
                    
                    if args:  # Only add if we found arguments
                        tool_calls.append({
                            "name": tool_name,
                            "arguments": args
                        })
                
                except Exception as e:
                    logger.warning("Failed to parse tool call", 
                                 tool_name=tool_name, 
                                 args_str=args_str, 
                                 error=str(e))
        
        return tool_calls
    
    def _format_tool_results(self, tool_results: List[Dict[str, Any]]) -> str:
        """Format tool results for inclusion in conversation."""
        formatted = []
        
        for tr in tool_results:
            tool_name = tr["tool"]
            result = tr["result"]
            
            if isinstance(result, dict) and "error" in result:
                formatted.append(f"{tool_name}: ERROR - {result['error']}")
            elif isinstance(result, list) and len(result) > 0:
                # For search results
                formatted.append(f"{tool_name}: Found {len(result)} results")
                for i, item in enumerate(result[:3], 1):  # Show first 3 results
                    if isinstance(item, dict):
                        title = item.get('title', 'Unknown')
                        snippet = item.get('snippet', item.get('content', ''))[:200]
                        formatted.append(f"  {i}. {title}: {snippet}")
            else:
                formatted.append(f"{tool_name}: {str(result)[:500]}")
        
        return "\n".join(formatted)
    
    def _is_response_complete(self, content: str) -> bool:
        """Check if response appears to be complete."""
        # Simple heuristics for completion
        completion_indicators = [
            "in conclusion",
            "to summarize", 
            "in summary",
            "final analysis",
            "complete analysis",
            "comprehensive overview"
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in completion_indicators)
    
    async def process_message(self, user_message: str, **kwargs) -> str:
        """
        Override process_message to use tool-enhanced processing.
        """
        if self.tool_enabled:
            return await self.process_with_tools(user_message)
        else:
            # Fall back to basic processing
            return await super().process_message(user_message, **kwargs)