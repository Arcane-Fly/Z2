import { useDashboardStats } from '../hooks/useApi';
import { DashboardChart } from '../components/DashboardChart';

export function Dashboard() {
  const { data: stats, isLoading, error } = useDashboardStats();

  // Sample chart data - in a real app this would come from the API
  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Active Agents',
        data: [0, 1, 2, 1, 3, 2],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
      },
      {
        label: 'Running Workflows',
        data: [0, 0, 1, 2, 1, 4],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
      },
    ],
  };

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Monitor your AI workforce and workflow performance
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">Failed to load dashboard data. Please try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Monitor your AI workforce and workflow performance
        </p>
      </div>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Stats Cards */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-medium">A</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Active Agents
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {isLoading ? (
                      <div className="animate-pulse bg-gray-200 h-6 w-8 rounded"></div>
                    ) : (
                      stats?.activeAgents || 0
                    )}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-medium">W</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Running Workflows
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {isLoading ? (
                      <div className="animate-pulse bg-gray-200 h-6 w-8 rounded"></div>
                    ) : (
                      stats?.runningWorkflows || 0
                    )}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-medium">$</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Cost (USD)
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {isLoading ? (
                      <div className="animate-pulse bg-gray-200 h-6 w-16 rounded"></div>
                    ) : (
                      `$${stats?.totalCost?.toFixed(2) || '0.00'}`
                    )}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-medium">T</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Tokens Used
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {isLoading ? (
                      <div className="animate-pulse bg-gray-200 h-6 w-16 rounded"></div>
                    ) : (
                      stats?.tokensUsed?.toLocaleString() || 0
                    )}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <DashboardChart title="Activity Over Time" data={chartData} />
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-center text-sm">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
              <span className="text-gray-500">2 minutes ago</span>
              <span className="ml-2">Agent "DataProcessor" started</span>
            </div>
            <div className="flex items-center text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span className="text-gray-500">5 minutes ago</span>
              <span className="ml-2">Workflow "EmailAutomation" completed</span>
            </div>
            <div className="flex items-center text-sm">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
              <span className="text-gray-500">10 minutes ago</span>
              <span className="ml-2">New model "GPT-4" configured</span>
            </div>
            <div className="flex items-center text-sm">
              <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
              <span className="text-gray-500">15 minutes ago</span>
              <span className="ml-2">Agent "ContentWriter" updated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Welcome Section */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Welcome to Z2 AI Workforce Platform
          </h3>
          <div className="mt-2 max-w-xl text-sm text-gray-500">
            <p>
              Get started by creating your first AI agent or workflow. Z2 provides
              dynamic multi-agent orchestration for complex task automation.
            </p>
          </div>
          <div className="mt-5 flex space-x-3">
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Create First Agent
            </button>
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              View Documentation
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}