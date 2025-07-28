import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';

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

export const useWorkflows = () => {
  return useQuery({
    queryKey: ['workflows'],
    queryFn: () => apiService.getWorkflows(),
  });
};

export const useModels = () => {
  return useQuery({
    queryKey: ['models'],
    queryFn: () => apiService.getModels(),
  });
};