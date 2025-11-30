/**
 * Unit tests for util/url.ts
 */

import { addUrlArgs, getHostname, cdnBaseUrl } from '../../util/url';

describe('addUrlArgs', () => {
  it('should add query args to URL without existing query', () => {
    const result = addUrlArgs('https://example.com/path', { foo: 'bar' });
    expect(result).toContain('foo=bar');
    expect(result).toContain('https://example.com/path');
  });

  it('should add query args to URL with existing query', () => {
    const result = addUrlArgs('https://example.com/path?existing=value', { foo: 'bar' });
    expect(result).toContain('existing=value');
    expect(result).toContain('foo=bar');
  });

  it('should handle null args', () => {
    const result = addUrlArgs('https://example.com/path', null);
    expect(result).toBe('https://example.com/path');
  });

  it('should handle undefined args', () => {
    const result = addUrlArgs('https://example.com/path', undefined);
    expect(result).toBe('https://example.com/path');
  });

  it('should convert number values to strings', () => {
    const result = addUrlArgs('https://example.com/', { count: 42 });
    expect(result).toContain('count=42');
  });

  it('should convert boolean values to strings', () => {
    const result = addUrlArgs('https://example.com/', { enabled: true, disabled: false });
    expect(result).toContain('enabled=true');
    expect(result).toContain('disabled=false');
  });

  it('should skip null values in args', () => {
    const result = addUrlArgs('https://example.com/', { valid: 'yes', invalid: null });
    expect(result).toContain('valid=yes');
    expect(result).not.toContain('invalid');
  });

  it('should skip undefined values in args', () => {
    const result = addUrlArgs('https://example.com/', { valid: 'yes', invalid: undefined });
    expect(result).toContain('valid=yes');
    expect(result).not.toContain('invalid');
  });

  it('should handle multiple args', () => {
    const result = addUrlArgs('https://example.com/', {
      a: '1',
      b: '2',
      c: '3',
    });
    expect(result).toContain('a=1');
    expect(result).toContain('b=2');
    expect(result).toContain('c=3');
  });

  it('should handle empty args object', () => {
    const result = addUrlArgs('https://example.com/path', {});
    expect(result).toBe('https://example.com/path');
  });

  it('should handle URLs with fragments', () => {
    const result = addUrlArgs('https://example.com/path#section', { foo: 'bar' });
    expect(result).toContain('foo=bar');
    // URL parsing behavior may vary with fragments
  });

  it('should encode special characters in values', () => {
    const result = addUrlArgs('https://example.com/', { search: 'hello world' });
    expect(result).toContain('search=hello%20world');
  });
});

describe('getHostname', () => {
  it('should extract hostname from full URL', () => {
    expect(getHostname('https://www.example.com/path')).toBe('www.example.com');
  });

  it('should extract hostname without www', () => {
    expect(getHostname('https://example.com/path')).toBe('example.com');
  });

  it('should handle URLs with port', () => {
    expect(getHostname('https://example.com:8080/path')).toBe('example.com');
  });

  it('should handle HTTP URLs', () => {
    expect(getHostname('http://example.com/path')).toBe('example.com');
  });

  it('should return null for invalid URLs', () => {
    expect(getHostname('not-a-url')).toBeNull();
  });

  it('should handle URLs with query strings', () => {
    expect(getHostname('https://example.com/path?query=value')).toBe('example.com');
  });

  it('should handle subdomains', () => {
    expect(getHostname('https://sub.domain.example.com/path')).toBe('sub.domain.example.com');
  });
});

describe('cdnBaseUrl', () => {
  it('should be the correct CDN URL', () => {
    expect(cdnBaseUrl).toBe('https://static.dancedeets.com');
  });

  it('should be a valid URL', () => {
    expect(() => new URL(cdnBaseUrl)).not.toThrow();
  });
});
