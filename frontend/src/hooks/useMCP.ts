/**
 * React hooks for MCP (Model Context Protocol) integration
 * 
 * These hooks provide magical real-time capabilities for the Z2 frontend,
 * enabling dynamic resource discovery, interactive tool execution,
 * and progressive task monitoring.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState, useCallback } from 'react';
import { 
  mcpService, 
  MCPProgressUpdate
} from '../services/mcp';

/**
 * Initialize MCP session with capability negotiation
 */
export function useMCPSession() {
  return useQuery({
    queryKey: ['mcp', 'session'],
    queryFn: () => mcpService.initialize(),
    retry: 3,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Discover and monitor MCP resources dynamically
 */
export function useMCPResources() {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'resources'],
    queryFn: () => mcpService.discoverResources(),
    enabled: !!session,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

/**
 * Get specific MCP resource content with real-time updates
 */
export function useMCPResource(uri: string | undefined) {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'resource', uri],
    queryFn: () => mcpService.getResource(uri!),
    enabled: !!session && !!uri,
    refetchInterval: 15000, // Refresh every 15 seconds for real-time data
  });
}

/**
 * Discover available MCP tools
 */
export function useMCPTools() {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'tools'],
    queryFn: () => mcpService.discoverTools(),
    enabled: !!session,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Execute MCP tool with progress tracking
 */
export function useMCPToolExecution() {
  const queryClient = useQueryClient();
  const [activeExecutions, setActiveExecutions] = useState<Map<string, MCPProgressUpdate>>(new Map());

  const executeToolMutation = useMutation({
    mutationFn: async ({
      toolName,
      arguments: args,
      onProgress
    }: {
      toolName: string;
      arguments: any;
      onProgress?: (update: MCPProgressUpdate) => void;
    }) => {
      const wrappedOnProgress = (update: MCPProgressUpdate) => {
        setActiveExecutions(prev => new Map(prev.set(toolName, update)));
        onProgress?.(update);
      };

      const result = await mcpService.executeTool(toolName, args, {
        stream: !!onProgress,
        onProgress: wrappedOnProgress
      });

      // Clear progress when complete
      setActiveExecutions(prev => {
        const next = new Map(prev);
        next.delete(toolName);
        return next;
      });

      return result;
    },
    onSuccess: () => {
      // Invalidate related queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['mcp', 'resources'] });
      queryClient.invalidateQueries({ queryKey: ['mcp', 'statistics'] });
    },
  });

  return {
    ...executeToolMutation,
    activeExecutions,
  };
}

/**
 * Agent execution with real-time progress
 */
export function useMCPAgentExecution() {
  const { mutate: executeTool, ...rest } = useMCPToolExecution();
  
  const executeAgent = useCallback((
    agentId: string,
    task: string,
    parameters?: any,
    onProgress?: (update: MCPProgressUpdate) => void
  ) => {
    return executeTool({
      toolName: 'execute_agent',
      arguments: { agent_id: agentId, task, parameters },
      onProgress
    });
  }, [executeTool]);

  return {
    executeAgent,
    ...rest
  };
}

/**
 * Workflow creation with MCP
 */
export function useMCPWorkflowCreation() {
  const { mutate: executeTool, ...rest } = useMCPToolExecution();
  
  const createWorkflow = useCallback((
    name: string,
    agents: string[],
    configuration?: any,
    onProgress?: (update: MCPProgressUpdate) => void
  ) => {
    return executeTool({
      toolName: 'create_workflow',
      arguments: { name, agents, configuration },
      onProgress
    });
  }, [executeTool]);

  return {
    createWorkflow,
    ...rest
  };
}

/**
 * System analysis with MCP
 */
export function useMCPSystemAnalysis() {
  const { mutate: executeTool, ...rest } = useMCPToolExecution();
  
  const analyzeSystem = useCallback((
    scope: 'performance' | 'security' | 'usage',
    options: { timeframe?: string; detailed?: boolean } = {}
  ) => {
    return executeTool({
      toolName: 'analyze_system',
      arguments: { scope, ...options }
    });
  }, [executeTool]);

  return {
    analyzeSystem,
    ...rest
  };
}

