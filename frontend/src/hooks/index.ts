/**
 * Custom React hooks for the Z2 platform
 */

import { useState, useEffect, useCallback } from 'react';
import { User, LoadingState } from '../types';
import { apiService } from '../services/api';

// Export all MCP hooks
export * from './useMCP';

// Authentication hook
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const token = localStorage.getItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'z2_auth_token');
    if (token) {
      apiService.getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'z2_auth_token');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await apiService.login({ email, password });
    localStorage.setItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'z2_auth_token', tokens.access_token);
    if (tokens.refresh_token) {
      localStorage.setItem(import.meta.env.VITE_REFRESH_TOKEN_KEY || 'z2_refresh_token', tokens.refresh_token);
    }
    const currentUser = await apiService.getCurrentUser();
    setUser(currentUser);
    return currentUser;
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiService.logout();
    } catch (error) {
      // Continue with logout even if API call fails
    }
    localStorage.removeItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'z2_auth_token');
    localStorage.removeItem(import.meta.env.VITE_REFRESH_TOKEN_KEY || 'z2_refresh_token');
    setUser(null);
  }, []);

  return { user, loading, login, logout, isAuthenticated: !!user };
}

// Generic data fetching hook
export function useApiData<T>(
  fetchFn: () => Promise<T>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [state, setState] = useState<LoadingState>('idle');
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setState('loading');
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
      setState('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setState('error');
    }
  }, dependencies);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const refetch = useCallback(() => {
    fetch();
  }, [fetch]);

  return { data, state, error, loading: state === 'loading', refetch };
}

// Agents hook
export function useAgents() {
  return useApiData(() => apiService.getAgents());
}

// Single agent hook
export function useAgent(id: string) {
  return useApiData(() => apiService.getAgent(id), [id]);
}

// Workflows hook
export function useWorkflows() {
  return useApiData(() => apiService.getWorkflows());
}

// Single workflow hook
export function useWorkflow(id: string) {
  return useApiData(() => apiService.getWorkflow(id), [id]);
}

// Local storage hook
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('Error setting localStorage:', error);
    }
  };

  return [storedValue, setValue] as const;
}

// Theme hook
export function useTheme() {
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('theme', 'light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme(current => current === 'light' ? 'dark' : 'light');
  }, [setTheme]);

  return { theme, setTheme, toggleTheme };
}

// Debounced value hook
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}