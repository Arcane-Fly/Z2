"""
Heavy Analysis Service for Z2 AI Workforce Platform

Integrates the make-it-heavy multi-agent orchestration framework with Z2's 
existing Model Integration Layer (MIL) and Multi-Agent Orchestration Framework (MAOF).
"""

import asyncio
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional
from uuid import uuid4

import structlog

from app.agents.basic_agent import BasicAIAgent
from app.agents.mil import ModelIntegrationLayer, LLMRequest, RoutingPolicy
from app.core.config import settings

logger = structlog.get_logger(__name__)


class HeavyAnalysisProgress:
    """Thread-safe progress tracking for heavy analysis tasks."""
    
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.agent_progress = {}
        self.agent_results = {}
        self.progress_lock = threading.Lock()
        self.start_time = time.time()
        
        # Initialize progress tracking
        for i in range(num_agents):
            self.agent_progress[i] = "QUEUED"
    
    def update_agent_progress(self, agent_id: int, status: str, result: str = None):
        """Thread-safe progress update."""
        with self.progress_lock:
            self.agent_progress[agent_id] = status
            if result is not None:
                self.agent_results[agent_id] = result
    
    def get_progress_status(self) -> Dict[int, str]:
        """Get current progress status for all agents."""
        with self.progress_lock:
            return self.agent_progress.copy()
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since task started."""
        return time.time() - self.start_time


class HeavyAnalysisService:
    """
    Heavy Analysis Service that orchestrates multiple agents for comprehensive analysis.
    
    Integrates make-it-heavy functionality with Z2's existing infrastructure:
    - Uses Z2's MIL for LLM provider abstraction
    - Leverages BasicAIAgent for individual agent execution
    - Follows Z2's patterns for error handling and logging
    """
    
    def __init__(self):
        self.mil = ModelIntegrationLayer()
        
        # Configuration (these could be moved to app config)
        self.default_num_agents = 4
        self.task_timeout = 300  # 5 minutes
        self.question_generation_prompt = """You are an orchestrator that needs to create {num_agents} different questions to thoroughly analyze this topic from multiple angles.

Original user query: {user_input}

Generate exactly {num_agents} different, specific questions that will help gather comprehensive information about this topic.
Each question should approach the topic from a different angle (research, analysis, verification, alternatives, etc.).

Return your response as a JSON array of strings, like this:
["question 1", "question 2", "question 3", "question 4"]

Only return the JSON array, nothing else."""

        self.synthesis_prompt = """You have {num_responses} different AI agents that analyzed the same query from different perspectives. 
Your job is to synthesize their responses into ONE comprehensive final answer.

Here are all the agent responses:

{agent_responses}

