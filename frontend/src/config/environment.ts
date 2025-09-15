/**
 * Unified Environment Configuration for Z2 Platform
 * 
 * This module consolidates all environment-related configuration logic
 * to eliminate duplication across the codebase (DRY principle).
 */

export interface EnvironmentConfig {
  api: {
    baseURL: string;
    wsURL: string;
    timeout: number;
    withCredentials: boolean;
    headers: Record<string, string>;
  };
  app: {
    name: string;
    version: string;
    isDev: boolean;
    isProd: boolean;
  };
  auth: {
    tokenKey: string;
  };
}

/**
 * Get the API base URL with proper protocol handling
 */
function getApiBaseUrl(): string {
  const viteUrl = import.meta.env.VITE_API_BASE_URL;
  
  if (viteUrl) {
    // Ensure HTTPS in production
    if (import.meta.env.PROD && !viteUrl.startsWith('https://')) {
      console.warn('API URL should use HTTPS in production, converting...');
      return viteUrl.replace('http://', 'https://');
    }
    return viteUrl;
  }
  
  // Development fallback
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }
  
  // Production fallback with correct domain
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    // In production HTTPS, use HTTPS with backend domain
    return `https://${window.location.hostname.replace('z2-production', 'z2-backend-production')}`;
  }
  
  // Final fallback
  console.error('VITE_API_BASE_URL not configured in production');
  return 'https://z2b-production.up.railway.app';
}

/**
 * Get the WebSocket URL with proper protocol handling
 */
function getWebSocketUrl(): string {
  const viteWsUrl = import.meta.env.VITE_WS_BASE_URL;
  
  if (viteWsUrl) {
    // Force WSS in production
    if (import.meta.env.PROD && !viteWsUrl.startsWith('wss://')) {
      console.warn('WebSocket URL should use WSS in production, converting...');
      return viteWsUrl.replace('ws://', 'wss://');
    }
    return viteWsUrl;
  }
  
  // Derive from API URL
  const apiUrl = getApiBaseUrl();
  return apiUrl.replace('https://', 'wss://').replace('http://', 'ws://');
}

/**
 * Unified environment configuration
 */
export const ENV_CONFIG: EnvironmentConfig = {
  api: {
    baseURL: getApiBaseUrl(),
    wsURL: getWebSocketUrl(),
    timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
    withCredentials: true,
    headers: {
      'Content-Type': 'application/json',
    },
  },
  app: {
    name: import.meta.env.VITE_APP_NAME || 'Z2 AI Workforce Platform',
    version: import.meta.env.VITE_APP_VERSION || '0.1.0',
    isDev: import.meta.env.DEV,
    isProd: import.meta.env.PROD,
  },
  auth: {
    tokenKey: import.meta.env.VITE_AUTH_TOKEN_KEY || 'z2_auth_token',
  },
} as const;

/**
 * Get API URL for auth endpoints (includes /api/v1 prefix)
 */
export function getAuthApiUrl(): string {
  const baseUrl = ENV_CONFIG.api.baseURL;
  return baseUrl.endsWith('/api/v1') ? baseUrl : `${baseUrl}/api/v1`;
}

/**
 * Get health check URL
 */
export function getHealthCheckUrl(): string {
  return `${ENV_CONFIG.api.baseURL}/health`;
}

/**
 * Validate environment configuration and log warnings
 */
export function validateEnvironment(): string[] {
  const warnings: string[] = [];
  
  if (!import.meta.env.VITE_API_BASE_URL) {
    warnings.push('VITE_API_BASE_URL not set, using dynamic fallback');
  }
  
  if (ENV_CONFIG.app.isProd) {
    if (!ENV_CONFIG.api.baseURL.startsWith('https://')) {
      warnings.push('API URL should use HTTPS in production');
    }
    if (!ENV_CONFIG.api.wsURL.startsWith('wss://')) {
      warnings.push('WebSocket URL should use WSS in production');
    }
  }
  
  return warnings;
}

// Legacy exports for backward compatibility
export const API_CONFIG = ENV_CONFIG.api;
export const APP_CONFIG = ENV_CONFIG.app;

export default ENV_CONFIG;