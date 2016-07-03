/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export function timeout(timeoutMs: number, promise: Promise) {
  return new Promise(function(resolve, reject) {
    console('running with timeout', timeoutMs);
    setTimeout(function() {
      reject(new Error('timeout'));
    }, timeoutMs);
    promise.then(resolve, reject);
  });
}

export async function retryWithBackoff(startTimeoutMs: number, backoffFactor: number, retries: number, getPromise: () => Promise) {
  try {
    console('remaining tries', retries);
    return await timeout(startTimeoutMs, getPromise());
  } catch (e) {
    if (retries > 0) {
      return retryWithBackoff(startTimeoutMs * backoffFactor, backoffFactor, retries - 1, getPromise);
    } else {
      throw e;
    }
  }
}
