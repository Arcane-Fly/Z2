/**
 * Authentication page with login and register forms
 */

import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';

export function AuthPage(): React.JSX.Element {
  const { authState } = useAuth();
  const [isLogin, setIsLogin] = useState(true);

  // Redirect if already authenticated
  if (authState.isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleAuthSuccess = () => {
    // Navigation will be handled by the redirect above
  };

  const switchToRegister = () => {
    setIsLogin(false);
  };

  const switchToLogin = () => {
    setIsLogin(true);
  };

  if (isLogin) {
    return (
      <LoginForm
        onSuccess={handleAuthSuccess}
        onSwitchToRegister={switchToRegister}
      />
    );
  }

  return (
    <RegisterForm
      onSuccess={handleAuthSuccess}
      onSwitchToLogin={switchToLogin}
    />
  );
}

export default AuthPage;