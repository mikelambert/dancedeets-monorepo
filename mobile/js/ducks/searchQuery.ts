/**
 * Copyright 2016 DanceDeets.
 */

import { Animated } from 'react-native';
import type { SearchQuery } from 'dancedeets-common/js/events/search';
import type { Action, Dispatch, ThunkAction } from '../actions/types';

const UPDATE_LOCATION = 'textInputs/UPDATE_LOCATION';
const UPDATE_KEYWORDS = 'textInputs/UPDATE_KEYWORDS';
const DETECTED_LOCATION = 'textInputs/DETECTED_LOCATION';

export type State = SearchQuery; // our current tentative search query

const initialState: State = {
  location: '',
  keywords: '',
  timePeriod: 'ALL_FUTURE',
};

export default function reducer(state: State = initialState, action: Action): State {
  if (
    action.type === UPDATE_LOCATION ||
    // Only set location from GPS if user hasn't entered any location
    (action.type === DETECTED_LOCATION && state.location === '')
  ) {
    return { ...state, location: action.location };
  } else if (action.type === UPDATE_KEYWORDS) {
    return { ...state, keywords: action.keywords };
  } else {
    return state;
  }
}

export function updateLocation(location: string): Action {
  return {
    type: UPDATE_LOCATION,
    location,
  };
}

export function updateKeywords(keywords: string): Action {
  return {
    type: UPDATE_KEYWORDS,
    keywords,
  };
}

export function detectedLocation(location: string): ThunkAction {
  return async (dispatch: Dispatch) => {
    await dispatch({
      type: DETECTED_LOCATION,
      location,
    });
  };
}
