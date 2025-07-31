import { useState } from 'react';
import { useCreateWorkflow, useAgents } from '../../hooks/useApi';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface CreateWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface WorkflowTask {
  name: string;
  description: string;
  agent_role?: string;
  depends_on?: string[];
}

const WORKFLOW_TEMPLATES = [
  {
    name: 'Research & Analysis',
    description: 'Comprehensive research followed by detailed analysis',
    goal: 'Conduct thorough research on the topic and provide detailed analysis with actionable insights',
    tasks: [
      { name: 'Initial Research', description: 'Gather comprehensive information from reliable sources', agent_role: 'researcher' },
      { name: 'Data Analysis', description: 'Analyze collected data and identify key patterns', agent_role: 'analyst', depends_on: ['Initial Research'] },
      { name: 'Report Generation', description: 'Create comprehensive report with findings and recommendations', agent_role: 'writer', depends_on: ['Data Analysis'] },
      { name: 'Quality Review', description: 'Review and validate the final report', agent_role: 'reviewer', depends_on: ['Report Generation'] },
    ]
  },
  {
    name: 'Software Development',
    description: 'Complete software development workflow from planning to deployment',
    goal: 'Design, develop, test, and deploy a software solution according to requirements',
    tasks: [
      { name: 'Requirements Planning', description: 'Define and document project requirements', agent_role: 'planner' },
      { name: 'Code Development', description: 'Implement the software solution', agent_role: 'coder', depends_on: ['Requirements Planning'] },
      { name: 'Code Review', description: 'Review code quality and best practices', agent_role: 'reviewer', depends_on: ['Code Development'] },
      { name: 'Testing & Validation', description: 'Test the solution and validate requirements', agent_role: 'validator', depends_on: ['Code Review'] },
    ]
  },
  {
    name: 'Content Creation',
    description: 'Multi-stage content creation with review and optimization',
    goal: 'Create high-quality content that meets target audience needs and business objectives',
    tasks: [
      { name: 'Content Planning', description: 'Plan content strategy and outline', agent_role: 'planner' },
      { name: 'Content Research', description: 'Research topic and gather supporting information', agent_role: 'researcher', depends_on: ['Content Planning'] },
      { name: 'Content Writing', description: 'Write the main content based on plan and research', agent_role: 'writer', depends_on: ['Content Research'] },
      { name: 'Content Review', description: 'Review and refine the content', agent_role: 'reviewer', depends_on: ['Content Writing'] },
    ]
  },
];

