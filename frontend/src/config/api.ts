/**
 * API configuration with Railway-specific settings
 */

// Ensure HTTPS in production
function getApiBaseUrl(): string {
  const viteUrl = import.meta.env.VITE_API_BASE_URL;
  
  if (viteUrl) {
    // Force HTTPS in production
    if (import.meta.env.PROD && !viteUrl.startsWith('https://')) {
      console.warn('API URL should use HTTPS in production, converting...');
      return viteUrl.replace('http://', 'https://');
    }
    return viteUrl;
  }
  
  // Production fallback with correct domain
  if (import.meta.env.PROD) {
    return 'https://z2b-production.up.railway.app';
  }
  
  return 'http://localhost:8000';
}

// WebSocket URL with WSS in production
function getWsBaseUrl(): string {
  const viteWsUrl = import.meta.env.VITE_WS_BASE_URL;
  
  if (viteWsUrl) {
    // Force WSS in production
    if (import.meta.env.PROD && !viteWsUrl.startsWith('wss://')) {
      console.warn('WebSocket URL should use WSS in production, converting...');
      return viteWsUrl.replace('ws://', 'wss://');
    }
    return viteWsUrl;
  }
  
  // Production fallback
  if (import.meta.env.PROD) {
    return 'wss://z2b-production.up.railway.app';
  }
  
  return 'ws://localhost:8000';
}

export const API_CONFIG = {
  baseURL: getApiBaseUrl(),
  wsURL: getWsBaseUrl(),
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
};

export default API_CONFIG;
