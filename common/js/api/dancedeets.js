/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import querystring from 'querystring';
import fetch from 'node-fetch';
import { timeout, retryWithBackoff } from './timeouts';

const DEV_SERVER = false;

function getUrl(version: string, path: string, args: Object) {
  let schemeHost = null;
  if (global.window.navigator.product === 'ReactNative') {
    schemeHost = DEV_SERVER
      ? 'http://dev.dancedeets.com:8080'
      : 'https://www.dancedeets.com';
  } else {
    schemeHost = window.location.origin;
  }
  let fullPath = `${schemeHost}/api/v${version}/${path}`;
  const formattedArgs = querystring.stringify(args);
  if (formattedArgs) {
    fullPath += `?${formattedArgs}`;
  }
  return fullPath;
}

export async function performRequest(
  path: string,
  args: Object,
  postArgs: ?Object | null,
  version: string
): Promise<Object> {
  try {
    const url = getUrl(version, path, args);
    console.log('JSON API:', url);
    const result = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postArgs),
    });
    // This setTimeout kicks the eventloop so it doesn't fall asleep.
    // Workaround for https://github.com/facebook/react-native/issues/14391
    setTimeout(() => null, 0);
    const json = await result.json();
    // 'undefined' means success, 'false' means error
    if (json.success === false) {
      throw new Error(`${json.errors}`);
    } else {
      return json;
    }
  } catch (e) {
    console.warn(
      'Error on API call:',
      path,
      'withArgs:',
      args,
      '. Error:',
      e.message,
      e
    );
    throw e;
  }
}

export function createRequest(
  path: string,
  args: Object,
  postArgs: ?Object | null
): () => Promise<Object> {
  return () => performRequest(path, args, postArgs);
}

export function idempotentRetry(
  timeoutMs: number,
  promiseGenerator: () => Promise<() => Promise<Object>>
) {
  return retryWithBackoff(timeoutMs, 2, 5, promiseGenerator);
}
