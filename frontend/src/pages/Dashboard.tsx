import { useDashboardStats } from '../hooks/useApi';
import { DashboardChart } from '../components/DashboardChart';
import { MCPControlPanel } from '../components/MCPControlPanel';
import { 
  useMCPSession, 
  useMCPStatistics, 
  useMCPAgents,
  useMCPWorkflows,
  useMCPMetrics,
  useMCPCleanup 
} from '../hooks/useMCP';
import { useEffect, useState } from 'react';

export function Dashboard() {
  // Traditional API data as fallback
  const { data: stats, isLoading: statsLoading, error: statsError } = useDashboardStats();
  
  // MCP Integration - The Magic ✨
  useMCPCleanup(); // Cleanup on unmount
  const { data: mcpSession, isLoading: sessionLoading } = useMCPSession();
  const { data: mcpStats } = useMCPStatistics();
  const { agents: mcpAgents } = useMCPAgents();
  const { activeWorkflows } = useMCPWorkflows();
  const { system: systemMetrics } = useMCPMetrics();
  
  // Real-time activity updates
  const [activities, setActivities] = useState<any[]>([]);
  
  // Use MCP data if available, fallback to traditional API
  const isLoading = sessionLoading || statsLoading;
  const error = statsError;
  
  // Enhanced stats with MCP data
  const enhancedStats = {
    activeAgents: mcpAgents?.length || stats?.activeAgents || 0,
    runningWorkflows: activeWorkflows?.length || stats?.runningWorkflows || 0,
    totalCost: systemMetrics?.cost || stats?.totalCost || 0,
    tokensUsed: systemMetrics?.tokens || stats?.tokensUsed || 0,
  };

  // Real-time activity feed from MCP
  useEffect(() => {
    if (mcpStats?.tasks?.running_tasks) {
      const newActivities = mcpStats.tasks.running_tasks.map((task) => ({
        id: task.task_id,
        time: new Date(task.started_at || Date.now()).toLocaleTimeString(),
        message: `Task "${task.task_name}" is ${task.progress * 100}% complete`,
        type: 'task',
        color: 'blue'
      }));
      setActivities(prev => [...newActivities, ...prev.slice(0, 3)].slice(0, 4));
    }
  }, [mcpStats]);

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
    <div style={{ 
      padding: '24px',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      minHeight: '100vh'
    }}>
      {/* Header Section */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 'bold',
          color: '#1f2937',
          margin: '0 0 8px 0',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          Dashboard
        </h1>
        <p style={{
          fontSize: '18px',
          color: '#6b7280',
          margin: 0,
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          Monitor your AI workforce and workflow performance
        </p>
      </div>
      
      {/* Stats Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '24px',
        marginBottom: '32px'
      }}>
        {/* Active Agents Card */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          boxShadow: '0 10px 25px rgba(102, 126, 234, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{
                fontSize: '14px',
                fontWeight: '500',
                color: 'rgba(255, 255, 255, 0.8)',
                margin: '0 0 8px 0',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                Active Agents
              </h3>
              <p style={{
                fontSize: '28px',
                fontWeight: 'bold',
                color: 'white',
                margin: 0,
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                {isLoading ? (
                  <div style={{
                    width: '40px',
                    height: '32px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    animation: 'pulse 2s infinite'
                  }}></div>
                ) : (
                  enhancedStats.activeAgents
                )}
              </p>
            </div>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg style={{ width: '24px', height: '24px', color: 'white' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Running Workflows Card */}
        <div style={{
          background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          boxShadow: '0 10px 25px rgba(79, 172, 254, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{
                fontSize: '14px',
                fontWeight: '500',
                color: 'rgba(255, 255, 255, 0.8)',
                margin: '0 0 8px 0',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                Running Workflows
              </h3>
              <p style={{
                fontSize: '28px',
                fontWeight: 'bold',
                color: 'white',
                margin: 0,
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                {isLoading ? (
                  <div style={{
                    width: '40px',
                    height: '32px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    animation: 'pulse 2s infinite'
                  }}></div>
                ) : (
                  enhancedStats.runningWorkflows
                )}
              </p>
            </div>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg style={{ width: '24px', height: '24px', color: 'white' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Total Cost Card */}
        <div style={{
          background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          boxShadow: '0 10px 25px rgba(250, 112, 154, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{
                fontSize: '14px',
                fontWeight: '500',
                color: 'rgba(255, 255, 255, 0.8)',
                margin: '0 0 8px 0',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                Total Cost (USD)
              </h3>
              <p style={{
                fontSize: '28px',
                fontWeight: 'bold',
                color: 'white',
                margin: 0,
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                {isLoading ? (
                  <div style={{
                    width: '60px',
                    height: '32px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    animation: 'pulse 2s infinite'
                  }}></div>
                ) : (
                  `$${enhancedStats.totalCost?.toFixed(2) || '0.00'}`
                )}
              </p>
            </div>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg style={{ width: '24px', height: '24px', color: 'white' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>

        {/* Tokens Used Card */}
        <div style={{
          background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: '#374151',
          boxShadow: '0 10px 25px rgba(168, 237, 234, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{
                fontSize: '14px',
                fontWeight: '500',
                color: '#6b7280',
                margin: '0 0 8px 0',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                Tokens Used
              </h3>
              <p style={{
                fontSize: '28px',
                fontWeight: 'bold',
                color: '#374151',
                margin: 0,
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                {isLoading ? (
                  <div style={{
                    width: '60px',
                    height: '32px',
                    background: 'rgba(107, 114, 128, 0.2)',
                    borderRadius: '8px',
                    animation: 'pulse 2s infinite'
                  }}></div>
                ) : (
                  enhancedStats.tokensUsed?.toLocaleString() || 0
                )}
              </p>
            </div>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'rgba(255, 255, 255, 0.5)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg style={{ width: '24px', height: '24px', color: '#374151' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Chart and Activity Section */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '24px',
        marginBottom: '32px'
      }}>
        {/* Chart Card */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(20px)',
          borderRadius: '20px',
          padding: '32px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#1f2937',
            margin: '0 0 24px 0',
            fontFamily: 'system-ui, -apple-system, sans-serif'
          }}>
            Activity Over Time
          </h3>
          <div style={{ height: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <DashboardChart title="" data={chartData} />
          </div>
        </div>
        
        {/* Recent Activity Card */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(20px)',
          borderRadius: '20px',
          padding: '32px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#1f2937',
            margin: '0 0 24px 0',
            fontFamily: 'system-ui, -apple-system, sans-serif'
          }}>
            Recent Activity
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* MCP Session Status */}
            {mcpSession && (
              <div style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  borderRadius: '50%',
                  marginRight: '12px',
                  animation: 'pulse 2s infinite'
                }}></div>
                <span style={{ color: '#6b7280', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                  Now
                </span>
                <span style={{
                  marginLeft: '8px',
                  color: '#374151',
                  fontFamily: 'system-ui, -apple-system, sans-serif'
                }}>
                  MCP Protocol v{mcpSession.protocolVersion} connected ✨
                </span>
              </div>
            )}
            
            {/* Real-time Activities from MCP */}
            {activities.map((activity, index) => (
              <div key={activity.id || index} style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  background: `linear-gradient(135deg, ${
                    activity.color === 'blue' ? '#3b82f6 0%, #1d4ed8 100%' :
                    activity.color === 'green' ? '#10b981 0%, #059669 100%' :
                    activity.color === 'yellow' ? '#f59e0b 0%, #d97706 100%' :
                    '#8b5cf6 0%, #7c3aed 100%'
                  })`,
                  borderRadius: '50%',
                  marginRight: '12px'
                }}></div>
                <span style={{
                  color: '#6b7280',
                  fontFamily: 'system-ui, -apple-system, sans-serif'
                }}>{activity.time}</span>
                <span style={{
                  marginLeft: '8px',
                  color: '#374151',
                  fontFamily: 'system-ui, -apple-system, sans-serif'
                }}>{activity.message}</span>
              </div>
            ))}
            
            {/* Static activities as fallback */}
            {activities.length === 0 && (
              <>
                <div style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                    borderRadius: '50%',
                    marginRight: '12px'
                  }}></div>
                  <span style={{
                    color: '#6b7280',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>2 minutes ago</span>
                  <span style={{
                    marginLeft: '8px',
                    color: '#374151',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>Agent "DataProcessor" started</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    borderRadius: '50%',
                    marginRight: '12px'
                  }}></div>
                  <span style={{
                    color: '#6b7280',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>5 minutes ago</span>
                  <span style={{
                    marginLeft: '8px',
                    color: '#374151',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>Workflow "EmailAutomation" completed</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                    borderRadius: '50%',
                    marginRight: '12px'
                  }}></div>
                  <span style={{
                    color: '#6b7280',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>10 minutes ago</span>
                  <span style={{
                    marginLeft: '8px',
                    color: '#374151',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>New model "GPT-4" configured</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                    borderRadius: '50%',
                    marginRight: '12px'
                  }}></div>
                  <span style={{
                    color: '#6b7280',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>15 minutes ago</span>
                  <span style={{
                    marginLeft: '8px',
                    color: '#374151',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>Agent "ContentWriter" updated</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* MCP Control Panel - The Magic ✨ */}
      <MCPControlPanel />

      {/* Welcome Section */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '20px',
        padding: '40px',
        color: 'white',
        boxShadow: '0 20px 40px rgba(102, 126, 234, 0.3)',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <h3 style={{
          fontSize: '24px',
          fontWeight: 'bold',
          color: 'white',
          margin: '0 0 16px 0',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          Welcome to Z2 AI Workforce Platform
        </h3>
        <p style={{
          fontSize: '16px',
          color: 'rgba(255, 255, 255, 0.9)',
          margin: '0 0 32px 0',
          maxWidth: '600px',
          lineHeight: '1.6',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          Get started by creating your first AI agent or workflow. Z2 provides
          dynamic multi-agent orchestration for complex task automation.
        </p>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <button
            type="button"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: '12px 24px',
              border: 'none',
              fontSize: '14px',
              fontWeight: '600',
              borderRadius: '12px',
              color: '#667eea',
              background: 'white',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 4px 14px rgba(255, 255, 255, 0.3)',
              fontFamily: 'system-ui, -apple-system, sans-serif'
            }}
            onMouseOver={(e) => {
              const target = e.target as HTMLElement;
              target.style.transform = 'translateY(-2px)';
              target.style.boxShadow = '0 8px 25px rgba(255, 255, 255, 0.4)';
            }}
            onMouseOut={(e) => {
              const target = e.target as HTMLElement;
              target.style.transform = 'translateY(0)';
              target.style.boxShadow = '0 4px 14px rgba(255, 255, 255, 0.3)';
            }}
          >
            Create First Agent
          </button>
          <button
            type="button"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: '12px 24px',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              fontSize: '14px',
              fontWeight: '600',
              borderRadius: '12px',
              color: 'white',
              background: 'transparent',
              cursor: 'pointer',
              transition: 'all 0.2s',
              fontFamily: 'system-ui, -apple-system, sans-serif'
            }}
            onMouseOver={(e) => {
              const target = e.target as HTMLElement;
              target.style.background = 'rgba(255, 255, 255, 0.1)';
              target.style.borderColor = 'rgba(255, 255, 255, 0.5)';
            }}
            onMouseOut={(e) => {
              const target = e.target as HTMLElement;
              target.style.background = 'transparent';
              target.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            }}
          >
            View Documentation
          </button>
        </div>
      </div>

      {/* CSS Animation for pulse */}
      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}
      </style>
    </div>
  )
}