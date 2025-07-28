/**
 * MCP Control Panel - The Magic Interface ✨
 * 
 * This component showcases the magical capabilities of the MCP integration,
 * providing real-time agent execution, interactive workflows, and dynamic
 * resource discovery in a beautiful, intuitive interface.
 */

import { useState } from 'react';
import { 
  useMCPSession,
  useMCPTools,
  useMCPPrompts,
  useMCPAgentExecution,
  useMCPWorkflowCreation,
  useMCPSystemAnalysis,
  useMCPStatistics
} from '../hooks/useMCP';

interface MCPControlPanelProps {
  className?: string;
}

export function MCPControlPanel({ className = '' }: MCPControlPanelProps) {
  const [activeTab, setActiveTab] = useState<'agents' | 'workflows' | 'analysis' | 'prompts'>('agents');
  const [agentTask, setAgentTask] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('default');
  const [workflowName, setWorkflowName] = useState('');
  const [progress, setProgress] = useState<{ [key: string]: number }>({});

  // MCP hooks
  const { data: session } = useMCPSession();
  const { data: tools } = useMCPTools();
  const { data: prompts } = useMCPPrompts();
  const { data: stats } = useMCPStatistics();
  
  const { executeAgent, isPending: agentPending } = useMCPAgentExecution();
  const { createWorkflow, isPending: workflowPending } = useMCPWorkflowCreation();
  const { analyzeSystem, isPending: analysisPending } = useMCPSystemAnalysis();

  const handleAgentExecution = () => {
    if (!agentTask.trim()) return;
    
    executeAgent(
      selectedAgent,
      agentTask,
      {},
      (update) => {
        setProgress(prev => ({ ...prev, [selectedAgent]: update.progress }));
      }
    );
  };

  const handleWorkflowCreation = () => {
    if (!workflowName.trim()) return;
    
    createWorkflow(
      workflowName,
      [selectedAgent, 'reasoning'],
      { priority: 'high' },
      (update) => {
        setProgress(prev => ({ ...prev, workflow: update.progress }));
      }
    );
  };

  const handleSystemAnalysis = (scope: 'performance' | 'security' | 'usage') => {
    analyzeSystem(scope, { detailed: true });
  };

  if (!session) {
    return (
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '20px',
        padding: '40px',
        color: 'white',
        textAlign: 'center',
        margin: '20px 0'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔮</div>
        <h3 style={{ fontSize: '24px', fontWeight: 'bold', margin: '0 0 16px 0' }}>
          Initializing MCP Magic...
        </h3>
        <p style={{ fontSize: '16px', opacity: 0.9 }}>
          Connecting to the Model Context Protocol for enhanced capabilities
        </p>
      </div>
    );
  }

  return (
    <div className={`mcp-control-panel ${className}`} style={{
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(20px)',
      borderRadius: '20px',
      padding: '32px',
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      margin: '20px 0'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '32px', textAlign: 'center' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>✨</div>
        <h2 style={{
          fontSize: '28px',
          fontWeight: 'bold',
          color: '#1f2937',
          margin: '0 0 8px 0',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          MCP Control Panel
        </h2>
        <p style={{
          fontSize: '16px',
          color: '#6b7280',
          margin: 0
        }}>
          Magical Model Context Protocol Interface • Protocol v{session.protocolVersion}
        </p>
      </div>

      {/* Stats Bar */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        <div style={{
          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
          borderRadius: '12px',
          padding: '16px',
          color: 'white',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
            {tools?.length || 0}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.8 }}>MCP Tools</div>
        </div>
        <div style={{
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          borderRadius: '12px',
          padding: '16px',
          color: 'white',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
            {prompts?.length || 0}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.8 }}>Prompts</div>
        </div>
        <div style={{
          background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
          borderRadius: '12px',
          padding: '16px',
          color: 'white',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
            {stats?.tasks?.running || 0}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.8 }}>Running Tasks</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '24px',
        borderBottom: '1px solid #e5e7eb',
        paddingBottom: '16px'
      }}>
        {[
          { id: 'agents', label: '🤖 Agents', icon: '🤖' },
          { id: 'workflows', label: '⚡ Workflows', icon: '⚡' },
          { id: 'analysis', label: '📊 Analysis', icon: '📊' },
          { id: 'prompts', label: '💭 Prompts', icon: '💭' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              padding: '12px 20px',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: activeTab === tab.id 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'transparent',
              color: activeTab === tab.id ? 'white' : '#6b7280',
              ...(activeTab !== tab.id && {
                ':hover': {
                  background: '#f3f4f6'
                }
              })
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ minHeight: '200px' }}>
        {activeTab === 'agents' && (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px', color: '#1f2937' }}>
              🤖 Execute Agent Task
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px', color: '#374151' }}>
                  Select Agent
                </label>
                <select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '14px',
                    background: 'white'
                  }}
                >
                  <option value="default">🔧 Default Agent</option>
                  <option value="reasoning">🧠 Reasoning Agent</option>
                  <option value="code">💻 Code Agent</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px', color: '#374151' }}>
                  Task Description
                </label>
                <textarea
                  value={agentTask}
                  onChange={(e) => setAgentTask(e.target.value)}
                  placeholder="Enter a task for the agent to execute..."
                  style={{
                    width: '100%',
                    height: '80px',
                    padding: '12px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '14px',
                    resize: 'vertical'
                  }}
                />
              </div>
              {progress[selectedAgent] !== undefined && (
                <div style={{
                  background: '#f3f4f6',
                  borderRadius: '8px',
                  padding: '12px'
                }}>
                  <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                    Progress: {Math.round(progress[selectedAgent] * 100)}%
                  </div>
                  <div style={{
                    width: '100%',
                    height: '8px',
                    background: '#e5e7eb',
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: `${progress[selectedAgent] * 100}%`,
                      height: '100%',
                      background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                </div>
              )}
              <button
                onClick={handleAgentExecution}
                disabled={agentPending || !agentTask.trim()}
                style={{
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: 'white',
                  background: agentPending 
                    ? '#9ca3af' 
                    : 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                  cursor: agentPending ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {agentPending ? 'Executing...' : '▶️ Execute Agent'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'workflows' && (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px', color: '#1f2937' }}>
              ⚡ Create Workflow
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px', color: '#374151' }}>
                  Workflow Name
                </label>
                <input
                  type="text"
                  value={workflowName}
                  onChange={(e) => setWorkflowName(e.target.value)}
                  placeholder="Enter workflow name..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '14px'
                  }}
                />
              </div>
              {progress.workflow !== undefined && (
                <div style={{
                  background: '#f3f4f6',
                  borderRadius: '8px',
                  padding: '12px'
                }}>
                  <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                    Creating workflow: {Math.round(progress.workflow * 100)}%
                  </div>
                  <div style={{
                    width: '100%',
                    height: '8px',
                    background: '#e5e7eb',
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: `${progress.workflow * 100}%`,
                      height: '100%',
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                </div>
              )}
              <button
                onClick={handleWorkflowCreation}
                disabled={workflowPending || !workflowName.trim()}
                style={{
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: 'white',
                  background: workflowPending 
                    ? '#9ca3af' 
                    : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  cursor: workflowPending ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {workflowPending ? 'Creating...' : '⚡ Create Workflow'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px', color: '#1f2937' }}>
              📊 System Analysis
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {[
                { scope: 'performance' as const, label: '🚀 Performance', color: '#3b82f6' },
                { scope: 'security' as const, label: '🔒 Security', color: '#ef4444' },
                { scope: 'usage' as const, label: '📈 Usage', color: '#10b981' }
              ].map(analysis => (
                <button
                  key={analysis.scope}
                  onClick={() => handleSystemAnalysis(analysis.scope)}
                  disabled={analysisPending}
                  style={{
                    padding: '20px',
                    border: 'none',
                    borderRadius: '16px',
                    fontSize: '16px',
                    fontWeight: '600',
                    color: 'white',
                    background: analysisPending 
                      ? '#9ca3af' 
                      : `linear-gradient(135deg, ${analysis.color} 0%, ${analysis.color}dd 100%)`,
                    cursor: analysisPending ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    textAlign: 'center'
                  }}
                >
                  {analysis.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'prompts' && (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px', color: '#1f2937' }}>
              💭 Available Prompts
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
              {prompts?.map(prompt => (
                <div
                  key={prompt.name}
                  style={{
                    background: 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)',
                    borderRadius: '12px',
                    padding: '16px',
                    border: '1px solid #d1d5db'
                  }}
                >
                  <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px', color: '#1f2937' }}>
                    {prompt.name}
                  </h4>
                  <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
                    {prompt.description}
                  </p>
                </div>
              )) || (
                <div style={{ textAlign: 'center', color: '#6b7280', gridColumn: '1 / -1' }}>
                  Loading prompts...
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        marginTop: '32px',
        paddingTop: '16px',
        borderTop: '1px solid #e5e7eb',
        textAlign: 'center',
        fontSize: '12px',
        color: '#6b7280'
      }}>
        ✨ Powered by Model Context Protocol (MCP) • Real-time capabilities enabled
      </div>
    </div>
  );
}