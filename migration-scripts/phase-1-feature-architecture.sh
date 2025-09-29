#!/bin/bash
set -euo pipefail

# Phase 1: Migrate to Feature-Based Architecture
# This script reorganizes the Z2 frontend from technical grouping to feature-based domains

echo "🚀 Phase 1: Migrating to Feature-Based Architecture"
echo "=================================================="

# Navigate to frontend directory
cd frontend/src

# Create backup
echo "📦 Creating backup..."
cp -r . ../src-backup-$(date +%Y%m%d-%H%M%S)

# Create feature directories
echo "📁 Creating feature directory structure..."
mkdir -p features/{auth,dashboard,agents,workflows,models}
mkdir -p shared/{components,hooks,utils,types,services}

# Create feature subdirectories
for feature in auth dashboard agents workflows models; do
  mkdir -p features/$feature/{components,hooks,services,types,tests}
  echo "export {};" > features/$feature/index.ts
done

# Create shared subdirectories
mkdir -p shared/components/{ui,layout}
mkdir -p shared/{hooks,utils,types,services}

echo "🔄 Moving auth-related files..."
# Move auth components
if [ -f components/LoginForm.tsx ]; then
  mv components/LoginForm.tsx features/auth/components/
fi
if [ -f components/RegisterForm.tsx ]; then
  mv components/RegisterForm.tsx features/auth/components/
fi
if [ -f components/ProtectedRoute.tsx ]; then
  mv components/ProtectedRoute.tsx features/auth/components/
fi

# Move auth hooks
if [ -f hooks/useAuth.tsx ]; then
  mv hooks/useAuth.tsx features/auth/hooks/
fi
if [ -f hooks/usePermissions.tsx ]; then
  mv hooks/usePermissions.tsx features/auth/hooks/
fi

# Move auth services
if [ -f services/auth.ts ]; then
  mv services/auth.ts features/auth/services/
fi

# Move auth types
if [ -f types/auth.ts ]; then
  mv types/auth.ts features/auth/types/
fi

