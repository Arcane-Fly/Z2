import { useState } from 'react';
import { useCreateAgent } from '../../hooks/useApi';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface CreateAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AGENT_ROLES = [
  { value: 'researcher', label: 'Researcher', description: 'Gathers and analyzes information' },
  { value: 'analyst', label: 'Analyst', description: 'Interprets data and provides insights' },
  { value: 'writer', label: 'Writer', description: 'Creates content and documentation' },
  { value: 'coder', label: 'Coder', description: 'Writes and reviews code' },
  { value: 'reviewer', label: 'Reviewer', description: 'Evaluates and provides feedback' },
  { value: 'planner', label: 'Planner', description: 'Develops strategies and plans' },
  { value: 'executor', label: 'Executor', description: 'Executes tasks and processes' },
  { value: 'coordinator', label: 'Coordinator', description: 'Manages team coordination' },
  { value: 'validator', label: 'Validator', description: 'Validates outputs and quality' },
];

const SYSTEM_PROMPT_TEMPLATES = {
  researcher: "You are a thorough researcher agent. Your role is to gather comprehensive information, analyze sources, and provide well-documented findings. Always cite your sources and present balanced perspectives.",
  analyst: "You are an analytical agent focused on data interpretation and insight generation. Break down complex information, identify patterns, and provide actionable recommendations based on evidence.",
  writer: "You are a professional writing agent. Create clear, engaging, and well-structured content. Adapt your writing style to the target audience and purpose while maintaining high quality standards.",
  coder: "You are an expert programming agent. Write clean, efficient, and well-documented code. Follow best practices, consider edge cases, and provide clear explanations for your implementations.",
  reviewer: "You are a meticulous review agent. Provide constructive feedback, identify areas for improvement, and ensure quality standards are met. Be specific and actionable in your recommendations.",
  planner: "You are a strategic planning agent. Develop comprehensive plans, break down complex goals into actionable steps, and consider risks and dependencies in your planning process.",
  executor: "You are a reliable execution agent. Focus on completing tasks efficiently and accurately. Follow instructions precisely while being adaptable to changing requirements.",
  coordinator: "You are a coordination agent responsible for managing team workflows. Facilitate communication, track progress, and ensure all team members are aligned and productive.",
  validator: "You are a quality validation agent. Verify outputs meet requirements, check for accuracy and completeness, and ensure deliverables are ready for use or deployment.",
};