export function CreateWorkflowModal({ isOpen, onClose }: CreateWorkflowModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    goal: '',
    max_duration_seconds: 3600,
    max_cost_usd: 10.0,
    require_human_approval: false,
    agent_ids: [] as string[],
    tasks: [] as WorkflowTask[],
  });

  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const createWorkflow = useCreateWorkflow();
  const { data: agents } = useAgents();

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.length > 100) {
      newErrors.name = 'Name must be 100 characters or less';
    }

    if (formData.description && formData.description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }

    if (!formData.goal.trim()) {
      newErrors.goal = 'Goal is required';
    } else if (formData.goal.length < 10) {
      newErrors.goal = 'Goal must be at least 10 characters';
    }

    if (formData.max_duration_seconds < 60 || formData.max_duration_seconds > 86400) {
      newErrors.max_duration_seconds = 'Duration must be between 60 seconds and 24 hours';
    }

    if (formData.max_cost_usd < 0.1 || formData.max_cost_usd > 1000) {
      newErrors.max_cost_usd = 'Cost limit must be between $0.10 and $1000';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await createWorkflow.mutateAsync(formData);
      onClose();
      // Reset form
      setFormData({
        name: '',
        description: '',
        goal: '',
        max_duration_seconds: 3600,
        max_cost_usd: 10.0,
        require_human_approval: false,
        agent_ids: [],
        tasks: [],
      });
      setSelectedTemplate('');
      setErrors({});
    } catch (error) {
      console.error('Failed to create workflow:', error);
      setErrors({ submit: 'Failed to create workflow. Please try again.' });
    }
  };

  const applyTemplate = (templateName: string) => {
    const template = WORKFLOW_TEMPLATES.find(t => t.name === templateName);
    if (template) {
      setFormData(prev => ({
        ...prev,
        name: template.name,
        description: template.description,
        goal: template.goal,
        tasks: template.tasks,
      }));
    }
  };

  const addTask = () => {
    setFormData(prev => ({
      ...prev,
      tasks: [...prev.tasks, { name: '', description: '', agent_role: '', depends_on: [] }]
    }));
  };

  const updateTask = (index: number, field: keyof WorkflowTask, value: any) => {
    setFormData(prev => ({
      ...prev,
      tasks: prev.tasks.map((task, i) => 
        i === index ? { ...task, [field]: value } : task
      )
    }));
  };

  const removeTask = (index: number) => {
    setFormData(prev => ({
      ...prev,
      tasks: prev.tasks.filter((_, i) => i !== index)
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Create New Workflow</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-6">
          {errors.submit && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-sm text-red-600">{errors.submit}</p>
            </div>
          )}

          {/* Template Selection */}
          <div>
            <label htmlFor="template" className="block text-sm font-medium text-gray-700">
              Start with Template (Optional)
            </label>
            <select
              id="template"
              value={selectedTemplate}
              onChange={(e) => {
                setSelectedTemplate(e.target.value);
                if (e.target.value) {
                  applyTemplate(e.target.value);
                }
              }}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Choose a template or start from scratch</option>
              {WORKFLOW_TEMPLATES.map((template) => (
                <option key={template.name} value={template.name}>
                  {template.name} - {template.description}
                </option>
              ))}
            </select>
          </div>

          {/* Basic Information */}
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Workflow Name *
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.name ? 'border-red-300' : ''
                }`}
                placeholder="Enter workflow name"
                maxLength={100}
              />
              {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.description ? 'border-red-300' : ''
                }`}
                placeholder="Describe what this workflow accomplishes"
                maxLength={1000}
              />
              {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
            </div>

            <div>
              <label htmlFor="goal" className="block text-sm font-medium text-gray-700">
                Workflow Goal *
              </label>
              <textarea
                id="goal"
                value={formData.goal}
                onChange={(e) => setFormData(prev => ({ ...prev, goal: e.target.value }))}
                rows={3}
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.goal ? 'border-red-300' : ''
                }`}
                placeholder="Define the specific goal this workflow should achieve"
              />
              {errors.goal && <p className="mt-1 text-sm text-red-600">{errors.goal}</p>}
              <p className="mt-1 text-sm text-gray-500">
                Be specific about what success looks like for this workflow.
              </p>
            </div>
          </div>

          {/* Configuration */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label htmlFor="max_duration_seconds" className="block text-sm font-medium text-gray-700">
                Max Duration (seconds)
              </label>
              <input
                type="number"
                id="max_duration_seconds"
                value={formData.max_duration_seconds}
                onChange={(e) => setFormData(prev => ({ ...prev, max_duration_seconds: parseInt(e.target.value) }))}
                min="60"
                max="86400"
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.max_duration_seconds ? 'border-red-300' : ''
                }`}
              />
              {errors.max_duration_seconds && <p className="mt-1 text-sm text-red-600">{errors.max_duration_seconds}</p>}
            </div>

            <div>
              <label htmlFor="max_cost_usd" className="block text-sm font-medium text-gray-700">
                Max Cost (USD)
              </label>
              <input
                type="number"
                id="max_cost_usd"
                value={formData.max_cost_usd}
                onChange={(e) => setFormData(prev => ({ ...prev, max_cost_usd: parseFloat(e.target.value) }))}
                step="0.1"
                min="0.1"
                max="1000"
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.max_cost_usd ? 'border-red-300' : ''
                }`}
              />
              {errors.max_cost_usd && <p className="mt-1 text-sm text-red-600">{errors.max_cost_usd}</p>}
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="require_human_approval"
                checked={formData.require_human_approval}
                onChange={(e) => setFormData(prev => ({ ...prev, require_human_approval: e.target.checked }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="require_human_approval" className="ml-2 block text-sm text-gray-700">
                Require human approval
              </label>
            </div>
          </div>

          {/* Agent Selection */}
          {agents && agents.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Agents (Optional)
              </label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                {agents.map((agent) => (
                  <label key={agent.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.agent_ids.includes(agent.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFormData(prev => ({ ...prev, agent_ids: [...prev.agent_ids, agent.id] }));
                        } else {
                          setFormData(prev => ({ ...prev, agent_ids: prev.agent_ids.filter(id => id !== agent.id) }));
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">{agent.name}</span>
                  </label>
                ))}
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Leave empty to let the system auto-assign agents based on task requirements.
              </p>
            </div>
          )}

          {/* Tasks */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="block text-sm font-medium text-gray-700">
                Workflow Tasks (Optional)
              </label>
              <button
                type="button"
                onClick={addTask}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                + Add Task
              </button>
            </div>
            
            {formData.tasks.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4 border-2 border-dashed border-gray-300 rounded-md">
                No tasks defined. The system will auto-generate tasks based on the workflow goal.
              </p>
            ) : (
              <div className="space-y-3">
                {formData.tasks.map((task, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="text-sm font-medium text-gray-700">Task {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeTask(index)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <input
                        type="text"
                        placeholder="Task name"
                        value={task.name}
                        onChange={(e) => updateTask(index, 'name', e.target.value)}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                      />
                      <input
                        type="text"
                        placeholder="Task description"
                        value={task.description}
                        onChange={(e) => updateTask(index, 'description', e.target.value)}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </form>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={createWorkflow.isPending}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createWorkflow.isPending ? 'Creating...' : 'Create Workflow'}
          </button>
        </div>
      </div>
    </div>
  );
}