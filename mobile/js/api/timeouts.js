/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export function timeout<T>(timeoutMs: number, promise: Promise<T>): Promise<T> {
  return new Promise(function(resolve, reject) {
    setTimeout(function() {
      reject(new Error(`${timeoutMs}ms timeout reached`));
    }, timeoutMs);
    promise.then(resolve, reject);
  });
}

export async function retryWithBackoff<T>(startTimeoutMs: number, backoffFactor: number, retries: number, getPromise: () => Promise<T>): Promise<T> {
  try {
    return await timeout(startTimeoutMs, getPromise());
  } catch (e) {
    if (retries > 0) {
      return retryWithBackoff(startTimeoutMs * backoffFactor, backoffFactor, retries - 1, getPromise);
    } else {
      throw e;
    }
  }
}
