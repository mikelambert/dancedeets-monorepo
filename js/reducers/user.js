/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

type User = {
  profile: any;
  picture: {data: {url: string}};
  friends: any;
};

export type State = {
  isLoggedIn: boolean;
  hasSkippedLogin: boolean;
  isOnboarding: boolean;
  userData: ?User;
};

const initialState = {
  isLoggedIn: false,
  hasSkippedLogin: false,
  isOnboarding: false,
  userData: null,
};

export function user(state: State = initialState, action: Action): State {
  if (action.type === 'LOGIN_LOGGED_OUT') {
    return initialState;
  }
  if (action.type === 'LOGIN_LOADED_USER') {
    console.log(action.user);
    return {
      ...state,
      userData: action.user,
    };
  }
  if (action.type === 'LOGIN_START_ONBOARD') {
    return {
      isLoggedIn: false,
      hasSkippedLogin: false,
      isOnboarding: true,
      userData: null,
    };
  }
  if (action.type === 'LOGIN_LOGGED_IN') {
    return {
      isLoggedIn: true,
      hasSkippedLogin: false,
      isOnboarding: false,
      userData: null,
    };
  }
  if (action.type === 'LOGIN_SKIPPED') {
    return {
      isLoggedIn: false,
      hasSkippedLogin: true,
      isOnboarding: false,
      userData: null,
    };
  }
  return state;
}
