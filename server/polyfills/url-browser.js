/**
 * Browser-compatible polyfill for Node.js url module
 * Uses native URL API available in modern browsers
 */

/**
 * Parse a URL string into its components
 * @param {string} urlStr - The URL to parse
 * @param {boolean} parseQueryString - If true, query property will be an object
 * @returns {object} Parsed URL object
 */
export function parse(urlStr, parseQueryString = false) {
  try {
    // Handle relative URLs by using a dummy base
    const isRelative = !urlStr.match(/^[a-z]+:\/\//i);
    const url = isRelative ? new URL(urlStr, 'http://dummy') : new URL(urlStr);

    const result = {
      protocol: isRelative ? null : url.protocol,
      slashes: url.protocol ? url.href.startsWith(url.protocol + '//') : null,
      auth: url.username ? (url.password ? `${url.username}:${url.password}` : url.username) : null,
      host: isRelative ? null : url.host,
      port: url.port || null,
      hostname: isRelative ? null : url.hostname,
      hash: url.hash || null,
      search: url.search || null,
      query: parseQueryString ? parseQuery(url.search) : (url.search ? url.search.slice(1) : null),
      pathname: url.pathname,
      path: url.pathname + (url.search || ''),
      href: isRelative ? urlStr : url.href,
    };

    return result;
  } catch (e) {
    // Return a minimal object for invalid URLs
    return {
      protocol: null,
      slashes: null,
      auth: null,
      host: null,
      port: null,
      hostname: null,
      hash: null,
      search: null,
      query: parseQueryString ? {} : null,
      pathname: urlStr,
      path: urlStr,
      href: urlStr,
    };
  }
}

/**
 * Parse query string into object
 */
function parseQuery(search) {
  if (!search || search === '?') return {};
  const params = new URLSearchParams(search);
  const result = {};
  for (const [key, value] of params) {
    if (result.hasOwnProperty(key)) {
      // Handle multiple values for same key
      if (Array.isArray(result[key])) {
        result[key].push(value);
      } else {
        result[key] = [result[key], value];
      }
    } else {
      result[key] = value;
    }
  }
  return result;
}

/**
 * Format a URL object back into a string
 * @param {object} urlObj - URL object to format
 * @returns {string} Formatted URL string
 */
export function format(urlObj) {
  let url = '';

  if (urlObj.protocol) {
    url += urlObj.protocol;
    if (urlObj.slashes !== false) {
      url += '//';
    }
  }

  if (urlObj.auth) {
    url += urlObj.auth + '@';
  }

  if (urlObj.hostname) {
    url += urlObj.hostname;
  } else if (urlObj.host) {
    url += urlObj.host;
  }

  if (urlObj.port && urlObj.hostname) {
    url += ':' + urlObj.port;
  }

  if (urlObj.pathname) {
    url += urlObj.pathname;
  }

  if (urlObj.search) {
    url += urlObj.search;
  } else if (urlObj.query) {
    if (typeof urlObj.query === 'object') {
      const params = new URLSearchParams();
      for (const [key, value] of Object.entries(urlObj.query)) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v));
        } else if (value !== null && value !== undefined) {
          params.append(key, value);
        }
      }
      const queryStr = params.toString();
      if (queryStr) {
        url += '?' + queryStr;
      }
    } else if (typeof urlObj.query === 'string') {
      url += '?' + urlObj.query;
    }
  }

  if (urlObj.hash) {
    url += urlObj.hash;
  }

  return url;
}

/**
 * Resolve a target URL relative to a base URL
 * @param {string} from - Base URL
 * @param {string} to - Target URL (potentially relative)
 * @returns {string} Resolved absolute URL
 */
export function resolve(from, to) {
  try {
    return new URL(to, from).href;
  } catch (e) {
    return to;
  }
}

// Default export for CommonJS compatibility
export default {
  parse,
  format,
  resolve,
};
