/**
 * Copyright 2016 DanceDeets.
 */

import { Animated } from 'react-native';
import type { Action, Dispatch, ThunkAction } from '../actions/types';

const START_OPEN = 'searchHeader/START_OPEN';
const FINISH_OPEN = 'searchHeader/FINISH_OPEN';
const START_CLOSE = 'searchHeader/START_CLOSE';
const FINISH_CLOSE = 'searchHeader/FINISH_CLOSE';

export interface State {
  navbarTitleVisible: boolean;
  searchFormVisible: boolean;
  headerAnim: Animated.Value;
}

const initialState: State = {
  navbarTitleVisible: true,
  searchFormVisible: false,
  headerAnim: new Animated.Value(0),
};

export default function reducer(state: State = initialState, action: Action): State {
  switch (action.type) {
    // do reducer stuff
    case START_OPEN:
      return { ...state, navbarTitleVisible: true, searchFormVisible: true };
    case FINISH_OPEN:
      return { ...state, navbarTitleVisible: false, searchFormVisible: true };
    case START_CLOSE:
      return { ...state, navbarTitleVisible: true, searchFormVisible: true };
    case FINISH_CLOSE:
      return { ...state, navbarTitleVisible: true, searchFormVisible: false };
    default:
      return state;
  }
}

export function showSearchForm(): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const state = getState();
    if (!state.searchHeader.navbarTitleVisible) {
      return;
    }
    await dispatch({ type: START_OPEN });

    Animated.timing(state.searchHeader.headerAnim, {
      toValue: 1,
      duration: 200,
      useNativeDriver: true,
    }).start(result => {
      dispatch({ type: FINISH_OPEN });
    });
  };
}

export function hideSearchForm(): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const state = getState();
    if (!state.searchHeader.searchFormVisible) {
      return;
    }
    await dispatch({ type: START_CLOSE });

    Animated.timing(state.searchHeader.headerAnim, {
      toValue: 0,
      duration: 100,
      useNativeDriver: true,
    }).start(result => {
      dispatch({ type: FINISH_CLOSE });
    });
  };
}
