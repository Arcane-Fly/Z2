import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Agent, Workflow } from '../types';

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => apiService.getDashboardStats(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};

export const useAgents = () => {
  return useQuery({
    queryKey: ['agents'],
    queryFn: () => apiService.getAgents(),
  });
};

export const useCreateAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (agent: Partial<Agent>) => apiService.createAgent(agent),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
};

export const useUpdateAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, agent }: { id: string; agent: Partial<Agent> }) => 
      apiService.updateAgent(id, agent),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
};

export const useDeleteAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => apiService.deleteAgent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
};

export const useWorkflows = () => {
  return useQuery({
    queryKey: ['workflows'],
    queryFn: () => apiService.getWorkflows(),
  });
};

export const useCreateWorkflow = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (workflow: Partial<Workflow>) => apiService.createWorkflow(workflow),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });
};

export const useUpdateWorkflow = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, workflow }: { id: string; workflow: Partial<Workflow> }) => 
      apiService.updateWorkflow(id, workflow),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });
};

export const useDeleteWorkflow = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => apiService.deleteWorkflow(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });
};

export const useModels = () => {
  return useQuery({
    queryKey: ['models'],
    queryFn: () => apiService.getModels(),
  });
};