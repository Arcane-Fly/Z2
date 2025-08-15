/**
 * Enhanced MCP Dashboard Component with Advanced Real-time Monitoring
 * 
 * Provides comprehensive system monitoring, agent activity tracking,
 * and workflow orchestration insights through the MCP protocol.
 */

import React, { useState, useEffect } from 'react';
import { 
  useMCPSession, 
  useMCPDashboard, 
  useMCPAgents, 
  useMCPWorkflows,
  useMCPStatistics 
} from '../hooks/useMCP';

interface MetricCard {
  title: string;
  value: string | number;
  change?: string;
  status: 'good' | 'warning' | 'error';
  description?: string;
}

interface ActivityItem {
  id: string;
  type: 'agent_execution' | 'workflow_start' | 'workflow_complete' | 'error';
  message: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error';
}

export const EnhancedMCPDashboard: React.FC = () => {
  const { data: session, isLoading: sessionLoading } = useMCPSession();
  const { data: dashboard, isLoading: dashboardLoading } = useMCPDashboard();
  const { agents, isLoading: agentsLoading } = useMCPAgents();
  const { activeWorkflows, isLoading: workflowsLoading } = useMCPWorkflows();
  const { data: stats } = useMCPStatistics();

  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Enhanced metrics calculation
  const metrics: MetricCard[] = [
    {
      title: 'Active Agents',
      value: agents?.filter(a => a.status === 'active').length || 0,
      change: '+2',
      status: 'good',
      description: 'Currently running AI agents'
    },
    {
      title: 'Running Workflows',
      value: activeWorkflows?.length || 0,
      change: '+1',
      status: 'good',
      description: 'Workflows in progress'
    },
    {
      title: 'System Health',
      value: dashboard?.systemHealth || 'Unknown',
      status: dashboard?.systemHealth === 'healthy' ? 'good' : 'warning',
      description: 'Overall system status'
    },
    {
      title: 'Success Rate',
      value: `${Math.round((stats?.successfulExecutions / (stats?.totalExecutions || 1)) * 100)}%`,
      change: '+5%',
      status: stats?.successfulExecutions / (stats?.totalExecutions || 1) > 0.9 ? 'good' : 'warning',
      description: 'Execution success rate'
    }
  ];

  // Generate activity feed
  const activities: ActivityItem[] = [
    ...agents?.map(agent => ({
      id: `agent-${agent.id}`,
      type: 'agent_execution' as const,
      message: `Agent ${agent.name} completed task`,
      timestamp: agent.lastActivity,
      status: 'success' as const
    })) || [],
    ...activeWorkflows?.map(workflow => ({
      id: `workflow-${workflow.id}`,
      type: workflow.status === 'completed' ? 'workflow_complete' as const : 'workflow_start' as const,
      message: `Workflow ${workflow.name} ${workflow.status}`,
      timestamp: workflow.updatedAt,
      status: workflow.status === 'failed' ? 'error' as const : 'success' as const
    })) || []
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).slice(0, 10);

  if (sessionLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Initializing MCP session...</div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-yellow-800 font-medium">MCP Session Required</h3>
        <p className="text-yellow-700">Please initialize an MCP session to view the dashboard.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Enhanced MCP Dashboard</h1>
          <p className="text-gray-600">Real-time AI workforce monitoring and orchestration</p>
        </div>
        <div className="flex space-x-3">
          <select 
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last Week</option>
          </select>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-md ${
              autoRefresh 
                ? 'bg-green-100 text-green-800 border border-green-300' 
                : 'bg-gray-100 text-gray-800 border border-gray-300'
            }`}
          >
            Auto Refresh {autoRefresh ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                {metric.change && (
                  <p className="text-sm text-green-600">{metric.change}</p>
                )}
              </div>
              <div className={`w-3 h-3 rounded-full ${
                metric.status === 'good' ? 'bg-green-400' :
                metric.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
              }`} />
            </div>
            {metric.description && (
              <p className="text-xs text-gray-500 mt-2">{metric.description}</p>
            )}
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Agent Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Agents</h3>
          {agentsLoading ? (
            <div className="text-gray-500">Loading agents...</div>
          ) : (
            <div className="space-y-3">
              {agents?.map(agent => (
                <div key={agent.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{agent.name}</p>
                    <p className="text-sm text-gray-600">{agent.role}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      agent.status === 'active' ? 'bg-green-100 text-green-800' :
                      agent.status === 'idle' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {agent.status}
                    </span>
                  </div>
                </div>
              )) || <div className="text-gray-500">No agents available</div>}
            </div>
          )}
        </div>

        {/* Workflow Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Workflows</h3>
          {workflowsLoading ? (
            <div className="text-gray-500">Loading workflows...</div>
          ) : (
            <div className="space-y-3">
              {activeWorkflows?.map(workflow => (
                <div key={workflow.id} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-gray-900">{workflow.name}</p>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      workflow.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      workflow.status === 'completed' ? 'bg-green-100 text-green-800' :
                      workflow.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {workflow.status}
                    </span>
                  </div>
                  {workflow.progress !== undefined && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${workflow.progress}%` }}
                      />
                    </div>
                  )}
                </div>
              )) || <div className="text-gray-500">No active workflows</div>}
            </div>
          )}
        </div>

        {/* Activity Feed */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {activities.map(activity => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  activity.status === 'success' ? 'bg-green-400' :
                  activity.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">MCP Session</h4>
            <p className="text-sm text-gray-600">Session ID: {session.session_id}</p>
            <p className="text-sm text-gray-600">Protocol: {session.protocol_version}</p>
            <p className="text-sm text-gray-600">Client: {session.client_name}</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Performance</h4>
            <p className="text-sm text-gray-600">Total Executions: {stats?.totalExecutions || 0}</p>
            <p className="text-sm text-gray-600">Successful: {stats?.successfulExecutions || 0}</p>
            <p className="text-sm text-gray-600">Failed: {stats?.failedExecutions || 0}</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Resources</h4>
            <p className="text-sm text-gray-600">Active Agents: {agents?.length || 0}</p>
            <p className="text-sm text-gray-600">Running Workflows: {activeWorkflows?.length || 0}</p>
            <p className="text-sm text-gray-600">System Status: {dashboard?.systemHealth || 'Unknown'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedMCPDashboard;