import { useState } from 'react';
import { useWorkflows } from '../hooks/useApi';
import { Workflow } from '../types';
import { PlusIcon, PlayIcon, PauseIcon, StopIcon, ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

export function Workflows() {
  const { data: workflows, isLoading, error } = useWorkflows();
  const [showCreateModal, setShowCreateModal] = useState(false);

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
            <p className="mt-2 text-gray-600">
              Design and execute multi-agent workflows
            </p>
          </div>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">Failed to load workflows. Please try again.</p>
        </div>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <PlayIcon className="h-5 w-5 text-green-500" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="mt-2 text-gray-600">
            Design and execute multi-agent workflows
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Create Workflow
        </button>
      </div>

      {isLoading ? (
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
      ) : workflows && workflows.length > 0 ? (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
          {workflows.map((workflow: Workflow) => (
            <div key={workflow.id} className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(workflow.status)}
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {workflow.name}
                    </h3>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(workflow.status)}`}>
                    {workflow.status}
                  </span>
                </div>
                
                <p className="mt-2 text-sm text-gray-500 line-clamp-2">
                  {workflow.description}
                </p>
                
                <div className="mt-4">
                  <div className="flex items-center text-sm text-gray-500">
                    <span>Agents: {workflow.agents?.length || 0}</span>
                    <span className="mx-2">•</span>
                    <span>Updated: {new Date(workflow.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="mt-6 flex justify-between">
                  <div className="flex space-x-2">
                    {workflow.status === 'draft' && (
                      <button
                        type="button"
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                      >
                        <PlayIcon className="h-4 w-4 mr-1" />
                        Start
                      </button>
                    )}
                    {workflow.status === 'running' && (
                      <>
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-yellow-700 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                        >
                          <PauseIcon className="h-4 w-4 mr-1" />
                          Pause
                        </button>
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                        >
                          <StopIcon className="h-4 w-4 mr-1" />
                          Stop
                        </button>
                      </>
                    )}
                  </div>
                  <button
                    type="button"
                    className="text-sm text-blue-600 hover:text-blue-500 font-medium"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))}
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No workflows</h3>
              <p className="mt-1 text-sm text-gray-500">
                Create your first multi-agent workflow to automate complex tasks.
              </p>
              <div className="mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Create Workflow
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TODO: Create Workflow Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create Workflow</h3>
            <p className="text-sm text-gray-500 mb-4">Workflow builder coming soon...</p>
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}