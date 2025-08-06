import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Add path alias so that imports using "@" resolve to the src directory. Without this,
  // Rollup and Vite cannot resolve aliases defined only in tsconfig.json, causing build errors.
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: Number(process.env.PORT) || 4173,
  },
  preview: {
    host: '0.0.0.0',
    port: Number(process.env.PORT) || 4173,
    // allow Railway’s healthcheck host
    allowedHosts: [
      'healthcheck.railway.app'
    ],
  },
})
