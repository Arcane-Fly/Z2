/**
 * API Configuration - Migrated to Unified Environment Config
 * 
 * @deprecated Use ENV_CONFIG from './environment' instead
 * This file maintained for backward compatibility during migration
 */

import { ENV_CONFIG } from './environment';

// Re-export unified configuration
export const API_CONFIG = ENV_CONFIG.api;

export default API_CONFIG;
