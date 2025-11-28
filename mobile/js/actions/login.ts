/**
 * Copyright 2016 DanceDeets.
 */

import { AccessToken, LoginManager } from 'react-native-fbsdk';
import { ActionSheetIOS, Alert, Platform } from 'react-native';
import { defineMessages, IntlShape } from 'react-intl';
import zip from 'lodash/zip';
import { trackLogin, trackLogout } from '../store/track';
import { performRequest } from '../api/fb';
import { auth, userInfo } from '../api/dancedeets';
import type { Action, Dispatch, ThunkAction, GetState, User } from './types';
import Geocoder from '../api/geocoder';
import { format } from '../events/formatAddress';
import { setSkippedLogin } from '../login/savedState';

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
  },
});

export function loginStartOnboard(): Action {
  return {
    type: 'LOGIN_START_ONBOARD',
  };
}

async function authAndGetUser(dispatch: Dispatch): Promise<void> {
  // This could be the first time this user is created.
  // So let's ensure the user is successfully created,
  // before we try to loadUserData and pull in empty data.
  await auth();
  loadUserData(dispatch);
}

export function loginComplete(token: AccessToken): ThunkAction {
  // Kick these off and let them happen in the background
  return async (dispatch: Dispatch) => {
    authAndGetUser(dispatch);
    trackLogin();
    // But mark us as logged-in here
    dispatch({
      type: 'LOGIN_LOGGED_IN',
      token,
    });
  };
}

interface FBRequestsMap {
  profile: Promise<{ id: string; name: string }>;
  picture: Promise<{ data: { url: string } }>;
  friends: Promise<{ data: Array<{ id: string }> }>;
  ddUser: Promise<{ location: string }>;
}

export async function loadUserData(dispatch: Dispatch): Promise<void> {
  const requests: FBRequestsMap = {
    profile: performRequest('GET', 'me', { fields: 'id,name' }),
    picture: performRequest('GET', 'me/picture', {
      type: 'large',
      fields: 'url',
      redirect: '0',
    }),
    friends: performRequest('GET', 'me/friends', {
      limit: '1000',
      fields: 'id',
    }),
    ddUser: userInfo(),
  };

  const keys = Object.keys(requests) as Array<keyof FBRequestsMap>;
  const promises = keys.map(x => requests[x]);
  const values = await Promise.all(promises);
  // Now await each of them and stick them in our user Object
  const user: Record<string, unknown> = {};
  zip(keys, values).forEach(kv => {
    if (kv[0]) {
      user[kv[0]] = kv[1];
    }
  });

  // Since ddUser.location could be a full address, let's get just the city
  const ddUser = user.ddUser as { location: string; formattedCity?: string };
  let formattedCity = ddUser.location;
  // If we fail to parse the address, just use the user's configured location above
  const address = await Geocoder.geocodeAddress(ddUser.location);
  if (address.length !== 0) {
    formattedCity = format(address[0]);
  }
  ddUser.formattedCity = formattedCity;

  dispatch({
    type: 'LOGIN_LOADED_USER',
    user: user as User,
  });
}

export function skipLogin(): ThunkAction {
  return (dispatch: Dispatch) => {
    setSkippedLogin(true);
    return dispatch({
      type: 'LOGIN_SKIPPED',
    });
  };
}

export function logOut(): ThunkAction {
  return (dispatch: Dispatch) => {
    LoginManager.logOut();
    setSkippedLogin(false);
    trackLogout();
    return dispatch({
      type: 'LOGIN_LOGGED_OUT',
    });
  };
}

interface UserState {
  user: {
    userData?: {
      profile?: {
        name: string;
      };
    };
  };
}

export function logOutWithPrompt(intl: IntlShape): ThunkAction {
  return (dispatch: Dispatch, getState: GetState) => {
    let name = 'DanceDeets';
    const userData = (getState() as unknown as UserState).user.userData;
    if (userData && userData.profile) {
      name = userData.profile.name;
    }

    if (Platform.OS === 'ios') {
      ActionSheetIOS.showActionSheetWithOptions(
        {
          title: intl.formatMessage(messages.logoutPrompt, { name }),
          options: [
            intl.formatMessage(messages.logoutButton),
            intl.formatMessage(messages.cancelButton),
          ],
          destructiveButtonIndex: 0,
          cancelButtonIndex: 1,
        },
        (buttonIndex: number) => {
          if (buttonIndex === 0) {
            dispatch(logOut());
          }
        }
      );
    } else {
      Alert.alert(
        intl.formatMessage(messages.logoutButton),
        intl.formatMessage(messages.logoutPrompt, { name }),
        [
          { text: intl.formatMessage(messages.cancelButton) },
          {
            text: intl.formatMessage(messages.logoutButton),
            onPress: () => dispatch(logOut()),
          },
        ]
      );
    }
  };
}