IMPORTANT: Just synthesize these into ONE final comprehensive answer that combines the best information from all agents. 
Do NOT mention that you are synthesizing multiple responses. 
Simply provide the final synthesized answer directly as your response."""

    async def decompose_task(self, user_input: str, num_agents: int) -> List[str]:
        """
        Use AI to dynamically generate different questions based on user input.
        Adapts make-it-heavy's question generation to use Z2's MIL.
        """
        try:
            # Create a request for question generation
            generation_prompt = self.question_generation_prompt.format(
                user_input=user_input,
                num_agents=num_agents
            )
            
            request = LLMRequest(
                prompt=generation_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Use MIL to route to optimal model for question generation
            routing_policy = RoutingPolicy(
                cost_weight=0.3,
                quality_weight=0.7,
                max_cost_per_request=0.01
            )
            
            response = await self.mil.generate_response(request, routing_policy)
            
            # Parse JSON response
            questions = json.loads(response.content.strip())
            
            # Validate we got the right number of questions
            if len(questions) != num_agents:
                raise ValueError(f"Expected {num_agents} questions, got {len(questions)}")
            
            logger.info("Generated questions for heavy analysis", 
                       num_questions=len(questions), 
                       user_input=user_input[:100])
            
            return questions
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("Question generation failed, using fallback", error=str(e))
            # Fallback: create simple variations if AI fails
            return [
                f"Research comprehensive information about: {user_input}",
                f"Analyze and provide insights about: {user_input}",
                f"Find alternative perspectives on: {user_input}",
                f"Verify and cross-check facts about: {user_input}"
            ][:num_agents]

    async def run_agent_async(self, agent_id: int, subtask: str, progress: HeavyAnalysisProgress) -> Dict[str, Any]:
        """
        Run a single agent with the given subtask using Z2's BasicAIAgent.
        """
        try:
            progress.update_agent_progress(agent_id, "INITIALIZING...")
            
            # Create a specialized agent for this subtask
            agent = BasicAIAgent(
                agent_name=f"HeavyAnalysis-Agent-{agent_id}",
                role="research_analyst"
            )
            
            progress.update_agent_progress(agent_id, "PROCESSING...")
            
            start_time = time.time()
            
            # Execute the subtask using process_message method
            response = await agent.process_message(subtask)
            
            execution_time = time.time() - start_time
            
            progress.update_agent_progress(agent_id, "COMPLETED", response)
            
            logger.info("Agent completed task", 
                       agent_id=agent_id, 
                       execution_time=execution_time,
                       response_length=len(response) if response else 0)
            
            return {
                "agent_id": agent_id,
                "status": "success", 
                "response": response,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error("Agent failed", agent_id=agent_id, error=str(e))
            progress.update_agent_progress(agent_id, f"FAILED: {str(e)}")
            
            return {
                "agent_id": agent_id,
                "status": "error",
                "response": f"Error: {str(e)}",
                "execution_time": 0
            }

    async def aggregate_results(self, agent_results: List[Dict[str, Any]]) -> str:
        """
        Combine results from all agents into a comprehensive final answer using Z2's MIL.
        """
        successful_results = [r for r in agent_results if r["status"] == "success"]
        
        if not successful_results:
            return "All agents failed to provide results. Please try again."
        
        # Extract responses for aggregation
        responses = [r["response"] for r in successful_results]
        
        if len(responses) == 1:
            return responses[0]
        
        # Build agent responses section
        agent_responses_text = ""
        for i, response in enumerate(responses, 1):
            agent_responses_text += f"=== AGENT {i} RESPONSE ===\n{response}\n\n"
        
        # Format synthesis prompt
        synthesis_prompt = self.synthesis_prompt.format(
            num_responses=len(responses),
            agent_responses=agent_responses_text
        )
        
        try:
            # Use MIL for synthesis
            request = LLMRequest(
                prompt=synthesis_prompt,
                temperature=0.5,
                max_tokens=2000
            )
            
            routing_policy = RoutingPolicy(
                cost_weight=0.2,
                quality_weight=0.8,
                max_cost_per_request=0.05
            )
            
            response = await self.mil.generate_response(request, routing_policy)
            
            logger.info("Synthesis completed", 
                       num_responses=len(responses),
                       final_length=len(response.content))
            
            return response.content
            
        except Exception as e:
            logger.error("Synthesis failed", error=str(e))
            
            # Fallback: concatenate responses
            combined = []
            for i, response in enumerate(responses, 1):
                combined.append(f"=== Agent {i} Response ===")
                combined.append(response)
                combined.append("")
            return "\n".join(combined)

    async def execute_heavy_analysis(
        self, 
        user_input: str, 
        num_agents: Optional[int] = None,
        callback=None
    ) -> Dict[str, Any]:
        """
        Main orchestration method for heavy analysis.
        
        Args:
            user_input: The query to analyze
            num_agents: Number of agents to deploy (default: 4)
            callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing the analysis result and metadata
        """
        if num_agents is None:
            num_agents = self.default_num_agents
        
        task_id = str(uuid4())
        start_time = time.time()
        
        logger.info("Starting heavy analysis", 
                   task_id=task_id,
                   user_input=user_input[:100], 
                   num_agents=num_agents)
        
        try:
            # Initialize progress tracking
            progress = HeavyAnalysisProgress(num_agents)
            
            # Decompose task into subtasks
            subtasks = await self.decompose_task(user_input, num_agents)
            
            # Execute agents in parallel using asyncio
            agent_tasks = []
            for i in range(num_agents):
                task = self.run_agent_async(i, subtasks[i], progress)
                agent_tasks.append(task)
            
            # Wait for all agents to complete
            agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            
            # Process any exceptions
            processed_results = []
            for i, result in enumerate(agent_results):
                if isinstance(result, Exception):
                    logger.error("Agent task failed", agent_id=i, error=str(result))
                    processed_results.append({
                        "agent_id": i,
                        "status": "error",
                        "response": f"Agent {i} failed: {str(result)}",
                        "execution_time": 0
                    })
                else:
                    processed_results.append(result)
            
            # Sort results by agent_id for consistent output
            processed_results.sort(key=lambda x: x["agent_id"])
            
            # Aggregate results
            final_result = await self.aggregate_results(processed_results)
            
            execution_time = time.time() - start_time
            
            logger.info("Heavy analysis completed", 
                       task_id=task_id,
                       execution_time=execution_time,
                       num_successful=len([r for r in processed_results if r["status"] == "success"]),
                       final_length=len(final_result))
            
            return {
                "task_id": task_id,
                "result": final_result,
                "execution_time": execution_time,
                "num_agents": num_agents,
                "agent_results": processed_results,
                "status": "completed"
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error("Heavy analysis failed", 
                        task_id=task_id, 
                        error=str(e),
                        execution_time=execution_time)
            
            return {
                "task_id": task_id,
                "result": f"Heavy analysis failed: {str(e)}",
                "execution_time": execution_time,
                "num_agents": num_agents,
                "agent_results": [],
                "status": "failed",
                "error": str(e)
            }