/**
 * Copyright 2016 DanceDeets.
 */

import url from 'url';

export function addUrlArgs(
  origUrl: string,
  args: Record<string, string | number | boolean | null | undefined> | null | undefined
): string {
  const parsedUrl = url.parse(origUrl, true);
  // Convert args to string values for URL query compatibility
  const stringArgs: Record<string, string> = {};
  if (args) {
    Object.entries(args).forEach(([key, value]) => {
      if (value != null) {
        stringArgs[key] = String(value);
      }
    });
  }
  parsedUrl.query = { ...parsedUrl.query, ...stringArgs };
  // Clear search so format uses query
  parsedUrl.search = null;
  const newUrl = url.format(parsedUrl);
  return newUrl;
}

export function getHostname(origUrl: string): string | null {
  return url.parse(origUrl).hostname;
}

export const cdnBaseUrl = 'https://static.dancedeets.com';
