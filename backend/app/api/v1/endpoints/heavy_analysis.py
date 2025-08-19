"""
Heavy Analysis API Endpoints

Provides REST API for the make-it-heavy multi-agent orchestration functionality.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import structlog

from app.core.auth_dependencies import get_current_user
from app.models.auth import User
from app.services.heavy_analysis import HeavyAnalysisService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/heavy-analysis", tags=["heavy-analysis"])


class HeavyAnalysisRequest(BaseModel):
    """Request model for heavy analysis."""
    
    query: str = Field(..., description="The query to analyze comprehensively", min_length=1, max_length=2000)
    num_agents: Optional[int] = Field(default=4, description="Number of agents to deploy", ge=2, le=8)
    

class HeavyAnalysisResponse(BaseModel):
    """Response model for heavy analysis."""
    
    task_id: str = Field(..., description="Unique identifier for this analysis task")
    result: str = Field(..., description="The comprehensive analysis result")
    execution_time: float = Field(..., description="Time taken to complete the analysis in seconds")
    num_agents: int = Field(..., description="Number of agents used")
    status: str = Field(..., description="Task status (completed, failed)")
    error: Optional[str] = Field(None, description="Error message if task failed")


class AgentResult(BaseModel):
    """Individual agent result."""
    
    agent_id: int = Field(..., description="Agent identifier")
    status: str = Field(..., description="Agent status (success, error)")
    response: str = Field(..., description="Agent response")
    execution_time: float = Field(..., description="Agent execution time in seconds")


class DetailedHeavyAnalysisResponse(HeavyAnalysisResponse):
    """Detailed response model including individual agent results."""
    
    agent_results: list[AgentResult] = Field(..., description="Individual agent results")


# Initialize the service
heavy_analysis_service = HeavyAnalysisService()


@router.post(
    "/analyze",
    response_model=HeavyAnalysisResponse,
    summary="Execute Heavy Analysis",
    description="Deploy multiple AI agents in parallel to provide comprehensive, multi-perspective analysis"
)
async def execute_heavy_analysis(
    request: HeavyAnalysisRequest,
    current_user: User = Depends(get_current_user)
) -> HeavyAnalysisResponse:
    """
    Execute heavy analysis using multiple parallel agents.
    
    This endpoint emulates "Grok Heavy" functionality by:
    1. Generating specialized research questions for the query
    2. Deploying multiple agents in parallel with different analytical perspectives
    3. Synthesizing all agent responses into a comprehensive final answer
    
    The analysis provides deep, multi-faceted insights by combining research,
    analysis, verification, and alternative perspectives.
    """
    try:
        logger.info("Heavy analysis requested", 
                   user_id=current_user.id,
                   query=request.query[:100],
                   num_agents=request.num_agents)
        
        result = await heavy_analysis_service.execute_heavy_analysis(
            user_input=request.query,
            num_agents=request.num_agents
        )
        
        return HeavyAnalysisResponse(
            task_id=result["task_id"],
            result=result["result"],
            execution_time=result["execution_time"],
            num_agents=result["num_agents"],
            status=result["status"],
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error("Heavy analysis endpoint failed", 
                    user_id=current_user.id,
                    error=str(e))
        
        raise HTTPException(
            status_code=500,
            detail=f"Heavy analysis failed: {str(e)}"
        )


@router.post(
    "/analyze/detailed",
    response_model=DetailedHeavyAnalysisResponse,
    summary="Execute Heavy Analysis (Detailed)",
    description="Execute heavy analysis with detailed agent-by-agent results"
)
async def execute_heavy_analysis_detailed(
    request: HeavyAnalysisRequest,
    current_user: User = Depends(get_current_user)
) -> DetailedHeavyAnalysisResponse:
    """
    Execute heavy analysis with detailed breakdown of individual agent results.
    
    This endpoint provides the same comprehensive analysis as the basic endpoint,
    but includes detailed information about each agent's contribution, execution
    time, and status for debugging and transparency.
    """
    try:
        logger.info("Detailed heavy analysis requested", 
                   user_id=current_user.id,
                   query=request.query[:100],
                   num_agents=request.num_agents)
        
        result = await heavy_analysis_service.execute_heavy_analysis(
            user_input=request.query,
            num_agents=request.num_agents
        )
        
        # Convert agent results to response models
        agent_results = [
            AgentResult(
                agent_id=agent["agent_id"],
                status=agent["status"],
                response=agent["response"],
                execution_time=agent["execution_time"]
            )
            for agent in result["agent_results"]
        ]
        
        return DetailedHeavyAnalysisResponse(
            task_id=result["task_id"],
            result=result["result"],
            execution_time=result["execution_time"],
            num_agents=result["num_agents"],
            status=result["status"],
            error=result.get("error"),
            agent_results=agent_results
        )
        
    except Exception as e:
        logger.error("Detailed heavy analysis endpoint failed", 
                    user_id=current_user.id,
                    error=str(e))
        
        raise HTTPException(
            status_code=500,
            detail=f"Heavy analysis failed: {str(e)}"
        )


@router.get(
    "/capabilities",
    summary="Get Heavy Analysis Capabilities",
    description="Get information about heavy analysis capabilities and configuration"
)
async def get_heavy_analysis_capabilities(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get information about heavy analysis capabilities.
    """
    return {
        "description": "Multi-agent orchestration for comprehensive analysis",
        "features": [
            "Dynamic question generation",
            "Parallel agent execution", 
            "Intelligent synthesis",
            "Real-time progress tracking",
            "Multiple analytical perspectives"
        ],
        "agent_range": {"min": 2, "max": 8},
        "default_agents": 4,
        "timeout": 300,
        "supported_query_types": [
            "Research questions",
            "Analysis requests", 
            "Information gathering",
            "Multi-perspective evaluation",
            "Fact verification",
            "Creative problem solving"
        ]
    }