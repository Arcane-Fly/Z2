/**
 * MCP (Model Context Protocol) service for Z2 platform
 * 
 * This service provides a magical interface to the MCP backend,
 * enabling real-time agent execution, dynamic resource discovery,
 * and interactive workflow management.
 */

import axios, { AxiosInstance } from 'axios';

export interface MCPResource {
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
}

export interface MCPPrompt {
  name: string;
  description: string;
  arguments?: any[];
}

export interface MCPSession {
  session_id: string;
  client_name: string;
  client_version: string;
  protocol_version: string;
  created_at: string;
  last_activity: string;
  expires_at?: string;
}

export interface MCPTaskExecution {
  task_id: string;
  tool_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: any;
  error?: string;
  can_cancel: boolean;
}

export interface MCPProgressUpdate {
  progress: number;
  total?: number;
  completed?: number;
  message?: string;
}

export interface MCPStatistics {
  timestamp: string;
  server_info: {
    name: string;
    version: string;
    protocol_version: string;
  };
  sessions: any;
  tasks: {
    running: number;
    running_tasks: Array<{
      task_id: string;
      task_name: string;
      progress: number;
      started_at?: string;
    }>;
  };
  capabilities: {
    streaming: boolean;
    cancellation: boolean;
    progress_tracking: boolean;
    session_persistence: boolean;
  };
}

class MCPService {
  private client: AxiosInstance;
  private sessionId?: string;
  private eventSources = new Map<string, EventSource>();
  
