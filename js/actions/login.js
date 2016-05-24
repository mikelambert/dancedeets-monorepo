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

import type { Action, ThunkAction } from './types';


export function loginStartOnboard(): Action {
  return {
    type: 'LOGIN_START_ONBOARD',
  };
}

export function loginComplete(token: AccessToken): Action {
  auth(token);
  return {
    type: 'LOGIN_LOGGED_IN',
    token: token,
  };
}

export function skipLogin(): Action {
  return {
    type: 'LOGIN_SKIPPED',
  };
}

export function logOut(): ThunkAction {
  return (dispatch) => {
    // TODO: Mixpanel logout
    LoginManager.logOut();

    // TODO: Make sure reducers clear their state
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
