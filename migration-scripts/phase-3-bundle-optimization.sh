#!/bin/bash
set -euo pipefail

# Phase 3: Bundle Optimization and Performance Improvements
# This script implements code splitting, lazy loading, and build optimizations

echo "🚀 Phase 3: Bundle Optimization and Performance Improvements"
echo "============================================================"

cd frontend

echo "📦 Creating backup..."
cp -r . ../frontend-backup-phase3-$(date +%Y%m%d-%H%M%S)

echo "📦 Installing performance optimization dependencies..."
yarn add @loadable/component
yarn add --dev webpack-bundle-analyzer vite-bundle-analyzer

echo "🔧 Implementing lazy loading for routes..."

# Create lazy-loaded route components
cat > src/routes/LazyRoutes.tsx << 'EOF'
/**
 * Lazy-loaded route components for code splitting
 */
import { lazy } from 'react';

// Lazy load feature pages
export const LazyDashboard = lazy(() => 
  import('@/features/dashboard/components/Dashboard').then(module => ({
    default: module.Dashboard
  }))
);

export const LazyAgents = lazy(() => 
  import('@/features/agents/components/Agents').then(module => ({
    default: module.Agents  
  }))
);

export const LazyWorkflows = lazy(() => 
  import('@/features/workflows/components/Workflows').then(module => ({
    default: module.Workflows
  }))
);

export const LazyModels = lazy(() => 
  import('@/features/models/components/Models').then(module => ({
    default: module.Models
  }))
);

export const LazySettings = lazy(() => 
  import('@/shared/components/Settings').then(module => ({
    default: module.Settings
  }))
);

export const LazyAuth = lazy(() => 
  import('@/features/auth/components/Auth').then(module => ({
    default: module.AuthPage
  }))
);

export const LazyDemo = lazy(() => 
  import('@/shared/components/DemoPage').then(module => ({
    default: module.DemoPage
  }))
);
EOF

