/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { Dimensions } from 'react-native';
import type { SearchResponse } from 'dancedeets-common/js/events/search';
import type { Action } from '../actions/types';

export type State = {
  loading: boolean, // loading indicator
  response: ?SearchResponse, // our last-searched response
  error: boolean, // whether there was an error fetching the current results
  errorString: ?string, // the error message to display to the user, if we have one
  waitingForLocationPermission: boolean, // are we waiitng for the user to grant the location permission
};

const initialState = {
  loading: false,
  response: null,
  error: false,
  errorString: null,
  waitingForLocationPermission: false,
};

export function search(state: State = initialState, action: Action): State {
  if (action.type === 'LOGIN_LOGGED_OUT') {
    return initialState;
  } else if (action.type === 'START_SEARCH') {
    return {
      ...state,
      loading: true,
      error: false,
      response: null,
    };
  } else if (action.type === 'SEARCH_COMPLETE') {
    return {
      ...state,
      loading: false,
      response: action.response,
    };
  } else if (action.type === 'SEARCH_FAILED') {
    return {
      ...state,
      loading: false,
      response: null,
      error: true,
      errorString: action.errorString,
    };
  } else if (action.type === 'WAITING_FOR_LOCATION') {
    return {
      ...state,
      waitingForLocationPermission: action.waiting,
    };
  }
  return state;
}
