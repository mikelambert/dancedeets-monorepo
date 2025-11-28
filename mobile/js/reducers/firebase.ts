/**
 * Copyright 2016 DanceDeets.
 */

import type { Action } from '../actions/types';

export type State = { [key: string]: any };

const initialState: State = {};

export function firebase(state: State = initialState, action: Action): State {
  if (action.type === 'FIREBASE_UPDATE') {
    return { ...state, [action.key]: action.value };
  }
  return state;
}
