/**
 * API service for Z2 platform
 */

import axios, { AxiosInstance } from 'axios';
import { ApiResponse, User, Agent, Workflow, AuthToken, LoginRequest } from '../types';
import API_CONFIG from '../config/api';

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: API_CONFIG.timeout,
      withCredentials: API_CONFIG.withCredentials,
      headers: API_CONFIG.headers,
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'z2_auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          localStorage.removeItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'z2_auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<AuthToken> {
    const response = await this.client.post<ApiResponse<AuthToken>>('/api/v1/auth/login', credentials);
    return response.data.data!;
  }

  async logout(): Promise<void> {
    await this.client.post('/api/v1/auth/logout');
  }

  async refreshToken(): Promise<AuthToken> {
    const refreshToken = localStorage.getItem(import.meta.env.VITE_REFRESH_TOKEN_KEY || 'z2_refresh_token');
    const response = await this.client.post<ApiResponse<AuthToken>>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data.data!;
  }

  // Users
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<ApiResponse<User>>('/api/v1/users/me');
    return response.data.data!;
  }

  // Agents
  async getAgents(): Promise<Agent[]> {
    const response = await this.client.get<ApiResponse<Agent[]>>('/api/v1/agents');
    return response.data.data!;
  }

  async getAgent(id: string): Promise<Agent> {
    const response = await this.client.get<ApiResponse<Agent>>(`/api/v1/agents/${id}`);
    return response.data.data!;
  }

  async createAgent(agent: Partial<Agent>): Promise<Agent> {
    const response = await this.client.post<ApiResponse<Agent>>('/api/v1/agents', agent);
    return response.data.data!;
  }

  async updateAgent(id: string, agent: Partial<Agent>): Promise<Agent> {
    const response = await this.client.put<ApiResponse<Agent>>(`/api/v1/agents/${id}`, agent);
    return response.data.data!;
  }

  async deleteAgent(id: string): Promise<void> {
    await this.client.delete(`/api/v1/agents/${id}`);
  }

  // Workflows
  async getWorkflows(): Promise<Workflow[]> {
    const response = await this.client.get<ApiResponse<Workflow[]>>('/api/v1/workflows');
    return response.data.data!;
  }

  async getWorkflow(id: string): Promise<Workflow> {
    const response = await this.client.get<ApiResponse<Workflow>>(`/api/v1/workflows/${id}`);
    return response.data.data!;
  }

  async createWorkflow(workflow: Partial<Workflow>): Promise<Workflow> {
    const response = await this.client.post<ApiResponse<Workflow>>('/api/v1/workflows', workflow);
    return response.data.data!;
  }

  async updateWorkflow(id: string, workflow: Partial<Workflow>): Promise<Workflow> {
    const response = await this.client.put<ApiResponse<Workflow>>(`/api/v1/workflows/${id}`, workflow);
    return response.data.data!;
  }

  async deleteWorkflow(id: string): Promise<void> {
    await this.client.delete(`/api/v1/workflows/${id}`);
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Dashboard metrics
  async getDashboardStats(): Promise<{
    activeAgents: number;
    runningWorkflows: number;
    totalCost: number;
    tokensUsed: number;
  }> {
    // Aggregate data from multiple endpoints
    const [agentsResponse, workflowsResponse] = await Promise.all([
      this.getAgents(),
      this.getWorkflows(),
    ]);

    // Calculate metrics
    const activeAgents = agentsResponse.filter(agent => agent.status === 'active').length;
    const runningWorkflows = workflowsResponse.filter(workflow => workflow.status === 'running').length;
    
    // TODO: Get real cost and token data from backend when available
    const totalCost = 0;
    const tokensUsed = 0;

    return {
      activeAgents,
      runningWorkflows,
      totalCost,
      tokensUsed,
    };
  }

  // Models
  async getModels(): Promise<any[]> {
    const response = await this.client.get<ApiResponse<any[]>>('/api/v1/models');
    return response.data.data!;
  }

  // A2A Agent discovery
  async getAgentInfo(): Promise<any> {
    const response = await this.client.get('/.well-known/agent.json');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
