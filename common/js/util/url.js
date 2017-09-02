/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import url from 'url';

export function addUrlArgs(origUrl: string, args: Object) {
  const parsedUrl = url.parse(origUrl, true);
  parsedUrl.query = { ...parsedUrl.query, ...args };
  const newUrl = url.format(parsedUrl);
  return newUrl;
}

export function getHostname(origUrl: string) {
  return url.parse(origUrl).hostname;
}

export const cdnBaseUrl = 'https://static.dancedeets.com';
