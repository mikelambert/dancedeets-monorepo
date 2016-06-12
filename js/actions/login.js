/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  AccessToken,
  LoginManager,
} from 'react-native-fbsdk';
import ActionSheetIOS from 'ActionSheetIOS';
import {Platform} from 'react-native';
import Alert from 'Alert';
import { auth } from '../api/dancedeets';
import { trackLogin, trackLogout } from '../store/track';
import { performRequest } from '../api/fb';
import _ from 'lodash/array';
import type { Action, Dispatch, hunkAction } from './types';


export function loginStartOnboard(): Action {
  return {
    type: 'LOGIN_START_ONBOARD',
  };
}

export function loginComplete(token: AccessToken): Action {
  // Kick these off and let them happen in the background
  return (dispatch: Dispatch) => {
    auth();
    trackLogin();
    loadUserData(dispatch);
    // But mark us as logged-in here
    dispatch({
      type: 'LOGIN_LOGGED_IN',
      token: token,
    });
  };
}

/*
export function performSearch(): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const searchQuery = getState().search.searchQuery;
    track('Search Events', {
      'Location': searchQuery.location,
      'Keywords': searchQuery.keywords,
    });
    await dispatch(searchStart());
    try {
*/
async function loadUserData(dispatch) {
  const requests = {
    profile: performRequest('GET', 'me', {fields: 'id,name'}),
    picture: performRequest('GET', 'me/picture', {type: 'large', fields: 'url', redirect: '0'}),
    friends: performRequest('GET', 'me/friends', {limit: '1000', fields: 'id'}),
  };

  const keys = Object.keys(requests);
  const promises = keys.map((x) => requests[x]);
  const values = await Promise.all(promises);
  // Now await each of them and stick them in our user Object
  const user = {};
  _.zip(keys, values).forEach(async (kv) => {
    user[kv[0]] = kv[1];
  });

  dispatch({
    type: 'LOGIN_LOADED_USER',
    user,
  });
}

export function skipLogin(): Action {
  return {
    type: 'LOGIN_SKIPPED',
  };
}

export function logOut(): ThunkAction {
  return (dispatch) => {
    LoginManager.logOut();
    trackLogout();
    return dispatch({
      type: 'LOGIN_LOGGED_OUT',
    });
  };
}

export function logOutWithPrompt(): ThunkAction {
  return (dispatch, getState) => {
    let name = getState().user.name || 'there';

    if (Platform.OS === 'ios') {
      ActionSheetIOS.showActionSheetWithOptions(
        {
          title: `Hi, ${name}`,
          options: ['Log out', 'Cancel'],
          destructiveButtonIndex: 0,
          cancelButtonIndex: 1,
        },
        (buttonIndex) => {
          if (buttonIndex === 0) {
            dispatch(logOut());
          }
        }
      );
    } else {
      Alert.alert(
        `Hi, ${name}`,
        'Log out from DanceDeets?',
        [
          { text: 'Cancel' },
          { text: 'Log out', onPress: () => dispatch(logOut()) },
        ]
      );
    }
  };
}