  constructor() {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1/mcp`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token if available
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('z2_auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  /**
   * Initialize MCP session with capability negotiation
   */
  async initialize(): Promise<any> {
    const initRequest = {
      protocolVersion: '2025-03-26',
      capabilities: {
        resources: { subscribe: true, listChanged: true },
        tools: { listChanged: true, progress: true, cancellation: true },
        prompts: { listChanged: true },
        sampling: {}
      },
      clientInfo: {
        name: 'Z2-Frontend',
        version: '1.0.0',
        description: 'Z2 AI Workforce Platform Frontend'
      }
    };

    const response = await this.client.post('/initialize', initRequest);
    this.sessionId = response.data.session_id;
    return response.data;
  }

  /**
   * Discover available MCP resources dynamically
   */
  async discoverResources(): Promise<MCPResource[]> {
    const response = await this.client.get('/resources', {
      params: { session_id: this.sessionId }
    });
    return response.data.resources;
  }

  /**
   * Get specific resource content
   */
  async getResource(uri: string): Promise<any> {
    const response = await this.client.get(`/resources/${encodeURIComponent(uri)}`, {
      params: { session_id: this.sessionId }
    });
    
    // Parse JSON content if it's a JSON resource
    if (response.data.mimeType === 'application/json') {
      try {
        return {
          ...response.data,
          content: JSON.parse(response.data.text)
        };
      } catch {
        return response.data;
      }
    }
    
    return response.data;
  }

  /**
   * Get available MCP tools
   */
  async discoverTools(): Promise<MCPTool[]> {
    const response = await this.client.get('/tools', {
      params: { session_id: this.sessionId }
    });
    return response.data.tools;
  }

  /**
   * Execute MCP tool with arguments
   */
  async executeTool(
    toolName: string, 
    arguments_: any, 
    options: { 
      stream?: boolean; 
      timeout?: number;
      onProgress?: (update: MCPProgressUpdate) => void;
    } = {}
  ): Promise<any> {
    const request = {
      arguments: arguments_,
      session_id: this.sessionId,
      stream: options.stream || false,
      can_cancel: true
    };

    if (options.stream && options.onProgress) {
      return this.executeStreamingTool(toolName, request, options.onProgress);
    }

    const response = await this.client.post(`/tools/${toolName}/call`, request, {
      timeout: options.timeout || 30000
    });
    
    return response.data;
  }

  /**
   * Execute tool with streaming progress updates
   */
  private async executeStreamingTool(
    toolName: string,
    request: any,
    onProgress: (update: MCPProgressUpdate) => void
  ): Promise<any> {
    const response = await this.client.post(`/tools/${toolName}/call`, request, {
      responseType: 'stream'
    });

    const taskId = response.headers['x-task-id'];
    
    // Set up EventSource for progress updates (Note: EventSource doesn't support custom headers)
    const baseUrl = this.client.defaults.baseURL?.replace('/api/v1/mcp', '');
    const eventSourceUrl = `${baseUrl}/api/v1/mcp/tools/${toolName}/call`;
    const eventSource = new EventSource(eventSourceUrl);

    this.eventSources.set(taskId, eventSource);

    return new Promise((resolve, reject) => {
      eventSource.onmessage = (event) => {
        try {
          const update = JSON.parse(event.data);
          onProgress(update);
          
          if (update.progress >= 1.0) {
            eventSource.close();
            this.eventSources.delete(taskId);
            resolve(update);
          }
        } catch (error) {
          reject(error);
        }
      };

      eventSource.onerror = (error) => {
        eventSource.close();
        this.eventSources.delete(taskId);
        reject(error);
      };
    });
  }

  /**
   * Cancel a running tool execution
   */
  async cancelTool(toolName: string, taskId: string): Promise<any> {
    const response = await this.client.post(`/tools/${toolName}/cancel`, { task_id: taskId });
    return response.data;
  }

  /**
   * Get tool execution status
   */
  async getToolStatus(toolName: string, taskId: string): Promise<MCPTaskExecution> {
    const response = await this.client.get(`/tools/${toolName}/status/${taskId}`);
    return response.data;
  }

  /**
   * Get available MCP prompts
   */
  async discoverPrompts(): Promise<MCPPrompt[]> {
    const response = await this.client.get('/prompts', {
      params: { session_id: this.sessionId }
    });
    return response.data.prompts;
  }

  /**
   * Get prompt with arguments
   */
  async getPrompt(promptName: string, arguments_?: any): Promise<any> {
    const response = await this.client.get(`/prompts/${promptName}`, {
      params: { 
        session_id: this.sessionId,
        arguments: arguments_ ? JSON.stringify(arguments_) : undefined
      }
    });
    return response.data;
  }

  /**
   * Get active MCP sessions
   */
  async getSessions(): Promise<MCPSession[]> {
    const response = await this.client.get('/sessions');
    return response.data.sessions;
  }

  /**
   * Get MCP server statistics
   */
  async getStatistics(): Promise<MCPStatistics> {
    const response = await this.client.get('/statistics');
    return response.data;
  }

  /**
   * Create sampling request (LLM completion)
   */
  async createMessage(request: {
    model?: string;
    messages: any[];
    max_tokens?: number;
  }): Promise<any> {
    const response = await this.client.post('/sampling/createMessage', {
      ...request,
      session_id: this.sessionId
    });
    return response.data;
  }

  /**
   * Real-time agent execution with progress tracking
   */
  async executeAgent(
    agentId: string,
    task: string,
    parameters?: any,
    onProgress?: (update: MCPProgressUpdate) => void
  ): Promise<any> {
    return this.executeTool('execute_agent', {
      agent_id: agentId,
      task,
      parameters: parameters || {},
      stream: !!onProgress
    }, {
      stream: !!onProgress,
      onProgress
    });
  }

  /**
   * Create workflow with MCP
   */
  async createWorkflow(
    name: string,
    agents: string[],
    configuration?: any,
    onProgress?: (update: MCPProgressUpdate) => void
  ): Promise<any> {
    return this.executeTool('create_workflow', {
      name,
      agents,
      configuration: configuration || {},
      stream: !!onProgress
    }, {
      stream: !!onProgress,
      onProgress
    });
  }

  /**
   * Analyze system performance
   */
  async analyzeSystem(
    scope: 'performance' | 'security' | 'usage',
    options: {
      timeframe?: string;
      detailed?: boolean;
    } = {}
  ): Promise<any> {
    return this.executeTool('analyze_system', {
      scope,
      timeframe: options.timeframe || '1h',
      detailed: options.detailed || false
    });
  }

  /**
   * Get real-time dashboard data using MCP resources
   */
  async getDashboardData(): Promise<{
    agents: any[];
    workflows: any[];
    metrics: any;
    activity: any[];
  }> {
    const [agentResource, workflowResource, metricsResource] = await Promise.all([
      this.getResource('agent://default'),
      this.getResource('workflow://active'), 
      this.getResource('system://metrics')
    ]);

    return {
      agents: [agentResource.content],
      workflows: workflowResource.content?.workflows || [],
      metrics: metricsResource.content,
      activity: [] // TODO: Get from activity resource
    };
  }

  /**
   * Close session and cleanup
   */
  async close(): Promise<void> {
    // Close all event sources
    this.eventSources.forEach(eventSource => eventSource.close());
    this.eventSources.clear();

    // Close MCP session
    if (this.sessionId) {
      try {
        await this.client.delete(`/sessions/${this.sessionId}`);
      } catch (error) {
        console.warn('Error closing MCP session:', error);
      }
      this.sessionId = undefined;
    }
  }
}

// Export singleton instance
export const mcpService = new MCPService();
export default mcpService;