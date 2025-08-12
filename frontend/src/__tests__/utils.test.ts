import { describe, expect, it, vi, afterEach } from 'vitest';
import {
  formatRelativeTime,
  groupBy,
  getErrorMessage,
  getStorageItem,
  setStorageItem,
} from '../utils';

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
});
