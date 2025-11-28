/**
 * Copyright 2016 DanceDeets.
 */

import type { Action } from './types';

export const FIREBASE_UPDATE = 'FIREBASE_UPDATE';

export function setFirebaseState(key: string, value: unknown): Action {
  return {
    type: FIREBASE_UPDATE,
    key,
    value,
  };
}
