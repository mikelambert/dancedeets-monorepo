/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { Animated } from 'react-native';
import type { Action, Dispatch, ThunkAction } from '../actions/types';

const SET_FORM_STATUS = 'searchHeader/SET_FORM_STATUS';
const SET_TITLE_STATUS = 'searchHeader/SET_TITLE_STATUS';

export type State = {
  navbarTitleVisible: boolean,
  searchFormVisible: boolean,
  headerAnim: Animated.Value,
};

const initialState = {
  navbarTitleVisible: true,
  searchFormVisible: false,
  headerAnim: new Animated.Value(0),
};

export default function reducer(state: State = initialState, action: Action) {
  switch (action.type) {
    // do reducer stuff
    case SET_TITLE_STATUS:
      return { ...state, navbarTitleVisible: action.status };
    case SET_FORM_STATUS:
      return { ...state, searchFormVisible: action.status };
    default:
      return state;
  }
}

export function showSearchForm(): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    await dispatch({ type: SET_FORM_STATUS, status: true });
    const state = getState();

    Animated.timing(state.searchHeader.headerAnim, {
      toValue: 1,
      duration: 200,
      useNativeDriver: true,
    }).start(result => {
      dispatch({ type: SET_TITLE_STATUS, status: false });
    });
  };
}

export function hideSearchForm(): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    await dispatch({ type: SET_TITLE_STATUS, status: true });
    const state = getState();

    Animated.timing(state.searchHeader.headerAnim, {
      toValue: 0,
      duration: 100,
      useNativeDriver: true,
    }).start(result => {
      dispatch({ type: SET_FORM_STATUS, status: false });
    });
  };
}