export function CreateAgentModal({ isOpen, onClose }: CreateAgentModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    role: '',
    system_prompt: '',
    temperature: 0.7,
    max_tokens: 4096,
    timeout_seconds: 300,
    tools: [] as string[],
    skills: [] as string[],
    preferred_models: [] as string[],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const createAgent = useCreateAgent();

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

    if (!formData.role) {
      newErrors.role = 'Role is required';
    }

    if (!formData.system_prompt.trim()) {
      newErrors.system_prompt = 'System prompt is required';
    } else if (formData.system_prompt.length < 10) {
      newErrors.system_prompt = 'System prompt must be at least 10 characters';
    }

    if (formData.temperature < 0 || formData.temperature > 2) {
      newErrors.temperature = 'Temperature must be between 0 and 2';
    }

    if (formData.max_tokens < 1 || formData.max_tokens > 32000) {
      newErrors.max_tokens = 'Max tokens must be between 1 and 32000';
    }

    if (formData.timeout_seconds < 30 || formData.timeout_seconds > 3600) {
      newErrors.timeout_seconds = 'Timeout must be between 30 and 3600 seconds';
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
      await createAgent.mutateAsync(formData);
      onClose();
      // Reset form
      setFormData({
        name: '',
        description: '',
        role: '',
        system_prompt: '',
        temperature: 0.7,
        max_tokens: 4096,
        timeout_seconds: 300,
        tools: [],
        skills: [],
        preferred_models: [],
      });
      setErrors({});
    } catch (error) {
      console.error('Failed to create agent:', error);
      setErrors({ submit: 'Failed to create agent. Please try again.' });
    }
  };

  const handleRoleChange = (role: string) => {
    setFormData(prev => ({
      ...prev,
      role,
      system_prompt: SYSTEM_PROMPT_TEMPLATES[role as keyof typeof SYSTEM_PROMPT_TEMPLATES] || prev.system_prompt
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Create New Agent</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          {errors.submit && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-sm text-red-600">{errors.submit}</p>
            </div>
          )}

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Agent Name *
            </label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                errors.name ? 'border-red-300' : ''
              }`}
              placeholder="Enter agent name"
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
              placeholder="Describe what this agent does"
              maxLength={1000}
            />
            {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
          </div>

          <div>
            <label htmlFor="role" className="block text-sm font-medium text-gray-700">
              Agent Role *
            </label>
            <select
              id="role"
              value={formData.role}
              onChange={(e) => handleRoleChange(e.target.value)}
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                errors.role ? 'border-red-300' : ''
              }`}
            >
              <option value="">Select a role</option>
              {AGENT_ROLES.map((role) => (
                <option key={role.value} value={role.value}>
                  {role.label} - {role.description}
                </option>
              ))}
            </select>
            {errors.role && <p className="mt-1 text-sm text-red-600">{errors.role}</p>}
          </div>

          <div>
            <label htmlFor="system_prompt" className="block text-sm font-medium text-gray-700">
              System Prompt *
            </label>
            <textarea
              id="system_prompt"
              value={formData.system_prompt}
              onChange={(e) => setFormData(prev => ({ ...prev, system_prompt: e.target.value }))}
              rows={4}
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                errors.system_prompt ? 'border-red-300' : ''
              }`}
              placeholder="Define the agent's behavior and instructions"
            />
            {errors.system_prompt && <p className="mt-1 text-sm text-red-600">{errors.system_prompt}</p>}
            <p className="mt-1 text-sm text-gray-500">
              This prompt will guide the agent's behavior and responses. Be specific about the agent's role and responsibilities.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label htmlFor="temperature" className="block text-sm font-medium text-gray-700">
                Temperature
              </label>
              <input
                type="number"
                id="temperature"
                value={formData.temperature}
                onChange={(e) => setFormData(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                step="0.1"
                min="0"
                max="2"
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.temperature ? 'border-red-300' : ''
                }`}
              />
              {errors.temperature && <p className="mt-1 text-sm text-red-600">{errors.temperature}</p>}
            </div>

            <div>
              <label htmlFor="max_tokens" className="block text-sm font-medium text-gray-700">
                Max Tokens
              </label>
              <input
                type="number"
                id="max_tokens"
                value={formData.max_tokens}
                onChange={(e) => setFormData(prev => ({ ...prev, max_tokens: parseInt(e.target.value) }))}
                min="1"
                max="32000"
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.max_tokens ? 'border-red-300' : ''
                }`}
              />
              {errors.max_tokens && <p className="mt-1 text-sm text-red-600">{errors.max_tokens}</p>}
            </div>

            <div>
              <label htmlFor="timeout_seconds" className="block text-sm font-medium text-gray-700">
                Timeout (seconds)
              </label>
              <input
                type="number"
                id="timeout_seconds"
                value={formData.timeout_seconds}
                onChange={(e) => setFormData(prev => ({ ...prev, timeout_seconds: parseInt(e.target.value) }))}
                min="30"
                max="3600"
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.timeout_seconds ? 'border-red-300' : ''
                }`}
              />
              {errors.timeout_seconds && <p className="mt-1 text-sm text-red-600">{errors.timeout_seconds}</p>}
            </div>
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
            disabled={createAgent.isPending}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createAgent.isPending ? 'Creating...' : 'Create Agent'}
          </button>
        </div>
      </div>
    </div>
  );
}