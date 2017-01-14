/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

export function timeout<T>(timeoutMs: number, promise: Promise<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      reject(new Error(`${timeoutMs}ms timeout reached`));
    }, timeoutMs);
    promise.then(resolve, reject);
  });
}

export async function retryWithBackoff<T>(startTimeoutMs: number, backoffFactor: number, retries: number, getPromise: () => Promise<T>): Promise<T> {
  try {
    return await timeout(startTimeoutMs, getPromise());
  } catch (e) {
    console.log(`Error on request, ${retries} retries remaining: ${e}`);
    if (retries > 0) {
      return retryWithBackoff(startTimeoutMs * backoffFactor, backoffFactor, retries - 1, getPromise);
    }
    throw e;
  }
}
