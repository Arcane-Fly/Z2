import React from 'react';
import { Routes, Route, Navigate, BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import AuthPage from './pages/Auth';
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
      <Router>
        <div className="min-h-screen bg-background">
          <Routes>
            {/* Public routes */}
            <Route path="/auth" element={<AuthPage />} />
            
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
      </Router>
    </AuthProvider>
  );
}

export default App;