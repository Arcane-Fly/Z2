/**
 * Login form component for Z2 platform
 */
import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { LoginRequest } from '../types/auth';
interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}
export function LoginForm({ onSuccess, onSwitchToRegister }: LoginFormProps): JSX.Element {
  const { login, authState, clearError } = useAuth();
  const [formData, setFormData] = useState<LoginRequest>({
    username: '',
    password: '',
    remember_me: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    try {
      await login(formData);
      onSuccess?.();
    } catch (error) {
      // Error is handled by the auth context
    }
  };
  const isLoading = authState.isLoading;
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 16px'
    }}>
      <div style={{
        maxWidth: '400px',
        width: '100%'
      }}>
        {/* Logo and Title Section */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            margin: '0 auto 24px',
            height: '80px',
            width: '80px',
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 20px 40px rgba(79, 172, 254, 0.3)'
          }}>
            <span style={{
              color: 'white',
              fontWeight: 'bold',
              fontSize: '28px',
              fontFamily: 'system-ui, -apple-system, sans-serif'
            }}>Z2</span>
          </div>
          <h1 style={{
            fontSize: '36px',
            fontWeight: 'bold',
            color: 'white',
            margin: '0 0 8px 0',
            fontFamily: 'system-ui, -apple-system, sans-serif'
          }}>
            Welcome Back
          </h1>
          <p style={{
            fontSize: '18px',
            color: 'rgba(255, 255, 255, 0.8)',
            margin: '0',
            fontFamily: 'system-ui, -apple-system, sans-serif'
          }}>
            Sign in to your Z2 AI Workforce Platform
          </p>
        </div>
        {/* Main Form Card */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          borderRadius: '24px',
          padding: '32px',
          boxShadow: '0 25px 50px rgba(0, 0, 0, 0.15)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          {authState.error && (
            <div style={{
              marginBottom: '24px',
              padding: '16px',
              background: '#fee2e2',
              border: '1px solid #fecaca',
              borderRadius: '12px'
            }}>
              <div style={{ display: 'flex' }}>
                <div style={{ flexShrink: 0 }}>
                  <svg style={{ height: '20px', width: '20px', color: '#ef4444' }} viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div style={{ marginLeft: '12px' }}>
                  <h3 style={{
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#dc2626',
                    margin: 0,
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>
                    Authentication Error
                  </h3>
                  <div style={{
                    marginTop: '4px',
                    fontSize: '14px',
                    color: '#b91c1c',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}>
                    {authState.error}
                  </div>
                </div>
              </div>
            </div>
          )}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Username Field */}
            <div>
              <label htmlFor="username" style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                Username
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '12px 16px 12px 44px',
                    background: 'white',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '16px',
                    color: '#111827',
                    fontFamily: 'system-ui, -apple-system, sans-serif',
                    outline: 'none',
                    transition: 'all 0.2s',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                    boxSizing: 'border-box'
                  }}
                  placeholder="Enter your username"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={isLoading}
                  onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#3b82f6'}
                  onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#e5e7eb'}
                />
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '12px',
                  transform: 'translateY(-50%)',
                  pointerEvents: 'none'
                }}>
                  <svg style={{ height: '20px', width: '20px', color: '#9ca3af' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
            </div>
           
            {/* Password Field */}
            <div>
              <label htmlFor="password" style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '12px 44px 12px 44px',
                    background: 'white',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '16px',
                    color: '#111827',
                    fontFamily: 'system-ui, -apple-system, sans-serif',
                    outline: 'none',
                    transition: 'all 0.2s',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                    boxSizing: 'border-box'
                  }}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
                  onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#3b82f6'}
                  onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#e5e7eb'}
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg
                    className="h-5 w-5 text-gray-400"
                    width={20}
                    height={20}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <button
                  type="button"
                  style={{
                    position: 'absolute',
                    top: '50%',
                    right: '12px',
                    transform: 'translateY(-50%)',
                    display: 'flex',
                    alignItems: 'center',
                    background: 'none',
                    border: 'none',
                    cursor: isLoading ? 'default' : 'pointer',
                    color: '#9ca3af',
                    transition: 'color 0.2s',
                    padding: '0',
                    opacity: isLoading ? 0.5 : 1
                  }}
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                  onMouseEnter={(e) => !isLoading && ((e.target as HTMLElement).style.color = '#6b7280')}
                  onMouseLeave={(e) => !isLoading && ((e.target as HTMLElement).style.color = '#9ca3af')}
                >
                  {showPassword ? (
                    <svg
                      className="h-5 w-5 text-gray-400"
                      width={20}
                      height={20}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464M18.364 18.364L16.95 16.95M18.364 18.364L20 20M8.464 8.464L7.05 7.05M16.95 16.95l1.414 1.414M20 20l-1.414-1.414M16.95 16.95L20 20" />
                    </svg>
                  ) : (
                    <svg
                      className="h-5 w-5 text-gray-400"
                      width={20}
                      height={20}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            {/* Remember Me and Forgot Password */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <input
                  id="remember_me"
                  name="remember_me"
                  type="checkbox"
                  style={{
                    height: '16px',
                    width: '16px',
                    color: '#3b82f6',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    cursor: isLoading ? 'default' : 'pointer',
                    opacity: isLoading ? 0.5 : 1
                  }}
                  checked={formData.remember_me}
                  onChange={handleChange}
                  disabled={isLoading}
                />
                <label htmlFor="remember_me" style={{
                  marginLeft: '8px',
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#374151',
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                  cursor: isLoading ? 'default' : 'pointer',
                  opacity: isLoading ? 0.5 : 1
                }}>
                  Remember me
                </label>
              </div>
              <div style={{ fontSize: '14px' }}>
                <button
                  type="button"
                  style={{
                    fontWeight: '500',
                    color: '#3b82f6',
                    background: 'none',
                    border: 'none',
                    cursor: isLoading ? 'default' : 'pointer',
                    fontFamily: 'system-ui, -apple-system, sans-serif',
                    padding: '0',
                    transition: 'color 0.2s',
                    opacity: isLoading ? 0.5 : 1
                  }}
                  disabled={isLoading}
                  onClick={() => {
                    // Create a mailto link for password reset requests
                    const subject = encodeURIComponent('Z2 Password Reset Request');
                    const body = encodeURIComponent(
                      'Please reset my password for my Z2 account.\n\n' +
                      'Account username: ' + (formData.username || '[Enter your username]') + '\n\n' +
                      'Please send password reset instructions to this email address.'
                    );
                    window.location.href = `mailto:support@z2.ai?subject=${subject}&body=${body}`;
                  }}
                  onMouseEnter={(e) => !isLoading && ((e.target as HTMLElement).style.color = '#2563eb')}
                  onMouseLeave={(e) => !isLoading && ((e.target as HTMLElement).style.color = '#3b82f6')}
                >
                  Forgot password?
                </button>
              </div>
            </div>
            {/* Sign In Button */}
            <button
              type="submit"
              disabled={isLoading}
              style={{
                position: 'relative',
                width: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                padding: '12px 16px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                borderRadius: '12px',
                color: 'white',
                background: isLoading
                  ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)'
                  : 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
                cursor: isLoading ? 'default' : 'pointer',
                transition: 'all 0.2s',
                boxShadow: '0 10px 25px rgba(59, 130, 246, 0.3)',
                transform: 'translateY(0)',
                fontFamily: 'system-ui, -apple-system, sans-serif',
                opacity: isLoading ? 0.7 : 1
              }}
              onMouseEnter={(e) => {
                if (!isLoading) {
                  const target = e.target as HTMLElement;
                  target.style.background = 'linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)';
                  target.style.transform = 'translateY(-2px)';
                  target.style.boxShadow = '0 15px 35px rgba(59, 130, 246, 0.4)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoading) {
                  const target = e.target as HTMLElement;
                  target.style.background = 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)';
                  target.style.transform = 'translateY(0)';
                  target.style.boxShadow = '0 10px 25px rgba(59, 130, 246, 0.3)';
                }
              }}
            >
              {isLoading ? (
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{
                    width: '20px',
                    height: '20px',
                    border: '2px solid transparent',
                    borderTop: '2px solid white',
                    borderRadius: '50%',
                    marginRight: '8px',
                    animation: 'spin 1s linear infinite'
                  }}></div>
                  Signing in...
                </div>
              ) : (
                <div className="flex items-center">
                  <svg
                    className="h-5 w-5 mr-2"
                    width={20}
                    height={20}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  Sign in to Z2
                </div>
              )}
            </button>
            {/* Register Link */}
            {onSwitchToRegister && (
              <div style={{
                textAlign: 'center',
                paddingTop: '16px',
                borderTop: '1px solid #e5e7eb'
              }}>
                <span style={{
                  fontSize: '14px',
                  color: '#6b7280',
                  fontFamily: 'system-ui, -apple-system, sans-serif'
                }}>
                  New to Z2?{' '}
                  <button
                    type="button"
                    style={{
                      fontWeight: '600',
                      color: '#3b82f6',
                      background: 'none',
                      border: 'none',
                      cursor: isLoading ? 'default' : 'pointer',
                      fontFamily: 'system-ui, -apple-system, sans-serif',
                      padding: '0',
                      transition: 'color 0.2s',
                      opacity: isLoading ? 0.5 : 1
                    }}
                    onClick={onSwitchToRegister}
                    disabled={isLoading}
                    onMouseEnter={(e) => !isLoading && ((e.target as HTMLElement).style.color = '#2563eb')}
                    onMouseLeave={(e) => !isLoading && ((e.target as HTMLElement).style.color = '#3b82f6')}
                  >
                    Create your account
                  </button>
                </span>
              </div>
            )}
          </form>
        </div>
        {/* Security Note */}
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <p style={{
            fontSize: '12px',
            color: 'rgba(255, 255, 255, 0.7)',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            margin: '0'
          }}>
            🔒 Your data is protected by enterprise-grade security
          </p>
        </div>
      </div>
    </div>
  );
}
export default LoginForm;