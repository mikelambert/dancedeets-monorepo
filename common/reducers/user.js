/**
 * Copyright DanceDeets.
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

export type State = {
  isLoggedIn: boolean;
  hasSkippedLogin: boolean;
  id: ?string;
  name: ?string;
};

const initialState = {
  isLoggedIn: false,
  hasSkippedLogin: false,
  id: null,
  name: null,
};

export function user(state: State = initialState, action: Action): State {
  if (action.type === 'LOGGED_IN') {
    let {id, name} = action.data;
    return {
      isLoggedIn: true,
      hasSkippedLogin: false,
      id,
      name,
    };
  }
  if (action.type === 'SKIPPED_LOGIN') {
    return {
      isLoggedIn: false,
      hasSkippedLogin: true,
      id: null,
      name: null,
    };
  }
  if (action.type === 'LOGGED_OUT') {
    return initialState;
  }
  return state;
}
