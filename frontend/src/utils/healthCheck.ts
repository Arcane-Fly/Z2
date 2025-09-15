/**
 * Health check utility for API connection validation - Refactored with DRY principles
 */

import { ENV_CONFIG, getHealthCheckUrl, validateEnvironment } from '../config/environment';

export interface HealthCheckResult {
  status: 'healthy' | 'unhealthy';
  apiUrl: string;
  protocol: string;
  errors?: string[];
  warnings?: string[];
  timestamp: string;
}

/**
 * Check API connection health using unified configuration
 */
export async function checkApiConnection(): Promise<HealthCheckResult> {
  const apiUrl = ENV_CONFIG.api.baseURL;
  const protocol = new URL(apiUrl).protocol;
  
  // Get environment warnings
  const warnings = validateEnvironment();
  
  try {
    const response = await fetch(getHealthCheckUrl(), {
      method: 'GET',
      headers: ENV_CONFIG.api.headers,
    });
    
    return {
      status: response.ok ? 'healthy' : 'unhealthy',
      apiUrl,
      protocol,
      errors: response.ok ? undefined : [`HTTP ${response.status}`],
      warnings: warnings.length > 0 ? warnings : undefined,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      apiUrl,
      protocol,
      errors: [error instanceof Error ? error.message : 'Unknown error'],
      warnings: warnings.length > 0 ? warnings : undefined,
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Validate environment configuration for production - Now using unified config
 * @deprecated Use validateEnvironment() from '../config/environment' instead
 */
export function validateEnvironmentConfig(): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  const warnings = validateEnvironment();
  const errors: string[] = [];

  // In production, we should have HTTPS
  if (ENV_CONFIG.app.isProd) {
    if (!ENV_CONFIG.api.baseURL.startsWith('https://')) {
      errors.push('API URL must use HTTPS in production');
    }
    if (!ENV_CONFIG.api.wsURL.startsWith('wss://')) {
      errors.push('WebSocket URL must use WSS in production');
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}