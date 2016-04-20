/**
 * Copyright DanceDeets.
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

export type State = {
  isLoggedIn: boolean;
  hasSkippedLogin: boolean;
  inTutorial: boolean;
  id: ?string;
  name: ?string;
};

const initialState = {
  isLoggedIn: false,
  hasSkippedLogin: false,
  inTutorial: false,
  //TODO: do we want/need these?
  id: null,
  name: null,
};

export function user(state: State = initialState, action: Action): State {
  if (action.type === 'LOGIN_LOADING') {
    return initialState;
  }
  if (action.type === 'LOGIN_START_TUTORIAL') {
    return {
      isLoggedIn: false,
      hasSkippedLogin: false,
      inTutorial: true,
      id: null,
      name: null,
    };
  }
  if (action.type === 'LOGIN_LOGGED_IN') {
    return {
      isLoggedIn: true,
      hasSkippedLogin: false,
      inTutorial: false,
      id: null,
      name: null,
    };
  }
  if (action.type === 'LOGIN_SKIPPED') {
    return {
      isLoggedIn: false,
      hasSkippedLogin: true,
      inTutorial: false,
      id: null,
      name: null,
    };
  }
  if (action.type === 'LOGIN_LOGGED_OUT') {
    return initialState;
  }
  return state;
}
