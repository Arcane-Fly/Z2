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

export function LoginForm({
  onSuccess,
  onSwitchToRegister,
}: LoginFormProps): JSX.Element {
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
    <div className='min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center py-12 px-4'>
      <div className='w-full max-w-md'>
        {/* Logo and Title Section */}
        <div className='text-center mb-8'>
          <div className='mx-auto mb-6 h-20 w-20 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-2xl flex items-center justify-center shadow-[0_20px_40px_rgba(79,172,254,0.3)]'>
            <span className='text-white font-bold text-2xl'>Z2</span>
          </div>
          <h1 className='text-4xl font-bold text-white mb-2'>Welcome Back</h1>
          <p className='text-lg text-white/80'>
            Sign in to your Z2 AI Workforce Platform
          </p>
        </div>

        {/* Main Form Card */}
        <div className='bg-white/95 backdrop-blur-2xl rounded-3xl p-8 shadow-2xl border border-white/20'>
          {authState.error && (
            <div className='mb-6 p-4 bg-red-100 border border-red-200 rounded-xl'>
              <div className='flex'>
                <div className='flex-shrink-0'>
                  <svg
                    className='h-5 w-5 text-red-600'
                    viewBox='0 0 20 20'
                    fill='currentColor'
                  >
                    <path
                      fillRule='evenodd'
                      d='M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z'
                      clipRule='evenodd'
                    />
                  </svg>
                </div>
                <div className='ml-3'>
                  <h3 className='text-sm font-medium text-red-700'>
                    Authentication Error
                  </h3>
                  <div className='mt-1 text-sm text-red-600'>
                    {authState.error}
                  </div>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className='flex flex-col gap-6'>
            {/* Username Field */}
            <div>
              <label
                htmlFor='username'
                className='block text-sm font-semibold text-gray-700 mb-2'
              >
                Username
              </label>
              <div className='relative'>
                <input
                  id='username'
                  name='username'
                  type='text'
                  autoComplete='username'
                  required
                  className='block w-full pl-11 pr-4 py-3 bg-white border-2 border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-all shadow-sm'
                  placeholder='Enter your username'
                  value={formData.username}
                  onChange={handleChange}
                  disabled={isLoading}
                />
                <div className='pointer-events-none absolute inset-y-0 left-0 pl-3 flex items-center'>
                  <svg
                    className='h-5 w-5 text-gray-400'
                    fill='none'
                    viewBox='0 0 24 24'
                    stroke='currentColor'
                  >
                    <path
                      strokeLinecap='round'
                      strokeLinejoin='round'
                      strokeWidth={2}
                      d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label
                htmlFor='password'
                className='block text-sm font-semibold text-gray-700 mb-2'
              >
                Password
              </label>
              <div className='relative'>
                <input
                  id='password'
                  name='password'
                  type={showPassword ? 'text' : 'password'}
                  autoComplete='current-password'
                  required
                  className='block w-full px-4 py-3 pr-12 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 shadow-sm hover:shadow-md'
                  placeholder='Enter your password'
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
                />
                <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
                  <svg
                    className='h-5 w-5 text-gray-400'
                    fill='none'
                    viewBox='0 0 24 24'
                    stroke='currentColor'
                  >
                    <path
                      strokeLinecap='round'
                      strokeLinejoin='round'
                      strokeWidth={2}
                      d='M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z'
                    />
                  </svg>
                </div>
                <button
                  type='button'
                  className='absolute inset-y-0 right-0 pr-3 flex items-center hover:text-gray-600 transition-colors'
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <svg
                      className='h-5 w-5 text-gray-400'
                      fill='none'
                      viewBox='0 0 24 24'
                      stroke='currentColor'
                    >
                      <path
                        strokeLinecap='round'
                        strokeLinejoin='round'
                        strokeWidth={2}
                        d='M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464M18.364 18.364L16.95 16.95M18.364 18.364L20 20M8.464 8.464L7.05 7.05M16.95 16.95l1.414 1.414M20 20l-1.414-1.414M16.95 16.95L20 20'
                      />
                    </svg>
                  ) : (
                    <svg
                      className='h-5 w-5 text-gray-400'
                      fill='none'
                      viewBox='0 0 24 24'
                      stroke='currentColor'
                    >
                      <path
                        strokeLinecap='round'
                        strokeLinejoin='round'
                        strokeWidth={2}
                        d='M15 12a3 3 0 11-6 0 3 3 0 016 0z'
                      />
                      <path
                        strokeLinecap='round'
                        strokeLinejoin='round'
                        strokeWidth={2}
                        d='M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z'
                      />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me and Forgot Password */}
            <div className='flex items-center justify-between'>
              <div className='flex items-center'>
                <input
                  id='remember_me'
                  name='remember_me'
                  type='checkbox'
                  className='h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded transition-colors'
                  checked={formData.remember_me}
                  onChange={handleChange}
                  disabled={isLoading}
                />
                <label
                  htmlFor='remember_me'
                  className='ml-2 block text-sm font-medium text-gray-700'
                >
                  Remember me
                </label>
              </div>

              <div className='text-sm'>
                <button
                  type='button'
                  className='font-medium text-blue-600 hover:text-blue-500 transition-colors disabled:opacity-50'
                  disabled={isLoading}
                  onClick={() => {
                    // Create a mailto link for password reset requests
                    const subject = encodeURIComponent(
                      'Z2 Password Reset Request'
                    );
                    const body = encodeURIComponent(
                      'Please reset my password for my Z2 account.\n\n' +
                        'Account username: ' +
                        (formData.username || '[Enter your username]') +
                        '\n\n' +
                        'Please send password reset instructions to this email address.'
                    );
                    window.location.href = `mailto:support@z2.ai?subject=${subject}&body=${body}`;
                  }}
                >
                  Forgot password?
                </button>
              </div>
            </div>

            {/* Sign In Button */}
            <button
              type='submit'
              disabled={isLoading}
              className='group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-semibold rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
            >
              {isLoading ? (
                <div className='flex items-center'>
                  <div className='animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2'></div>
                  Signing in...
                </div>
              ) : (
                <div className='flex items-center'>
                  <svg
                    className='h-5 w-5 mr-2'
                    fill='none'
                    viewBox='0 0 24 24'
                    stroke='currentColor'
                  >
                    <path
                      strokeLinecap='round'
                      strokeLinejoin='round'
                      strokeWidth={2}
                      d='M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1'
                    />
                  </svg>
                  Sign in to Z2
                </div>
              )}
            </button>

            {/* Register Link */}
            {onSwitchToRegister && (
              <div className='text-center pt-4 border-t border-gray-200'>
                <span className='text-sm text-gray-600'>
                  New to Z2?{' '}
                  <button
                    type='button'
                    className='font-semibold text-blue-600 hover:text-blue-500 transition-colors'
                    onClick={onSwitchToRegister}
                    disabled={isLoading}
                  >
                    Create your account
                  </button>
                </span>
              </div>
            )}
          </form>
        </div>

        {/* Security Note */}
        <div className='text-center'>
          <p className='text-xs text-gray-500'>
            🔒 Your data is protected by enterprise-grade security
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;
