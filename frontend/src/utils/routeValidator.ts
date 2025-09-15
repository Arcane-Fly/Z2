import { ENV_CONFIG } from '../config/environment';

const API_ROUTES = [
  '/api/v1/auth/login',
  '/api/v1/auth/register', 
  '/api/v1/auth/logout',
  '/api/v1/users/me',
  '/api/v1/agents',
  '/api/v1/workflows',
  '/api/v1/models',
  '/health'
];

export interface RouteValidationResult {
  route: string;
  available: boolean;
  status?: number;
  error?: string;
}

export async function validateRoute(route: string): Promise<RouteValidationResult> {
  try {
    const response = await fetch(`${ENV_CONFIG.api.baseURL}${route}`, {
      method: 'OPTIONS',
      headers: { 
        ...ENV_CONFIG.api.headers,
        'Origin': window.location.origin 
      },
      credentials: ENV_CONFIG.api.withCredentials ? 'include' : 'omit'
    });
    
    return {
      route,
      available: response.ok,
      status: response.status
    };
  } catch (error) {
    return {
      route,
      available: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

export async function validateAllRoutes(): Promise<Map<string, RouteValidationResult>> {
  const results = new Map<string, RouteValidationResult>();
  
  const validationPromises = API_ROUTES.map(async (route) => {
    const result = await validateRoute(route);
    results.set(route, result);
    return result;
  });
  
  await Promise.all(validationPromises);
  return results;
}

export async function validateAPIConnection(): Promise<{
  connected: boolean;
  baseURL: string;
  healthStatus?: any;
  error?: string;
}> {
  try {
    const response = await fetch(`${ENV_CONFIG.api.baseURL}/health`, {
      method: 'GET',
      headers: ENV_CONFIG.api.headers,
      credentials: ENV_CONFIG.api.withCredentials ? 'include' : 'omit',
      // Short timeout for health check
      signal: AbortSignal.timeout(5000)
    });

    if (response.ok) {
      const healthData = await response.json();
      return {
        connected: true,
        baseURL: ENV_CONFIG.api.baseURL,
        healthStatus: healthData
      };
    } else {
      return {
        connected: false,
        baseURL: ENV_CONFIG.api.baseURL,
        error: `Health check failed with status ${response.status}`
      };
    }
  } catch (error) {
    return {
      connected: false,
      baseURL: ENV_CONFIG.api.baseURL,
      error: error instanceof Error ? error.message : 'Connection failed'
    };
  }
}