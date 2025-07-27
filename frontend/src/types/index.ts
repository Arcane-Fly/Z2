/**
 * Type definitions for the Z2 platform
 */

// Re-export auth types
export * from './auth';

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: string;
  message?: string;
}

// User types (keeping existing for compatibility)
export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
  updated_at: string;
}

// Agent types
export interface Agent {
  id: string;
  name: string;
  description: string;
  type: string;
  status: 'active' | 'inactive' | 'error';
  capabilities: string[];
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Workflow types
export interface Workflow {
  id: string;
  name: string;
  description: string;
  agents: Agent[];
  status: 'draft' | 'running' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

// Authentication types (keeping existing for compatibility)
export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

// A2A Protocol types
export interface A2AHandshake {
  agent_id: string;
  capabilities: string[];
  protocol_version: string;
}

export interface A2ANegotiation {
  session_id: string;
  skills: string[];
  parameters: Record<string, any>;
}

// MCP Protocol types
export interface MCPResource {
  name: string;
  description: string;
  type: string;
  uri: string;
}

export interface MCPTool {
  name: string;
  description: string;
  input_schema: Record<string, any>;
}

// UI State types
export interface UIState {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  loading: boolean;
  errors: string[];
}

// Common types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}