# Update App.tsx to use lazy loading with Suspense
cat > src/App.tsx << 'EOF'
import { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/features/auth';
import { Layout } from '@/shared/components/layout/Layout';
import { ProtectedRoute } from '@/features/auth';
import { Toaster } from '@/shared/components/ui/toaster';
import { LoadingSpinner } from '@/shared/components/ui/LoadingSpinner';

// Lazy-loaded components
import {
  LazyDashboard,
  LazyAgents,
  LazyWorkflows,
  LazyModels,
  LazySettings,
  LazyAuth,
  LazyDemo
} from './routes/LazyRoutes';

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <LoadingSpinner size="lg" />
  </div>
);

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-background">
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public routes */}
            <Route path="/auth" element={<LazyAuth />} />
            <Route path="/demo" element={<LazyDemo />} />
            
            {/* Protected routes with layout */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <LazyDashboard />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/agents" 
              element={
                <ProtectedRoute requiredRole="operator">
                  <Layout>
                    <LazyAgents />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/workflows" 
              element={
                <ProtectedRoute requiredRole="operator">
                  <Layout>
                    <LazyWorkflows />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/models" 
              element={
                <ProtectedRoute requiredRole="developer">
                  <Layout>
                    <LazyModels />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute requiredRole="manager">
                  <Layout>
                    <LazySettings />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
        <Toaster />
      </div>
    </AuthProvider>
  );
}

export default App;
EOF

echo "⚡ Optimizing Vite configuration..."

# Update vite.config.ts with advanced optimizations
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    }
  },
  server: {
    host: '0.0.0.0',
    port: Number(process.env.PORT) || 5173,
  },
  preview: {
    host: '0.0.0.0',
    port: Number(process.env.PORT) || 4173,
    allowedHosts: [
      'healthcheck.railway.app',
      'z2-production.up.railway.app'
    ],
  },
  build: {
    outDir: 'dist',
    cssCodeSplit: true, // Enable CSS code splitting
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom'],
          'router': ['react-router-dom'],
          'ui-vendor': ['@heroicons/react', 'clsx', 'tailwind-merge'],
          'query': ['@tanstack/react-query'],
          'charts': ['chart.js', 'react-chartjs-2'],
          
          // Feature chunks
          'auth-feature': [
            './src/features/auth/components/LoginForm',
            './src/features/auth/components/RegisterForm',
            './src/features/auth/hooks/useAuth',
            './src/features/auth/services/auth'
          ],
          'dashboard-feature': [
            './src/features/dashboard/components/Dashboard',
            './src/features/dashboard/components/DashboardChart'
          ]
        },
        // Asset naming for better caching
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop().replace('.tsx', '').replace('.ts', '') : 'chunk';
          return `js/${facadeModuleId}-[hash].js`;
        },
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `images/[name]-[hash][extname]`;
          } else if (/css/i.test(ext)) {
            return `css/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
      },
    },
    // Chunk size warning threshold
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@tanstack/react-query'
    ],
  },
})
EOF

echo "📊 Adding bundle analysis scripts..."

# Update package.json to add bundle analysis scripts
if command -v jq &> /dev/null; then
  # Update package.json using jq
  jq '.scripts += {
    "analyze": "vite-bundle-analyzer dist/stats.html",
    "build:analyze": "vite build --mode production && vite-bundle-analyzer",
    "build:stats": "vite build --mode production --emptyOutDir --sourcemap",
    "preload-routes": "echo \"Preloading critical routes for better performance\""
  }' package.json > package.json.tmp && mv package.json.tmp package.json
else
  echo "⚠️  jq not available - please manually add bundle analysis scripts to package.json"
fi

echo "🔧 Optimizing component exports for tree-shaking..."

# Update shared UI components index to use more specific exports
cat > src/shared/components/ui/index.ts << 'EOF'
// UI Components - Tree-shaking optimized exports
// Import only what you need to reduce bundle size

// Button components
export { Button } from './Button';
export type { ButtonProps } from './Button/Button';

// Modal components  
export { Modal } from './Modal';
export type { ModalProps } from './Modal/Modal';

// Form components
export { Input, Textarea, Select } from './Form';
export type { InputProps, TextareaProps, SelectProps } from './Form/Form';

// Table components
export { Table } from './Table';  
export type { TableProps } from './Table/Table';

// Badge components
export { Badge } from './Badge';
export type { BadgeProps } from './Badge/Badge';

// Card components - Split for better tree-shaking
export { Card } from './Card';
export { MetricCard } from './Card/MetricCard';
export { ActivityItem } from './Card/ActivityItem'; 
export { StatsGrid } from './Card/StatsGrid';

// Loading components - Split for better tree-shaking
export { LoadingSpinner } from './LoadingSpinner';
export { Skeleton } from './LoadingSpinner/Skeleton';
export { ProgressBar } from './LoadingSpinner/ProgressBar';
export { PulseIndicator } from './LoadingSpinner/PulseIndicator';

// Toast components
export { Toaster } from './toaster';
EOF

echo "🚀 Adding performance monitoring..."

# Create performance monitoring utility
cat > src/shared/utils/performance.ts << 'EOF'
/**
 * Performance monitoring utilities
 */

// Web Vitals measurement
export const measureWebVitals = () => {
  if (typeof window !== 'undefined' && 'performance' in window) {
    // Measure First Contentful Paint
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.log(`Performance metric: ${entry.name} = ${entry.startTime}ms`);
      }
    });
    
    observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
    
    // Measure bundle size impact
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      console.log(`Network: ${connection.effectiveType}, Downlink: ${connection.downlink}Mbps`);
    }
  }
};

// Chunk loading performance
export const trackChunkLoading = (chunkName: string) => {
  const start = performance.now();
  return () => {
    const end = performance.now();
    console.log(`Chunk '${chunkName}' loaded in ${end - start}ms`);
  };
};

// Component render performance
export const measureComponentRender = (componentName: string) => {
  const start = performance.now();
  return () => {
    const end = performance.now();
    if (end - start > 16) { // Longer than 1 frame at 60fps
      console.warn(`Component '${componentName}' took ${end - start}ms to render`);
    }
  };
};
EOF

# Add performance measurement to main.tsx
cat > src/main.tsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.tsx'
import './index.css'
import { measureWebVitals } from '@/shared/utils/performance'

// Create QueryClient with optimized settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: (failureCount, error: any) => {
        if (error?.status === 404) return false;
        return failureCount < 3;
      },
    },
  },
});

// Start performance monitoring
measureWebVitals();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
EOF

echo "📝 Adding sideEffects configuration..."

# Update package.json to mark as side-effect free for better tree-shaking
if command -v jq &> /dev/null; then
  jq '. + {"sideEffects": ["**/*.css", "**/*.scss", "./src/index.css"]}' package.json > package.json.tmp && mv package.json.tmp package.json
fi

echo "🔧 Creating preload hints for critical resources..."

# Update index.html with resource hints
cat > index.html << 'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    
    <!-- Preload critical resources -->
    <link rel="preload" href="/src/main.tsx" as="script" crossorigin>
    <link rel="preload" href="/src/index.css" as="style">
    
    <!-- DNS prefetch for external resources -->
    <link rel="dns-prefetch" href="//fonts.googleapis.com">
    
    <!-- Preconnect to critical domains -->
    <link rel="preconnect" href="https://api.z2.ai" crossorigin>
    
    <title>Z2 AI Workforce Platform</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

echo "✅ Phase 3 migration completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Run 'yarn build' to create optimized production build"
echo "2. Run 'yarn analyze' to analyze bundle size improvements"  
echo "3. Test lazy loading by navigating between routes"
echo "4. Monitor performance metrics in browser dev tools"
echo "5. Run 'yarn preview' to test production build locally"
echo ""
echo "📊 Performance Analysis:"
echo "- Run 'yarn build:analyze' to see detailed bundle analysis"
echo "- Check Network tab for chunk loading behavior"
echo "- Verify tree-shaking worked by examining chunk contents"
echo ""
echo "🔄 Rollback: If issues occur, restore from backup:"
echo "   cd .. && rm -rf frontend && cp -r frontend-backup-phase3-* frontend"
echo ""