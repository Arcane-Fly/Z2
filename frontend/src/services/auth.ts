/**
 * Authentication service for Z2 platform
 */

import { 
  LoginRequest, 
  RegisterRequest, 
  TokenResponse, 
  User as AuthUser 
} from '../types/auth';

// Construct the API base URL. In development we default to the backend running on
// localhost without an API prefix. In production, VITE_API_BASE_URL should be
// set to the backend domain without the `/api/v1` suffix. To avoid missing or
// duplicated prefixes we normalise here.

// Protocol-aware fallback for production environments
const getApiRoot = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    // In production HTTPS, use HTTPS with backend domain
    return `https://${window.location.hostname.replace('z2-production', 'z2-backend-production')}`;
  }
  
  return 'http://localhost:8000';
};

const apiRoot = getApiRoot();
// Append `/api/v1` if not already present
const API_BASE_URL = apiRoot.endsWith('/api/v1') ? apiRoot : `${apiRoot}/api/v1`;

class AuthService {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}/auth`;
  }

  /**
   * Get the authorization header with current token
   */
  private getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  /**
   * Make an authenticated API request
   */
  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ 
        error: 'Request failed' 
      }));
      throw new Error(error.detail || error.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Store authentication tokens
   */
  private storeTokens(tokenResponse: TokenResponse): void {
    localStorage.setItem('access_token', tokenResponse.access_token);
    
    if (tokenResponse.refresh_token) {
      localStorage.setItem('refresh_token', tokenResponse.refresh_token);
    }

    // Store expiration time
    const expiresAt = Date.now() + (tokenResponse.expires_in * 1000);
    localStorage.setItem('token_expires_at', expiresAt.toString());
  }

  /**
   * Get stored access token
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Get stored refresh token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  /**
   * Check if token is expired
   */
  isTokenExpired(): boolean {
    const expiresAt = localStorage.getItem('token_expires_at');
    if (!expiresAt) return true;
    
    return Date.now() > parseInt(expiresAt, 10);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    return token !== null && !this.isTokenExpired();
  }

  /**
   * Clear all stored tokens
   */
  clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires_at');
  }

  /**
   * User login
   */
  async login(credentials: LoginRequest): Promise<{ user: AuthUser; tokens: TokenResponse }> {
    const tokenResponse = await this.makeRequest<TokenResponse>('/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    this.storeTokens(tokenResponse);

    // Get user profile after successful login
    const user = await this.getCurrentUser();

    return { user, tokens: tokenResponse };
  }

  /**
   * User registration
   */
  async register(userData: RegisterRequest): Promise<{ user: AuthUser; tokens: TokenResponse }> {
    const tokenResponse = await this.makeRequest<TokenResponse>('/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    this.storeTokens(tokenResponse);

    // Get user profile after successful registration
    const user = await this.getCurrentUser();

    return { user, tokens: tokenResponse };
  }

  /**
   * User logout
   */
  async logout(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    
    try {
      await this.makeRequest('/logout', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch (error) {
      console.warn('Logout request failed:', error);
      // Continue with local cleanup even if server request fails
    } finally {
      this.clearTokens();
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<TokenResponse> {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const tokenResponse = await this.makeRequest<TokenResponse>('/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    this.storeTokens(tokenResponse);
    return tokenResponse;
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<AuthUser> {
    return this.makeRequest<AuthUser>('/me');
  }

  /**
   * Auto-refresh token if needed
   */
  async ensureValidToken(): Promise<string | null> {
    const token = this.getToken();
    
    if (!token) {
      return null;
    }

    // If token is expired or will expire in the next 5 minutes, try to refresh
    const expiresAt = localStorage.getItem('token_expires_at');
    const fiveMinutesFromNow = Date.now() + (5 * 60 * 1000);
    
    if (expiresAt && parseInt(expiresAt, 10) < fiveMinutesFromNow) {
      try {
        await this.refreshToken();
        return this.getToken();
      } catch (error) {
        console.warn('Token refresh failed:', error);
        this.clearTokens();
        return null;
      }
    }

    return token;
  }
}

export const authService = new AuthService();
export default authService;