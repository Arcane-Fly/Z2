/**
 * Accessibility Enhancement Utilities
 * 
 * Provides utilities and hooks for improving accessibility compliance
 * and user experience for users with disabilities
 */

import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Screen reader announcement hook
 */
export function useAnnouncement(): (message: string, priority?: 'polite' | 'assertive') => void {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.setAttribute('class', 'sr-only');
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }, []);

  return announce;
}

/**
 * Keyboard navigation hook
 */
export function useKeyboardNavigation(
  keys: string[],
  handler: (key: string, event: KeyboardEvent) => void,
  dependencies: any[] = []
): void {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (keys.includes(event.key)) {
        handler(event.key, event);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [keys, handler, ...dependencies]);
}

/**
 * Focus management hook
 */
export function useFocusManagement() {
  const focusHistory = useRef<HTMLElement[]>([]);

  const saveFocus = useCallback(() => {
    const activeElement = document.activeElement as HTMLElement;
    if (activeElement && activeElement !== document.body) {
      focusHistory.current.push(activeElement);
    }
  }, []);

  const restoreFocus = useCallback(() => {
    const lastFocused = focusHistory.current.pop();
    if (lastFocused && lastFocused.focus) {
      lastFocused.focus();
    }
  }, []);

  const setFocus = useCallback((element: HTMLElement | null) => {
    if (element && element.focus) {
      element.focus();
    }
  }, []);

  return { saveFocus, restoreFocus, setFocus };
}

/**
 * ARIA attributes helper
 */
export interface AriaProps {
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-selected'?: boolean;
  'aria-checked'?: boolean | 'mixed';
  'aria-disabled'?: boolean;
  'aria-hidden'?: boolean;
  'aria-live'?: 'polite' | 'assertive' | 'off';
  'aria-atomic'?: boolean;
  'aria-busy'?: boolean;
  'aria-controls'?: string;
  'aria-owns'?: string;
  'aria-haspopup'?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog';
  role?: string;
}

export function useAriaAttributes(defaultProps: AriaProps = {}): AriaProps {
  return defaultProps;
}

/**
 * Skip link component for keyboard navigation
 */
export const SkipLink: React.FC<{ href: string; children: React.ReactNode }> = ({
  href,
  children
}) => (
  <a
    href={href}
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-md z-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    onFocus={() => {
      // Ensure skip link is visible when focused
    }}
  >
    {children}
  </a>
);

/**
 * Color contrast utilities
 */
export const colorContrast = {
  // WCAG AA compliant contrast ratios
  isAccessible: (_foreground: string, _background: string): boolean => {
    // This would need a proper color contrast calculation library
    // For now, return true as a placeholder
    return true;
  },
  
  // Get accessible text color for background
  getTextColor: (backgroundColor: string): 'white' | 'black' => {
    // Simple heuristic - would need proper luminance calculation
    return backgroundColor.includes('dark') || backgroundColor.includes('black') ? 'white' : 'black';
  }
};

/**
 * Focus visible utility for custom focus indicators
 */
export function useFocusVisible(): {
  focusVisible: boolean;
  onFocus: () => void;
  onBlur: () => void;
  onKeyDown: (event: KeyboardEvent) => void;
  onMouseDown: () => void;
} {
  const [focusVisible, setFocusVisible] = useState(false);
  const hadKeyboardEvent = useRef(false);

  const onKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.metaKey || event.altKey || event.ctrlKey) {
      return;
    }
    hadKeyboardEvent.current = true;
  }, []);

  const onMouseDown = useCallback(() => {
    hadKeyboardEvent.current = false;
  }, []);

  const onFocus = useCallback(() => {
    setFocusVisible(hadKeyboardEvent.current);
  }, []);

  const onBlur = useCallback(() => {
    setFocusVisible(false);
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', onKeyDown, true);
    document.addEventListener('mousedown', onMouseDown, true);

    return () => {
      document.removeEventListener('keydown', onKeyDown, true);
      document.removeEventListener('mousedown', onMouseDown, true);
    };
  }, [onKeyDown, onMouseDown]);

  return {
    focusVisible,
    onFocus,
    onBlur,
    onKeyDown,
    onMouseDown
  };
}

/**
 * Landmark navigation hook
 */
export function useLandmarkNavigation() {
  const landmarks = useRef<Map<string, HTMLElement>>(new Map());

  const registerLandmark = useCallback((id: string, element: HTMLElement) => {
    landmarks.current.set(id, element);
  }, []);

  const unregisterLandmark = useCallback((id: string) => {
    landmarks.current.delete(id);
  }, []);

  const navigateToLandmark = useCallback((id: string) => {
    const element = landmarks.current.get(id);
    if (element) {
      element.focus();
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, []);

  return {
    registerLandmark,
    unregisterLandmark,
    navigateToLandmark
  };
}

/**
 * High contrast mode detection
 */
export function useHighContrast(): boolean {
  const [highContrast, setHighContrast] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-contrast: high)').matches;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    const handler = (event: MediaQueryListEvent) => {
      setHighContrast(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return highContrast;
}

/**
 * Screen reader detection
 */
export function useScreenReader(): boolean {
  const [hasScreenReader, setHasScreenReader] = useState(false);

  useEffect(() => {
    // Check for common screen reader indicators
    const userAgent = navigator.userAgent.toLowerCase();
    const hasScreenReaderUA = 
      userAgent.includes('jaws') || 
      userAgent.includes('nvda') || 
      userAgent.includes('voiceover') ||
      userAgent.includes('talkback');

    // Check for reduced motion preference as an indicator
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    setHasScreenReader(hasScreenReaderUA || prefersReducedMotion);
  }, []);

  return hasScreenReader;
}

/**
 * Live region for dynamic content announcements
 */
export const LiveRegion: React.FC<{
  message: string;
  level?: 'polite' | 'assertive';
  className?: string;
}> = ({ message, level = 'polite', className = 'sr-only' }) => (
  <div
    aria-live={level}
    aria-atomic="true"
    className={className}
  >
    {message}
  </div>
);

/**
 * Progress announcement hook for screen readers
 */
export function useProgressAnnouncement(
  progress: number,
  total: number,
  intervalMs: number = 5000
): void {
  const announce = useAnnouncement();
  const lastAnnouncedRef = useRef(0);

  useEffect(() => {
    const percentage = Math.round((progress / total) * 100);
    const now = Date.now();

    if (
      percentage !== lastAnnouncedRef.current && 
      now - lastAnnouncedRef.current > intervalMs
    ) {
      announce(`Progress: ${percentage}% complete`);
      lastAnnouncedRef.current = now;
    }
  }, [progress, total, intervalMs, announce]);
}

/**
 * Accessible form utilities
 */
export const formA11y = {
  getErrorId: (fieldName: string) => `${fieldName}-error`,
  getHelpId: (fieldName: string) => `${fieldName}-help`,
  getDescribedBy: (fieldName: string, hasError: boolean, hasHelp: boolean) => {
    const ids = [];
    if (hasError) ids.push(formA11y.getErrorId(fieldName));
    if (hasHelp) ids.push(formA11y.getHelpId(fieldName));
    return ids.length > 0 ? ids.join(' ') : undefined;
  }
};

export default {
  useAnnouncement,
  useKeyboardNavigation,
  useFocusManagement,
  useAriaAttributes,
  SkipLink,
  colorContrast,
  useFocusVisible,
  useLandmarkNavigation,
  useHighContrast,
  useScreenReader,
  LiveRegion,
  useProgressAnnouncement,
  formA11y
};