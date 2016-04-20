/**
 * Copyright DanceDeets.
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

export type State = { type: 'CAROUSEL' } | { type: 'NO_LOGIN' } | { type: 'STILL_NO_LOGIN' };

var initialState = { type: 'CAROUSEL' };
export function onboarding(state: State = initialState, action: Action): State {
  if (action.type == 'LOGIN_START_ONBOARD') {
    return initialState;
  }
  if (action.type == 'ONBOARD_NO_LOGIN') {
    return { type: 'NO_LOGIN' };
  }
  if (action.type == 'ONBOARD_STILL_NO_LOGIN') {
    return { type: 'STILL_NO_LOGIN' };
  }
  return state;
}
