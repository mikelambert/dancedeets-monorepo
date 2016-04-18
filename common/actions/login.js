/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import FacebookSDK from 'FacebookSDK';
import ActionSheetIOS from 'ActionSheetIOS';
import {Platform} from 'react-native';
import Alert from 'Alert';

import type { Action, ThunkAction } from './types';

async function FacebookLogin(scope): Promise {
  return new Promise((resolve, reject) => {
    FacebookSDK.login((response) => {
      if (response && !response.error) {
        resolve(response);
      } else {
        reject(response && response.error);
      }
    }, {scope});
  });
}

async function queryFacebookAPI(path, ...args): Promise {
  return new Promise((resolve, reject) => {
    FacebookSDK.api(path, ...args, (response) => {
      if (response && !response.error) {
        resolve(response);
      } else {
        reject(response && response.error);
      }
    });
  });
}

async function _logInWithFacebook(source: ?string): Promise<Array<Action>> {
  await FacebookLogin('public_profile,email,user_friends');
  const profile = await queryFacebookAPI('/me', {fields: 'name,email'});

  // TODO: Save user to Mixpanel, as well as to our server with authtoken

  const action = {
    type: 'LOGGED_IN',
    source,
    data: {
      id: profile.id,
      name: profile.name,
    },
  };

  return Promise.all([
    Promise.resolve(action),
  ]);
}

export function logInWithFacebook(source: ?string): ThunkAction {
  return (dispatch) => {
    const login = _logInWithFacebook(source);

    // Loading friends schedules shouldn't block the login process
    login.then(
      (result) => {
        dispatch(result);
        // TODO: Load other things in the background (ie after we sent off the state)
        // that shouldn't block the login process
      }
    );
    return login;
  };
}

export function skipLogin(): Action {
  return {
    type: 'SKIPPED_LOGIN',
  };
}

export function logOut(): ThunkAction {
  return (dispatch) => {
    // TODO: Mixpanel logout
    FacebookSDK.logout();

    // TODO: Make sure reducers clear their state
    return dispatch({
      type: 'LOGGED_OUT',
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
