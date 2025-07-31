import { useState } from 'react';
import { useAgents } from '../hooks/useApi';
import { useMCPAgents, useMCPAgentExecution } from '../hooks/useMCP';
import { CreateAgentModal } from '../components/modals';
import { Agent } from '../types';
import { PlusIcon, PencilIcon, TrashIcon, PlayIcon } from '@heroicons/react/24/outline';

export function Agents() {
  const { data: agents, isLoading, error } = useAgents();
  const { agents: mcpAgents, isLoading: mcpLoading } = useMCPAgents();
  const { executeAgent, isPending: executionPending } = useMCPAgentExecution();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [executingAgent, setExecutingAgent] = useState<string | null>(null);

  // Enhanced agents data with MCP real-time status
  const enhancedAgents = agents || [];
  if (mcpAgents) {
    // Add MCP agent data if available
    mcpAgents.forEach((mcpAgent: any) => {
      if (mcpAgent?.content) {
        const existing = enhancedAgents.find(a => a.id === mcpAgent.content.id);
        if (!existing) {
          enhancedAgents.push({
            id: mcpAgent.content.id,
            name: mcpAgent.content.id.charAt(0).toUpperCase() + mcpAgent.content.id.slice(1),
            status: mcpAgent.content.status,
            description: `MCP Agent - Load: ${mcpAgent.content.load}`,
            type: mcpAgent.content.type,
            capabilities: mcpAgent.content.capabilities,
            config: {},
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          });
        }
      }
    });
  }

  const handleQuickExecute = (agentId: string) => {
    setExecutingAgent(agentId);
    try {
      executeAgent(
        agentId,
        'Perform a quick status check and report current capabilities',
        {},
        (progress) => {
          console.log(`Agent ${agentId} progress: ${progress.progress * 100}%`);
        }
      );
    } catch (error) {
      console.error('Error executing agent:', error);
    } finally {
      setExecutingAgent(null);
    }
  };

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Agents</h1>
            <p className="mt-2 text-gray-600">
              Manage your AI agents and their configurations
            </p>
          </div>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">Failed to load agents. Please try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agents</h1>
          <p className="mt-2 text-gray-600">
            Manage your AI agents and their configurations
            {mcpAgents && mcpAgents.length > 0 && (
              <span className="ml-2 inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
                ✨ MCP Enhanced
              </span>
            )}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Create Agent
        </button>
      </div>

      {(isLoading || mcpLoading) ? (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              </div>
            </div>
          </div>
        </div>
      ) : enhancedAgents && enhancedAgents.length > 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {enhancedAgents.map((agent: Agent) => (
              <li key={agent.id}>
                <div className="px-4 py-4 flex items-center justify-between">
                  <div className="flex items-center min-w-0 flex-1">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-sm font-medium">
                          {agent.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4 min-w-0 flex-1">
                      <div className="flex items-center">
                        <h3 className="text-sm font-medium text-gray-900 truncate">
                          {agent.name}
                        </h3>
                        <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          agent.status === 'active' 
                            ? 'bg-green-100 text-green-800' 
                            : agent.status === 'error'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {agent.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 truncate">
                        {agent.description}
                      </p>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <span className="truncate">Type: {agent.type}</span>
                        {agent.capabilities && agent.capabilities.length > 0 && (
                          <>
                            <span className="mx-2">•</span>
                            <span className="truncate">
                              {agent.capabilities.length} capabilities
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {/* MCP Quick Execute - Magic Button ✨ */}
                    <button
                      type="button"
                      onClick={() => handleQuickExecute(agent.id)}
                      disabled={executingAgent === agent.id || executionPending}
                      className="inline-flex items-center p-2 border border-purple-300 rounded-md shadow-sm text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Quick MCP Execute ✨"
                    >
                      {executingAgent === agent.id ? (
                        <div className="h-4 w-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
                      ) : (
                        <PlayIcon className="h-4 w-4" />
                      )}
                    </button>
                    <button
                      type="button"
                      className="inline-flex items-center p-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      className="inline-flex items-center p-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No agents</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating your first AI agent.
              </p>
              <div className="mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Create Agent
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Agent Modal */}
      <CreateAgentModal 
        isOpen={showCreateModal} 
        onClose={() => setShowCreateModal(false)} 
      />
    </div>
  )
}