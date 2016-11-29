/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

export type State = {[key: string]: any};

const initialState = {};

export function firebase(state: State = initialState, action: Action): State {
  if (action.type === 'FIREBASE_UPDATE') {
    return {...state, [action.key]: action.value};
  }
  return state;
}
