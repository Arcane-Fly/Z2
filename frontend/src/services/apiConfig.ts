// Protocol-aware API configuration
function getApiBaseUrl(): string {
  const viteUrl = import.meta.env.VITE_API_BASE_URL;
  
  if (viteUrl) {
    // Ensure HTTPS in production
    if (import.meta.env.PROD && !viteUrl.startsWith('https://')) {
      console.warn('API URL should use HTTPS in production');
      return viteUrl.replace('http://', 'https://');
    }
    return viteUrl;
  }
  
  // Development fallback 
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }
  
  // Production fallback - should not be reached if env vars are configured correctly
  console.error('VITE_API_BASE_URL not configured in production');
  return 'https://z2b-production.up.railway.app';
}

function getWebSocketUrl(): string {
  const viteWsUrl = import.meta.env.VITE_WS_BASE_URL;
  
  if (viteWsUrl) {
    return viteWsUrl;
  }
  
  // Derive from API URL
  const apiUrl = getApiBaseUrl();
  return apiUrl.replace('https://', 'wss://').replace('http://', 'ws://');
}

export const API_CONFIG = {
  baseURL: getApiBaseUrl(),
  wsURL: getWebSocketUrl(),
  timeout: 30000,
  withCredentials: true,
} as const;

export const APP_CONFIG = {
  name: import.meta.env.VITE_APP_NAME || 'Z2 AI Workforce Platform',
  version: import.meta.env.VITE_APP_VERSION || '0.1.0',
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
} as const;