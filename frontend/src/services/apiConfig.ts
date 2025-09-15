/**
 * API Configuration - Unified with Environment Config
 * 
 * @deprecated Use ENV_CONFIG from '../config/environment' instead
 * This file maintained for backward compatibility during migration
 */

import { API_CONFIG as NEW_API_CONFIG, APP_CONFIG as NEW_APP_CONFIG } from '../config/environment';

// Legacy exports for backward compatibility
export const API_CONFIG = NEW_API_CONFIG;
export const APP_CONFIG = NEW_APP_CONFIG;