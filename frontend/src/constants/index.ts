/**
 * Centralized constants for the Z2 frontend application
 * This file provides a single source of truth for configuration values,
 * API routes, and other constants used throughout the application.
 */

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_V1_PREFIX = '/api/v1';
export const API_TIMEOUT = 30000; // 30 seconds

// API Routes
export const API_ROUTES = {
  // Authentication
  AUTH: {
    LOGIN: `${API_V1_PREFIX}/auth/login`,
    LOGOUT: `${API_V1_PREFIX}/auth/logout`,
    REGISTER: `${API_V1_PREFIX}/auth/register`,
    REFRESH: `${API_V1_PREFIX}/auth/refresh`,
    ME: `${API_V1_PREFIX}/auth/me`,
  },
  
  // Users
  USERS: {
    BASE: `${API_V1_PREFIX}/users`,
    BY_ID: (id: string) => `${API_V1_PREFIX}/users/${id}`,
  },
  
  // Agents
  AGENTS: {
    BASE: `${API_V1_PREFIX}/agents`,
    BY_ID: (id: string) => `${API_V1_PREFIX}/agents/${id}`,
    EXECUTE: (id: string) => `${API_V1_PREFIX}/agents/${id}/execute`,
  },
  
  // Workflows
  WORKFLOWS: {
    BASE: `${API_V1_PREFIX}/workflows`,
    BY_ID: (id: string) => `${API_V1_PREFIX}/workflows/${id}`,
    EXECUTE: (id: string) => `${API_V1_PREFIX}/workflows/${id}/execute`,
  },
  
  // Models
  MODELS: {
    BASE: `${API_V1_PREFIX}/models`,
    BY_ID: (id: string) => `${API_V1_PREFIX}/models/${id}`,
  },
  
  // MCP
  MCP: {
    BASE: `${API_V1_PREFIX}/mcp`,
    INITIALIZE: `${API_V1_PREFIX}/mcp/initialize`,
    RESOURCES: `${API_V1_PREFIX}/mcp/resources`,
    TOOLS: `${API_V1_PREFIX}/mcp/tools`,
  },
  
  // A2A Protocol
  A2A: {
    BASE: `${API_V1_PREFIX}/a2a`,
    HANDSHAKE: `${API_V1_PREFIX}/a2a/handshake`,
    NEGOTIATE: `${API_V1_PREFIX}/a2a/negotiate`,
  },
  
  // Memory Graph
  MEMORY_GRAPH: {
    BASE: `${API_V1_PREFIX}/memory-graph`,
    QUERY: `${API_V1_PREFIX}/memory-graph/query`,
  },
  
  // Activity & Monitoring
  ACTIVITY: {
    BASE: `${API_V1_PREFIX}/activity`,
    RECENT: `${API_V1_PREFIX}/activity/recent`,
  },
  
  // Health
  HEALTH: {
    BASE: '/health',
    READY: '/health/ready',
    LIVE: '/health/live',
  },
} as const;

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'z2_auth_token',
  REFRESH_TOKEN: 'z2_refresh_token',
  THEME: 'theme',
  USER_PREFERENCES: 'user_preferences',
  SIDEBAR_STATE: 'sidebar_collapsed',
} as const;

// Theme Configuration
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
} as const;

// Agent Status
export const AGENT_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  ERROR: 'error',
} as const;

// Workflow Status
export const WORKFLOW_STATUS = {
  DRAFT: 'draft',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const;

// Loading States
export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
} as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  DEFAULT_PAGE: 1,
  MAX_PAGE_SIZE: 100,
} as const;

// Timeouts & Intervals
export const TIMEOUTS = {
  DEBOUNCE_DEFAULT: 300,
  DEBOUNCE_SEARCH: 500,
  TOAST_DURATION: 3000,
  RETRY_DELAY: 1000,
} as const;

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const;

// Validation Rules
export const VALIDATION = {
  MIN_PASSWORD_LENGTH: 8,
  MAX_PASSWORD_LENGTH: 128,
  MIN_USERNAME_LENGTH: 3,
  MAX_USERNAME_LENGTH: 50,
  // NOTE: Frontend validation is for UX only. Backend must validate all inputs for security.
  // This regex can be bypassed by malicious users, so never rely on it for security.
  EMAIL_REGEX: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
} as const;

// Feature Flags
export const FEATURES = {
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_DEBUG: import.meta.env.VITE_DEBUG === 'true',
  ENABLE_DEMO_MODE: import.meta.env.VITE_DEMO_MODE === 'true',
} as const;

// WebSocket Configuration
export const WS_CONFIG = {
  RECONNECT_INTERVAL: 5000,
  MAX_RECONNECT_ATTEMPTS: 10,
  PING_INTERVAL: 30000,
} as const;

// Date & Time Formats
export const DATE_FORMATS = {
  SHORT: 'MMM d, yyyy',
  LONG: 'MMMM d, yyyy',
  DATETIME: 'MMM d, yyyy h:mm a',
  TIME: 'h:mm a',
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  GENERIC: 'An unexpected error occurred. Please try again.',
  NETWORK: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
} as const;

// MCP Protocol
export const MCP_PROTOCOL = {
  VERSION: '2025-03-26',
  SERVER_NAME: 'Z2 AI Workforce Platform',
  SERVER_VERSION: '1.0.0',
} as const;

// Export all constants
export default {
  API_BASE_URL,
  API_V1_PREFIX,
  API_TIMEOUT,
  API_ROUTES,
  STORAGE_KEYS,
  THEMES,
  AGENT_STATUS,
  WORKFLOW_STATUS,
  LOADING_STATES,
  PAGINATION,
  TIMEOUTS,
  HTTP_STATUS,
  VALIDATION,
  FEATURES,
  WS_CONFIG,
  DATE_FORMATS,
  ERROR_MESSAGES,
  MCP_PROTOCOL,
} as const;
