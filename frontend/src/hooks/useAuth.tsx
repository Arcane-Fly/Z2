/**
 * Authentication context and provider for Z2 platform
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { 
  AuthState, 
  AuthContextType, 
  LoginRequest, 
  RegisterRequest, 
  User as AuthUser 
} from '../types/auth';
import { authService } from '../services/auth';

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: AuthUser; token: string; refreshToken?: string } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_CLEAR_ERROR' }
  | { type: 'AUTH_SET_LOADING'; payload: boolean };

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        refreshToken: action.payload.refreshToken || null,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };

    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };

    case 'AUTH_CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    case 'AUTH_SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };

    default:
      return state;
  }
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider props
interface AuthProviderProps {
  children: ReactNode;
}

// Provider component
export function AuthProvider({ children }: AuthProviderProps): React.JSX.Element {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize authentication state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = await authService.ensureValidToken();
        
        if (token) {
          const user = await authService.getCurrentUser();
          const refreshToken = authService.getRefreshToken();
          
          dispatch({
            type: 'AUTH_SUCCESS',
            payload: { user, token, refreshToken: refreshToken || undefined },
          });
        } else {
          dispatch({ type: 'AUTH_SET_LOADING', payload: false });
        }
      } catch (error) {
        console.warn('Auth initialization failed:', error);
        authService.clearTokens();
        dispatch({ type: 'AUTH_SET_LOADING', payload: false });
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginRequest): Promise<void> => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const { user, tokens } = await authService.login(credentials);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user,
          token: tokens.access_token,
          refreshToken: tokens.refresh_token,
        },
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      throw error;
    }
  };

  // Register function
  const register = async (userData: RegisterRequest): Promise<void> => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const { user, tokens } = await authService.register(userData);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user,
          token: tokens.access_token,
          refreshToken: tokens.refresh_token,
        },
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      throw error;
    }
  };

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      dispatch({ type: 'AUTH_LOGOUT' });
    }
  };

  // Refresh authentication
  const refreshAuth = async (): Promise<void> => {
    try {
      const tokens = await authService.refreshToken();
      const user = await authService.getCurrentUser();
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user,
          token: tokens.access_token,
          refreshToken: tokens.refresh_token,
        },
      });
    } catch (error) {
      console.warn('Token refresh failed:', error);
      dispatch({ type: 'AUTH_LOGOUT' });
      throw error;
    }
  };

  // Clear error
  const clearError = (): void => {
    dispatch({ type: 'AUTH_CLEAR_ERROR' });
  };

  // Context value
  const contextValue: AuthContextType = {
    authState: state,
    login,
    register,
    logout,
    refreshAuth,
    clearError,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

// Higher-order component for authentication protection
export function withAuth<P extends object>(
  Component: React.ComponentType<P>
): React.ComponentType<P> {
  return function AuthenticatedComponent(props: P) {
    const { authState } = useAuth();
    
    if (authState.isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      );
    }
    
    if (!authState.isAuthenticated) {
      // Redirect to login or show login form
      return <div>Please log in to access this page.</div>;
    }
    
    return <Component {...props} />;
  };
}