# Move auth components selector
if [ -f components/auth/ ]; then
  mv components/auth/* features/auth/components/ 2>/dev/null || true
fi

echo "🔄 Moving dashboard-related files..."
# Move dashboard components
if [ -f components/DashboardChart.tsx ]; then
  mv components/DashboardChart.tsx features/dashboard/components/
fi
if [ -f components/EnhancedMCPDashboard.tsx ]; then
  mv components/EnhancedMCPDashboard.tsx features/dashboard/components/
fi
if [ -f components/MCPControlPanel.tsx ]; then
  mv components/MCPControlPanel.tsx features/dashboard/components/
fi

# Move dashboard pages
if [ -f pages/Dashboard.tsx ]; then
  mv pages/Dashboard.tsx features/dashboard/components/
fi
if [ -f pages/EnhancedDashboard.tsx ]; then
  mv pages/EnhancedDashboard.tsx features/dashboard/components/
fi

echo "🔄 Moving agent-related files..."
# Move agent files
if [ -f pages/Agents.tsx ]; then
  mv pages/Agents.tsx features/agents/components/
fi
if [ -f components/modals/CreateAgentModal.tsx ]; then
  mv components/modals/CreateAgentModal.tsx features/agents/components/
fi

echo "🔄 Moving workflow-related files..."
# Move workflow files
if [ -f pages/Workflows.tsx ]; then
  mv pages/Workflows.tsx features/workflows/components/
fi
if [ -f components/modals/CreateWorkflowModal.tsx ]; then
  mv components/modals/CreateWorkflowModal.tsx features/workflows/components/
fi

echo "🔄 Moving model-related files..."
# Move model files  
if [ -f pages/Models.tsx ]; then
  mv pages/Models.tsx features/models/components/
fi

echo "🔄 Moving shared components..."
# Move UI components to shared
if [ -d components/ui ]; then
  cp -r components/ui/* shared/components/ui/ 2>/dev/null || true
  rm -rf components/ui
fi

# Move layout components to shared
if [ -d components/layout ]; then
  cp -r components/layout/* shared/components/layout/ 2>/dev/null || true
  rm -rf components/layout
fi

# Move remaining shared components
for component in ErrorBoundary.tsx; do
  if [ -f components/$component ]; then
    mv components/$component shared/components/
  fi
done

echo "🔄 Moving shared utilities and services..."
# Move shared hooks
if [ -d hooks ]; then
  for hook in useApi.ts useMCP.ts usePerformance.ts; do
    if [ -f hooks/$hook ]; then
      mv hooks/$hook shared/hooks/
    fi
  done
fi

# Move shared services
if [ -d services ]; then
  for service in api.ts apiConfig.ts mcp.ts; do
    if [ -f services/$service ]; then
      mv services/$service shared/services/
    fi
  done
fi

# Move shared utilities
if [ -d utils ]; then
  mv utils/* shared/utils/ 2>/dev/null || true
  rmdir utils 2>/dev/null || true
fi

# Move shared types
if [ -f types/index.ts ]; then
  mv types/index.ts shared/types/
fi

# Move remaining pages to appropriate features or shared
if [ -f pages/Settings.tsx ]; then
  mv pages/Settings.tsx shared/components/
fi
if [ -f pages/Auth.tsx ]; then
  mv pages/Auth.tsx features/auth/components/
fi
if [ -f pages/DemoPage.tsx ]; then
  mv pages/DemoPage.tsx shared/components/
fi

echo "📝 Creating barrel exports..."
# Create feature barrel exports
cat > features/auth/index.ts << 'EOF'
// Auth Feature Exports
export * from './components/LoginForm';
export * from './components/RegisterForm';  
export * from './components/ProtectedRoute';
export * from './hooks/useAuth';
export * from './hooks/usePermissions';
export * from './services/auth';
export * from './types/auth';
EOF

cat > features/dashboard/index.ts << 'EOF'
// Dashboard Feature Exports
export * from './components/Dashboard';
export * from './components/DashboardChart';
export * from './components/EnhancedMCPDashboard';
export * from './components/MCPControlPanel';
EOF

cat > features/agents/index.ts << 'EOF'
// Agents Feature Exports
export * from './components/Agents';
export * from './components/CreateAgentModal';
EOF

cat > features/workflows/index.ts << 'EOF'
// Workflows Feature Exports  
export * from './components/Workflows';
export * from './components/CreateWorkflowModal';
EOF

cat > features/models/index.ts << 'EOF'
// Models Feature Exports
export * from './components/Models';
EOF

# Create shared barrel exports
cat > shared/index.ts << 'EOF'
// Shared Exports
export * from './components';
export * from './hooks';
export * from './services';
export * from './types';
export * from './utils';
EOF

cat > shared/components/index.ts << 'EOF'
// Shared Components
export * from './ui';
export * from './layout';
export * from './ErrorBoundary';
EOF

echo "🔧 Updating import paths in App.tsx..."
# Update imports in App.tsx
if [ -f App.tsx ]; then
  # Create updated App.tsx with new import paths
  cat > App.tsx.new << 'EOF'
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/features/auth';
import { AuthPage } from '@/features/auth/components/Auth';
import { DemoPage } from '@/shared/components/DemoPage';
import { Layout } from '@/shared/components/layout/Layout';
import { Dashboard } from '@/features/dashboard/components/Dashboard';
import { Agents } from '@/features/agents/components/Agents';
import { Workflows } from '@/features/workflows/components/Workflows';
import { Models } from '@/features/models/components/Models';
import { Settings } from '@/shared/components/Settings';
import { ProtectedRoute } from '@/features/auth';
import { Toaster } from '@/shared/components/ui/toaster';

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
EOF
  
  # Replace old App.tsx
  mv App.tsx.new App.tsx
fi

echo "🔧 Updating TypeScript configuration..."
# Update tsconfig.json to add feature paths
cd ../
if [ -f tsconfig.json ]; then
  # Create backup
  cp tsconfig.json tsconfig.json.backup
  
  # Update paths in tsconfig.json
  cat tsconfig.json | jq '.compilerOptions.paths += {
    "@/features/*": ["./src/features/*"],
    "@/shared/*": ["./src/shared/*"]
  }' > tsconfig.json.tmp && mv tsconfig.json.tmp tsconfig.json
fi

echo "✅ Phase 1 migration completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Run 'npm run build' to check for compilation errors"
echo "2. Run 'npm run test' to ensure tests still pass"
echo "3. Update remaining import statements as needed"
echo "4. Review and test the application manually"
echo ""
echo "🔄 Rollback: If issues occur, restore from backup:"
echo "   cd src && rm -rf features shared && cp -r ../src-backup-* ."
echo ""