/**
 * Shared Design System Utilities - DRY Principle Implementation
 * 
 * This module provides reusable styling utilities and patterns
 * to eliminate repetition across components.
 */

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility function to merge Tailwind classes safely
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Common transition patterns used across components
 */
export const TRANSITIONS = {
  default: 'transition-all duration-200',
  fast: 'transition-all duration-150',
  slow: 'transition-all duration-300',
  colors: 'transition-colors duration-200',
  transform: 'transition-transform duration-200',
  opacity: 'transition-opacity duration-200',
} as const;

/**
 * Common spacing patterns
 */
export const SPACING = {
  component: {
    sm: 'p-3',
    md: 'p-4', 
    lg: 'p-6',
    xl: 'p-8',
  },
  margin: {
    sm: 'm-2',
    md: 'm-4',
    lg: 'm-6',
    xl: 'm-8',
  },
  gap: {
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
    xl: 'gap-8',
  },
} as const;

/**
 * Common border radius patterns
 */
export const RADIUS = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  full: 'rounded-full',
} as const;

/**
 * Common shadow patterns
 */
export const SHADOWS = {
  none: 'shadow-none',
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: 'shadow-xl',
  inner: 'shadow-inner',
} as const;

/**
 * Focus ring patterns for accessibility
 */
export const FOCUS_RING = {
  default: 'focus:outline-none focus:ring-2 focus:ring-offset-2',
  primary: 'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
  secondary: 'focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2',
  danger: 'focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2',
} as const;

/**
 * Disabled state patterns
 */
export const DISABLED = {
  default: 'disabled:opacity-50 disabled:cursor-not-allowed',
  button: 'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
  input: 'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
} as const;

/**
 * Interactive element base classes
 */
export const INTERACTIVE = {
  button: cn(
    'inline-flex items-center justify-center font-medium',
    RADIUS.md,
    FOCUS_RING.default,
    TRANSITIONS.colors,
    DISABLED.button
  ),
  input: cn(
    'block w-full border-gray-300',
    RADIUS.md,
    FOCUS_RING.primary,
    TRANSITIONS.colors,
    DISABLED.input
  ),
  card: cn(
    'bg-white border border-gray-200',
    RADIUS.lg,
    TRANSITIONS.default,
    SHADOWS.sm
  ),
} as const;

/**
 * Color variant utilities for consistent theming
 */
export const COLOR_VARIANTS = {
  primary: {
    bg: 'bg-blue-600',
    bgHover: 'hover:bg-blue-700',
    text: 'text-blue-600',
    textHover: 'hover:text-blue-700',
    border: 'border-blue-600',
    ring: 'ring-blue-500',
  },
  secondary: {
    bg: 'bg-gray-100',
    bgHover: 'hover:bg-gray-200',
    text: 'text-gray-600',
    textHover: 'hover:text-gray-700',
    border: 'border-gray-300',
    ring: 'ring-gray-500',
  },
  success: {
    bg: 'bg-green-600',
    bgHover: 'hover:bg-green-700',
    text: 'text-green-600',
    textHover: 'hover:text-green-700',
    border: 'border-green-600',
    ring: 'ring-green-500',
  },
  warning: {
    bg: 'bg-yellow-600',
    bgHover: 'hover:bg-yellow-700',
    text: 'text-yellow-600',
    textHover: 'hover:text-yellow-700',
    border: 'border-yellow-600',
    ring: 'ring-yellow-500',
  },
  danger: {
    bg: 'bg-red-600',
    bgHover: 'hover:bg-red-700',
    text: 'text-red-600',
    textHover: 'hover:text-red-700',
    border: 'border-red-600',
    ring: 'ring-red-500',
  },
} as const;

/**
 * Size variant utilities
 */
export const SIZE_VARIANTS = {
  xs: { text: 'text-xs', padding: 'px-2 py-1' },
  sm: { text: 'text-sm', padding: 'px-3 py-1.5' },
  md: { text: 'text-sm', padding: 'px-4 py-2' },
  lg: { text: 'text-base', padding: 'px-6 py-3' },
  xl: { text: 'text-lg', padding: 'px-8 py-4' },
} as const;

/**
 * Common layout patterns
 */
export const LAYOUT = {
  flexCenter: 'flex items-center justify-center',
  flexBetween: 'flex items-center justify-between',
  flexCol: 'flex flex-col',
  flexColCenter: 'flex flex-col items-center justify-center',
  grid2: 'grid grid-cols-2',
  grid3: 'grid grid-cols-3',
  grid4: 'grid grid-cols-4',
  gridResponsive: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
} as const;

/**
 * Animation utilities for consistent motion
 */
export const ANIMATIONS = {
  fadeIn: 'animate-in fade-in duration-200',
  slideIn: 'animate-in slide-in-from-bottom-4 duration-300',
  scaleIn: 'animate-in zoom-in-95 duration-200',
  pulse: 'animate-pulse',
  spin: 'animate-spin',
  bounce: 'animate-bounce',
} as const;

/**
 * Typography utilities for consistent text styling
 */
export const TYPOGRAPHY = {
  heading: {
    h1: 'text-3xl font-bold tracking-tight',
    h2: 'text-2xl font-semibold tracking-tight',
    h3: 'text-xl font-semibold',
    h4: 'text-lg font-medium',
    h5: 'text-base font-medium',
    h6: 'text-sm font-medium',
  },
  body: {
    lg: 'text-lg',
    md: 'text-base',
    sm: 'text-sm',
    xs: 'text-xs',
  },
  weight: {
    light: 'font-light',
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold',
  },
} as const;

export type TransitionKey = keyof typeof TRANSITIONS;
export type ColorVariant = keyof typeof COLOR_VARIANTS;
export type SizeVariant = keyof typeof SIZE_VARIANTS;
export type LayoutPattern = keyof typeof LAYOUT;