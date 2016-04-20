/**
 * Copyright DanceDeets.
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

export type State = {
  isLoggedIn: boolean;
  hasSkippedLogin: boolean;
  isOnboarding: boolean;
  id: ?string;
  name: ?string;
};

const initialState = {
  isLoggedIn: false,
  hasSkippedLogin: false,
  isOnboarding: false,
  //TODO: do we want/need these?
  id: null,
  name: null,
};

export function user(state: State = initialState, action: Action): State {
  if (action.type === 'LOGIN_LOADING') {
    return initialState;
  }
  if (action.type === 'LOGIN_START_ONBOARD') {
    return {
      isLoggedIn: false,
      hasSkippedLogin: false,
      isOnboarding: true,
      id: null,
      name: null,
    };
  }
  if (action.type === 'LOGIN_LOGGED_IN') {
    return {
      isLoggedIn: true,
      hasSkippedLogin: false,
      isOnboarding: false,
      id: null,
      name: null,
    };
  }
  if (action.type === 'LOGIN_SKIPPED') {
    return {
      isLoggedIn: false,
      hasSkippedLogin: true,
      isOnboarding: false,
      id: null,
      name: null,
    };
  }
  if (action.type === 'LOGIN_LOGGED_OUT') {
    return initialState;
  }
  return state;
}
