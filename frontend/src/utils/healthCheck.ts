/**
 * Health check utility for API connection validation
 */

export interface HealthCheckResult {
  status: 'healthy' | 'unhealthy';
  apiUrl: string;
  protocol: string;
  errors?: string[];
  timestamp: string;
}

/**
 * Check API connection health
 */
export async function checkApiConnection(): Promise<HealthCheckResult> {
  const getApiUrl = () => {
    if (import.meta.env.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL;
    }
    
    if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
      // In production HTTPS, use HTTPS with backend domain
      return `https://${window.location.hostname.replace('z2-production', 'z2-backend-production')}`;
    }
    
    return 'http://localhost:8000';
  };

  const apiUrl = getApiUrl();
  const protocol = new URL(apiUrl).protocol;
  
  try {
    const response = await fetch(`${apiUrl}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    return {
      status: response.ok ? 'healthy' : 'unhealthy',
      apiUrl,
      protocol,
      errors: response.ok ? undefined : [`HTTP ${response.status}`],
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      apiUrl,
      protocol,
      errors: [error instanceof Error ? error.message : 'Unknown error'],
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Validate environment configuration for production
 */
export function validateEnvironmentConfig(): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check if in production environment
  const isProduction = typeof window !== 'undefined' && window.location.protocol === 'https:';
  
  if (isProduction) {
    // In production, API URL should use HTTPS
    const apiUrl = import.meta.env.VITE_API_BASE_URL;
    
    if (!apiUrl) {
      warnings.push('VITE_API_BASE_URL not set, using dynamic fallback');
    } else if (!apiUrl.startsWith('https://')) {
      errors.push('API URL must use HTTPS in production');
    }
    
    // Check WebSocket URL
    const wsUrl = import.meta.env.VITE_WS_BASE_URL;
    if (!wsUrl) {
      warnings.push('VITE_WS_BASE_URL not set');
    } else if (!wsUrl.startsWith('wss://')) {
      errors.push('WebSocket URL must use WSS in production');
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}