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
import { userInfo } from '../api/dancedeets';
import _ from 'lodash/array';
import type { Action, Dispatch, ThunkAction, User } from './types';
import Geocoder from '../api/geocoder';
import {format} from '../events/formatAddress';
import {
  defineMessages,
  intlShape,
} from 'react-intl';

const messages = defineMessages({
  logoutButton: {
    id: 'login.logout',
    defaultMessage: 'Logout',
    description: 'Button to log out of the app',
  },
  cancelButton: {
    id: 'buttons.cancel',
    defaultMessage: 'Cancel',
    description: 'Button to cancel',
  },
  logoutPrompt: {
    id: 'login.logoutPrompt',
    defaultMessage: 'Logout from my account',
    description: 'Prompt to show the user before logging out',
  }
});


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
export async function loadUserData(dispatch) {
  const requests = {
    profile: performRequest('GET', 'me', {fields: 'id,name'}),
    picture: performRequest('GET', 'me/picture', {type: 'large', fields: 'url', redirect: '0'}),
    friends: performRequest('GET', 'me/friends', {limit: '1000', fields: 'id'}),
    ddUser: userInfo(),
  };

  const keys = Object.keys(requests);
  const promises = keys.map((x) => requests[x]);
  const values = await Promise.all(promises);
  // Now await each of them and stick them in our user Object
  const user: any = {};
  _.zip(keys, values).forEach((kv) => {
    user[kv[0]] = kv[1];
  });

  // Since ddUser.location could be a full address, let's get just the city
  const address = await Geocoder.geocodeAddress(user.ddUser.location);
  const formattedCity = format(address[0]);
  user.ddUser.formattedCity = formattedCity;

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

export function logOutWithPrompt(intl: intlShape): ThunkAction {
  return (dispatch, getState) => {
    let name = getState().user.userData.profile.name || 'DanceDeets';

    if (Platform.OS === 'ios') {
      ActionSheetIOS.showActionSheetWithOptions(
        {
          title: intl.formatMessage(messages.logoutPrompt, {name}),
          options: [intl.formatMessage(messages.logoutButton), intl.formatMessage(messages.cancelButton)],
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
        intl.formatMessage(messages.logoutButton),
        intl.formatMessage(messages.logoutPrompt, {name}),
        [
          { text: intl.formatMessage(messages.cancelButton) },
          { text: intl.formatMessage(messages.logoutButton), onPress: () => dispatch(logOut()) },
        ]
      );
    }
  };
}
