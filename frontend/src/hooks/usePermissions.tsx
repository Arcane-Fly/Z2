/**
 * Hook for checking user permissions and superuser status
 */

import { useAuth } from './useAuth';

export function usePermissions() {
  const { authState } = useAuth();

  const isSuperuser = authState.user?.is_superuser || false;
  const userRole = authState.user?.user_type;
  const isAuthenticated = authState.isAuthenticated;

  // Role hierarchy for permission checking
  const roleHierarchy: Record<string, number> = {
    viewer: 1,
    operator: 2,
    developer: 3,
    manager: 4,
    admin: 5,
  };

  const hasRole = (requiredRole: string): boolean => {
    if (!authState.user) return false;
    
    // Superusers always have access
    if (isSuperuser) return true;
    
    const requiredLevel = roleHierarchy[requiredRole] || 0;
    const userLevel = roleHierarchy[userRole || ''] || 0;
    
    return userLevel >= requiredLevel;
  };

  const hasAnyRole = (roles: string[]): boolean => {
    return roles.some(role => hasRole(role));
  };

  const canManageUsers = (): boolean => {
    return isSuperuser || hasRole('admin') || hasRole('manager');
  };

  const canManageSystem = (): boolean => {
    return isSuperuser || hasRole('admin');
  };

  const canCreateAgents = (): boolean => {
    return isSuperuser || hasRole('developer');
  };

  const canCreateWorkflows = (): boolean => {
    return isSuperuser || hasRole('developer');
  };

  const canViewMetrics = (): boolean => {
    return isSuperuser || hasRole('manager');
  };

  return {
    isSuperuser,
    userRole,
    isAuthenticated,
    hasRole,
    hasAnyRole,
    canManageUsers,
    canManageSystem,
    canCreateAgents,
    canCreateWorkflows,
    canViewMetrics,
  };
}

export default usePermissions;