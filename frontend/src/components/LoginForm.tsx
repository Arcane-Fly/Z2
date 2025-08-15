/**
 * Login form component for Z2 platform
 */
import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { LoginRequest } from '../types/auth';

interface LoginFormProps {
  /** Callback executed after a successful login */
  onSuccess?: () => void;
  /** Switch the UI to a registration view */
  onSwitchToRegister?: () => void;
}

/**
 * Renders the login form for the Z2 AI Workforce Platform.
 *
 * This component uses the `useAuth` hook to perform authentication,
 * handles form state, loading state, and error presentation.
 *
 * **Styling**
 * The component is primarily styled using Tailwind CSS.
 * Inline styles are used only where dynamic styling is required
 * (e.g. loading state, hover effects).
 */
export function LoginForm({
  onSuccess,
  onSwitchToRegister,
}: LoginFormProps): React.JSX.Element {
  const { login, authState, clearError } = useAuth();

  const [formData, setFormData] = useState<LoginRequest>({
    username: '',
    password: '',
    remember_me: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const isLoading = authState.isLoading;

  /** Handles updates to any input field */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  /** Submit handler for the login form */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    try {
      await login(formData);
      onSuccess?.();
    } catch {
      // Errors are handled inside the auth context
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <div className="mx-auto mb-6 h-20 w-20 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-2xl flex items-center justify-center shadow-[0_20px_40px_rgba(79,172,254,0.3)]">
            <span className="text-white font-bold text-2xl">Z2</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-lg text-white/80">
            Sign in to your Z2 AI Workforce Platform
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white/95 backdrop-blur-2xl rounded-3xl p-8 shadow-2xl border border-white/20">
          {authState.error && (
            <div className="mb-6 p-4 bg-red-100 border border-red-200 rounded-xl">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-600"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm8.707-10.707a1 1 0 00-1.414-1.414L8.586 10l-1.293-1.293a1 1 0 00-1.414 1.414L8.586 10l-1.293-1.293a1 1 0 011.414-1.414L8.586 8.586l-1.293-1.293a1 1 0 011.414-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-700">
                    Authentication Error
                  </h3>
                  <p className="mt-1 text-sm text-red-600">{authState.error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Form */}
          <form
            onSubmit={handleSubmit}
            style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}
          >
            {/* Username */}
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                Username
              </label>
              <div className="relative">
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  className="block w-full pl-11 pr-4 py-3 bg-white border-2 border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-all shadow-sm"
                  placeholder="Enter your username"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={isLoading}
                  onFocus={(e) =>
                    ((e.target as HTMLInputElement).style.borderColor =
                      '#3b82f6')
                  }
                  onBlur={(e) =>
                    ((e.target as HTMLInputElement).style.borderColor =
                      '#e5e7eb')
                  }
                />
                <div className="pointer-events-none absolute inset-y-0 left-0 pl-3 flex items-center">
                  <svg
                    className="h-5 w-5 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '12px 44px 12px 44px',
                    background: 'white',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '16px',
                    color: '#111827',
                    outline: 'none',
                    transition: 'all 0.2s',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    boxSizing: 'border-box',
                  }}
                  onFocus={(e) =>
                    ((e.target as HTMLInputElement).style.borderColor =
                      '#3b82f6')
                  }
                  onBlur={(e) =>
                    ((e.target as HTMLInputElement).style.borderColor =
                      '#e5e7eb')
                  }
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg
                    className="h-5 w-5 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
                <button
                  type="button"
                  style={{
                    position: 'absolute',
                    top: '50%',
                    right: '12px',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: isLoading ? 'default' : 'pointer',
                    color: '#9ca3af',
                    padding: 0,
                    opacity: isLoading ? 0.5 : 1,
                  }}
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                  onMouseEnter={(e) =>
                    !isLoading &&
                    ((e.target as HTMLElement).style.color = '#6b7280')
                  }
                  onMouseLeave={(e) =>
                    !isLoading &&
                    ((e.target as HTMLElement).style.color = '#9ca3af')
                  }
                >
                  {showPassword ? (
                    <svg
                      className="h-5 w-5 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464M18.364 18.364L16.95 16.95M18.364 18.364L20 20M8.464 8.464L7.05 7.05M16.95 16.95l1.414 1.414M20 20l-1.414-1.414M16.95 16.95L20 20"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="h-5 w-5 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Remember me & Forgot password */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <input
                  id="remember_me"
                  name="remember_me"
                  type="checkbox"
                  checked={formData.remember_me}
                  onChange={handleChange}
                  disabled={isLoading}
                  style={{
                    height: '16px',
                    width: '16px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    color: '#3b82f6',
                    cursor: isLoading ? 'default' : 'pointer',
                    opacity: isLoading ? 0.5 : 1,
                  }}
                />
                <label
                  htmlFor="remember_me"
                  style={{
                    marginLeft: '8px',
                    fontSize: '14px',
                    fontWeight: 500,
                    color: '#374151',
                    cursor: isLoading ? 'default' : 'pointer',
                    opacity: isLoading ? 0.5 : 1,
                  }}
                >
                  Remember me
                </label>
              </div>

              <button
                type="button"
                style={{
                  fontWeight: 500,
                  color: '#3b82f6',
                  background: 'none',
                  border: 'none',
                  cursor: isLoading ? 'default' : 'pointer',
                  transition: 'color 0.2s',
                  opacity: isLoading ? 0.5 : 1,
                }}
                onClick={() => {
                  const subject = encodeURIComponent(
                    'Z2 Password Reset Request',
                  );
                  const body = encodeURIComponent(
                    `Please reset my password for my Z2 account.\n\n` +
                      `Account username: ${formData.username || '[Enter your username]'}\n\n` +
                      `Please send password reset instructions to this email address.`,
                  );
                  window.location.href = `mailto:support@z2.ai?subject=${subject}&body=${body}`;
                }}
                disabled={isLoading}
                onMouseEnter={(e) =>
                  !isLoading &&
                  ((e.target as HTMLElement).style.color = '#2563eb')
                }
                onMouseLeave={(e) =>
                  !isLoading &&
                  ((e.target as HTMLElement).style.color = '#3b82f6')
                }
              >
                Forgot password?
              </button>
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
                opacity: isLoading ? 0.7 : 1,
                fontFamily: 'system-ui, -apple-system, sans-serif',
                transform: 'translateY(0)',
              }}
              onMouseEnter={(e) => {
                if (!isLoading) {
                  const t = e.target as HTMLElement;
                  t.style.background =
                    'linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)';
                  t.style.transform = 'translateY(-2px)';
                  t.style.boxShadow = '0 15px 35px rgba(59, 130, 246, 0.4)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoading) {
                  const t = e.target as HTMLElement;
                  t.style.background =
                    'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)';
                  t.style.transform = 'translateY(0)';
                  t.style.boxShadow = '0 10px 25px rgba(59, 130, 246, 0.3)';
                }
              }}
            >
              {isLoading ? (
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div
                    style={{
                      width: '20px',
                      height: '20px',
                      border: '2px solid transparent',
                      borderTop: '2px solid white',
                      borderRadius: '50%',
                      marginRight: '8px',
                      animation: 'spin 1s linear infinite',
                    }}
                  />
                  Signing in...
                </div>
              ) : (
                <div className="flex items-center">
                  <svg
                    className="h-5 w-5 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 16L7 12l4-4M7 12l4-4M11 12h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
                    />
                  </svg>
                  Sign in to Z2
                </div>
              )}
            </button>

            {/* Register link */}
            {onSwitchToRegister && (
              <div
                style={{
                  textAlign: 'center',
                  paddingTop: '16px',
                  borderTop: '1px solid #e5e7eb',
                }}
              >
                <span style={{ fontSize: '14px', color: '#6b7280' }}>
                  New to Z2?{' '}
                  <button
                    type="button"
                    style={{
                      fontWeight: 600,
                      color: '#3b82f6',
                      background: 'none',
                      border: 'none',
                      cursor: isLoading ? 'default' : 'pointer',
                      opacity: isLoading ? 0.5 : 1,
                      transition: 'color 0.2s',
                    }}
                    onClick={onSwitchToRegister}
                    disabled={isLoading}
                    onMouseEnter={(e) =>
                      !isLoading &&
                      ((e.target as HTMLElement).style.color = '#2563eb')
                    }
                    onMouseLeave={(e) =>
                      !isLoading &&
                      ((e.target as HTMLElement).style.color = '#3b82f6')
                    }
                  >
                    Create your account
                  </button>
                </span>
              </div>
            )}
          </form>
        </div>

        {/* Security note */}
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <p
            style={{
              fontSize: '12px',
              color: 'rgba(255,255,255,0.7)',
              fontFamily: 'system-ui, -apple-system, sans-serif',
              margin: 0,
            }}
          >
            🔐 Your data is protected by enterprise‑grade security
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;