/**
 * Discover MCP prompts
 */
export function useMCPPrompts() {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'prompts'],
    queryFn: () => mcpService.discoverPrompts(),
    enabled: !!session,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Get prompt with arguments
 */
export function useMCPPrompt(promptName: string | undefined, arguments_?: any) {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'prompt', promptName, arguments_],
    queryFn: () => mcpService.getPrompt(promptName!, arguments_),
    enabled: !!session && !!promptName,
  });
}

/**
 * Monitor active MCP sessions
 */
export function useMCPSessions() {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'sessions'],
    queryFn: () => mcpService.getSessions(),
    enabled: !!session,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

/**
 * Get MCP server statistics with real-time updates
 */
export function useMCPStatistics() {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'statistics'],
    queryFn: () => mcpService.getStatistics(),
    enabled: !!session,
    refetchInterval: 10000, // Refresh every 10 seconds for real-time stats
  });
}

/**
 * Enhanced dashboard data using MCP resources
 */
export function useMCPDashboard() {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'dashboard'],
    queryFn: () => mcpService.getDashboardData(),
    enabled: !!session,
    refetchInterval: 15000, // Refresh every 15 seconds
  });
}

/**
 * Real-time agent status from MCP resources
 */
export function useMCPAgents() {
  const defaultAgent = useMCPResource('agent://default');
  const reasoningAgent = useMCPResource('agent://reasoning');
  const codeAgent = useMCPResource('agent://code');
  
  return {
    agents: [defaultAgent.data, reasoningAgent.data, codeAgent.data].filter(Boolean),
    isLoading: defaultAgent.isLoading || reasoningAgent.isLoading || codeAgent.isLoading,
    error: defaultAgent.error || reasoningAgent.error || codeAgent.error,
    refetch: () => {
      defaultAgent.refetch();
      reasoningAgent.refetch();
      codeAgent.refetch();
    }
  };
}

/**
 * Real-time workflow status from MCP resources
 */
export function useMCPWorkflows() {
  const activeWorkflows = useMCPResource('workflow://active');
  const workflowTemplates = useMCPResource('workflow://templates');
  
  return {
    activeWorkflows: activeWorkflows.data?.content?.workflows || [],
    templates: workflowTemplates.data?.content?.templates || [],
    isLoading: activeWorkflows.isLoading || workflowTemplates.isLoading,
    error: activeWorkflows.error || workflowTemplates.error,
    refetch: () => {
      activeWorkflows.refetch();
      workflowTemplates.refetch();
    }
  };
}

/**
 * Real-time system metrics from MCP
 */
export function useMCPMetrics() {
  const systemMetrics = useMCPResource('system://metrics');
  const statistics = useMCPStatistics();
  
  const combinedMetrics = {
    system: systemMetrics.data?.content,
    server: statistics.data,
    isLoading: systemMetrics.isLoading || statistics.isLoading,
    error: systemMetrics.error || statistics.error,
    refetch: () => {
      systemMetrics.refetch();
      statistics.refetch();
    }
  };

  return combinedMetrics;
}

/**
 * Task execution monitoring
 */
export function useMCPTaskMonitor(toolName?: string, taskId?: string) {
  const { data: session } = useMCPSession();
  
  return useQuery({
    queryKey: ['mcp', 'task', toolName, taskId],
    queryFn: () => mcpService.getToolStatus(toolName!, taskId!),
    enabled: !!session && !!toolName && !!taskId,
    refetchInterval: 1000, // Very frequent updates for task monitoring
  });
}

/**
 * Cancel task execution
 */
export function useMCPTaskCancellation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ toolName, taskId }: { toolName: string; taskId: string }) =>
      mcpService.cancelTool(toolName, taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mcp', 'task'] });
    },
  });
}

/**
 * Create LLM completion using MCP sampling
 */
export function useMCPCompletion() {
  return useMutation({
    mutationFn: (request: {
      model?: string;
      messages: any[];
      max_tokens?: number;
    }) => mcpService.createMessage(request),
  });
}

/**
 * Cleanup hook for MCP session
 */
export function useMCPCleanup() {
  useEffect(() => {
    return () => {
      mcpService.close();
    };
  }, []);
}