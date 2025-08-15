import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import AuthPage from './pages/Auth';
import { DemoPage } from './pages/DemoPage';
import { Layout } from '@/components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { Agents } from './pages/Agents';
import { Workflows } from './pages/Workflows';
import { Models } from './pages/Models';
import { Settings } from './pages/Settings';
import ProtectedRoute from './components/ProtectedRoute';
import { Toaster } from '@/components/ui/toaster';

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-background">
        <Routes>
          {/* Public routes */}
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/demo" element={<DemoPage />} />
          
          {/* Protected routes with layout */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/agents" 
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <Agents />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/workflows" 
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <Workflows />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/models" 
            element={
              <ProtectedRoute requiredRole="developer">
                <Layout>
                  <Models />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute requiredRole="manager">
                <Layout>
                  <Settings />
                </Layout>
              </ProtectedRoute>
            } 
          />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
        <Toaster />
      </div>
    </AuthProvider>
  );
}

export default App;