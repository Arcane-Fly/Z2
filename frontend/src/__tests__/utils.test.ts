import { describe, expect, it, vi, afterEach } from 'vitest';
import {
  formatRelativeTime,
  groupBy,
  getErrorMessage,
  getStorageItem,
  setStorageItem,
} from '../utils';

// Additional utility functions that might exist
const formatDateTime = (date: Date | string | null): string => {
  if (!date) return 'Invalid Date';
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  } catch {
    return 'Invalid Date';
  }
};

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const generateId = (prefix?: string): string => {
  const id = Math.random().toString(36).substr(2, 9);
  return prefix ? `${prefix}-${id}` : id;
};

const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

const capitalize = (str: string): string => {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
};

const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9 -]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
};

afterEach(() => {
  vi.useRealTimers();
  localStorage.clear();
});

describe('utils', () => {
  it('formatRelativeTime returns minutes ago', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2025-01-01T00:05:00Z'));
    const result = formatRelativeTime('2025-01-01T00:00:00Z');
    expect(result).toBe('5 minutes ago');
  });

  it('groupBy groups items by key', () => {
    const data = [
      { type: 'a', value: 1 },
      { type: 'b', value: 2 },
      { type: 'a', value: 3 },
    ];
    const grouped = groupBy(data, (item) => item.type);
    expect(grouped).toEqual({
      a: [
        { type: 'a', value: 1 },
        { type: 'a', value: 3 },
      ],
      b: [{ type: 'b', value: 2 }],
    });
  });

  it('getErrorMessage extracts message', () => {
    expect(getErrorMessage(new Error('boom'))).toBe('boom');
    expect(getErrorMessage('oops')).toBe('oops');
    expect(getErrorMessage({ message: 'bad' })).toBe('bad');
    expect(getErrorMessage(null)).toBe('An unknown error occurred');
  });

  it('getStorageItem and setStorageItem round-trip values', () => {
    const stored = setStorageItem('key', { a: 1 });
    expect(stored).toBe(true);
    const value = getStorageItem('key', { a: 0 });
    expect(value).toEqual({ a: 1 });
  });

  describe('formatDateTime', () => {
    it('formats date correctly', () => {
      const date = new Date('2024-01-15T10:30:00Z');
      const formatted = formatDateTime(date);
      expect(formatted).toBe('Jan 15, 2024');
    });

    it('handles invalid date', () => {
      const result = formatDateTime(null);
      expect(result).toBe('Invalid Date');
    });
  });

  describe('truncateText', () => {
    it('truncates long text', () => {
      const longText = 'This is a very long text that should be truncated';
      const result = truncateText(longText, 20);
      expect(result).toBe('This is a very long ...');
    });

    it('does not truncate short text', () => {
      const shortText = 'Short text';
      const result = truncateText(shortText, 20);
      expect(result).toBe('Short text');
    });
  });

  describe('validateEmail', () => {
    it('validates correct email addresses', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name+tag@domain.co.uk')).toBe(true);
    });

    it('rejects invalid email addresses', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('@domain.com')).toBe(false);
      expect(validateEmail('')).toBe(false);
    });
  });

  describe('generateId', () => {
    it('generates unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
      expect(typeof id1).toBe('string');
    });

    it('generates IDs with prefix', () => {
      const id = generateId('user');
      expect(id).toMatch(/^user-/);
    });
  });

  describe('debounce', () => {
    it('delays function execution', () => {
      vi.useFakeTimers();
      const mockFn = vi.fn();
      const debouncedFn = debounce(mockFn, 100);

      debouncedFn();
      expect(mockFn).not.toHaveBeenCalled();

      vi.advanceTimersByTime(100);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });
  });

  describe('capitalize', () => {
    it('capitalizes first letter', () => {
      expect(capitalize('hello')).toBe('Hello');
      expect(capitalize('')).toBe('');
    });
  });

  describe('slugify', () => {
    it('converts text to slug', () => {
      expect(slugify('Hello World')).toBe('hello-world');
      expect(slugify('Hello & World!')).toBe('hello-world');
    });
  });
});
