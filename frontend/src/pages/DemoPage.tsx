import { IconSizingDemo } from '../components/demo/IconSizingDemo';
import { checkApiConnection, validateEnvironmentConfig } from '../utils/healthCheck';
import { useState, useEffect } from 'react';

interface HealthStatus {
  api: any;
  environment: any;
}

export function DemoPage() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkHealth() {
      try {
        const [apiResult, envResult] = await Promise.all([
          checkApiConnection(),
          Promise.resolve(validateEnvironmentConfig())
        ]);
        
        setHealthStatus({
          api: apiResult,
          environment: envResult
        });
      } catch (error) {
        console.error('Health check failed:', error);
      } finally {
        setLoading(false);
      }
    }
    
    checkHealth();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Z2 Platform - Fixes Demo</h1>
          <p className="text-gray-600">
            Demonstrating the resolution of mixed content blocking and icon sizing issues.
          </p>
        </div>

        {/* Health Check Section */}
        <div className="mb-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">🔍 Health Check Results</h2>
          
          {loading ? (
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ) : healthStatus ? (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-700">API Connection</h3>
                <div className={`p-3 rounded-md ${
                  healthStatus.api.status === 'healthy' 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-yellow-50 border border-yellow-200'
                }`}>
                  <p className="text-sm">
                    <strong>Status:</strong> {healthStatus.api.status} <br />
                    <strong>URL:</strong> {healthStatus.api.apiUrl} <br />
                    <strong>Protocol:</strong> {healthStatus.api.protocol} <br />
                    <strong>Timestamp:</strong> {healthStatus.api.timestamp}
                  </p>
                  {healthStatus.api.errors && (
                    <p className="text-sm text-red-600 mt-2">
                      <strong>Errors:</strong> {healthStatus.api.errors.join(', ')}
                    </p>
                  )}
                </div>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-700">Environment Configuration</h3>
                <div className={`p-3 rounded-md ${
                  healthStatus.environment.valid 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <p className="text-sm">
                    <strong>Valid:</strong> {healthStatus.environment.valid ? 'Yes' : 'No'}
                  </p>
                  {healthStatus.environment.errors?.length > 0 && (
                    <p className="text-sm text-red-600 mt-2">
                      <strong>Errors:</strong> {healthStatus.environment.errors.join(', ')}
                    </p>
                  )}
                  {healthStatus.environment.warnings?.length > 0 && (
                    <p className="text-sm text-yellow-600 mt-2">
                      <strong>Warnings:</strong> {healthStatus.environment.warnings.join(', ')}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-red-800 text-sm">Failed to perform health checks</p>
            </div>
          )}
        </div>

        {/* Icon Sizing Demo */}
        <div className="bg-white rounded-lg shadow">
          <IconSizingDemo />
        </div>

        {/* Summary */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-800 mb-4">✅ Issues Resolved</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-blue-700 mb-2">Mixed Content Blocking Fixed</h3>
              <ul className="text-sm text-blue-600 space-y-1">
                <li>• Protocol-aware fallback logic implemented</li>
                <li>• Dynamic HTTPS detection for production</li>
                <li>• Proper domain replacement for Railway deployment</li>
                <li>• Health check utility for validation</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-blue-700 mb-2">Icon Sizing Issues Fixed</h3>
              <ul className="text-sm text-blue-600 space-y-1">
                <li>• Global CSS constraints for safety</li>
                <li>• Maximum size limits (2rem) for all icons</li>
                <li>• Button-specific icon sizing</li>
                <li>• Navigation icon standardization</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}