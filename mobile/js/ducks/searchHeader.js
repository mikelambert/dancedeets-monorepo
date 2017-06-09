/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import type { Action } from '../actions/types';

const SET_STATUS = 'searchHeader/SET_STATUS';

export type State = {
  headerOpened: boolean,
};

const initialState = {
  headerOpened: false,
};

export default function reducer(state: State = initialState, action: Action) {
  switch (action.type) {
    // do reducer stuff
    case SET_STATUS:
      return { ...state, headerOpened: action.status };
    default:
      return state;
  }
}

export function setHeaderStatus(status: boolean): Action {
  return { type: SET_STATUS, status };
}
