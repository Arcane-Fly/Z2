/**
 * Configuration barrel export
 * Centralized exports for all configuration modules
 */

// Environment configuration (primary export)
export * from './environment';

// Note: api.ts is deprecated and re-exports from environment for backward compatibility
// Don't re-export from it to avoid duplication
