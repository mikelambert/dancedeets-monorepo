/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import type { Action } from './types';

export const FIREBASE_UPDATE = 'FIREBASE_UPDATE';

export function setFirebaseState(key: string, value: any): Action {
  return {
    type: FIREBASE_UPDATE,
    key,
    value,
  };
}
