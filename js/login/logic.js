/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import _ from 'lodash/collection';
import {
  Alert
} from 'react-native';
import {
  LoginManager,
  AccessToken,
} from 'react-native-fbsdk';
import { loginStartOnboard, loginComplete } from '../actions';
import type { Dispatch } from '../actions/types';
import { track } from '../store/track';
import {
  defineMessages,
  intlShape,
} from 'react-intl';


const messages = defineMessages({
  loginTitle: {
    id: 'login.title',
    defaultMessage: 'Login Required',
    description: 'Title for window prompting tuser if they would like to log in',
  },
  loginMessage: {
    id: 'login.message',
    defaultMessage: '"{feature}" requires logging in. Would you like to login?',
    description: 'Prompt in asking the user if they would like to login',
  },
  promptCancel: {
    id: 'prompt.cancel',
    defaultMessage: 'Cancel',
    description: 'Cancel button',
  },
  promptOk: {
    id: 'prompt.ok',
    defaultMessage: 'OK',
    description: 'OK button',
  },
});

export async function canGetValidLoginFor(feature: string, intl: intlShape, dispatch: Dispatch) {
  return new Promise((resolve, reject) => {
    const ok = async () => {
      const loggedIn = await loginButtonPressed(dispatch);
      resolve(Boolean(loggedIn));
    };
    const cancel = () => {
      resolve(false);
    };
    Alert.alert(
      intl.formatMessage(messages.loginTitle),
      intl.formatMessage(messages.loginMessage, {feature}),
      [
        {text: intl.formatMessage(messages.promptCancel), onPress: cancel, style: 'cancel'},
        {text: intl.formatMessage(messages.promptOk), onPress: ok},
      ]
    );
  });
}

export async function loginButtonPressed(dispatch: Dispatch) {
  try {
    const token = await loginOrLogout();
    track('Login - Completed');
    await dispatch(loginComplete(token));
    return token;
  } catch (e) {
    console.log('Staying on this screen, failed to login because: ' + e);
    return null;
  }
}

export async function autoLoginAtStartup(dispatch: Dispatch, secondTime: boolean = false) {
  // When they open the app, check for their existing FB token.
  if (await isLoggedOut()) {
    console.log('Wait for onboarding!');
    track('Login - Not Logged In');
    return await dispatch(loginStartOnboard());
  // Now let's check how old the token is. We want to refresh old tokens,
  // but not delay/block users who have recently refreshed.
  } else if (secondTime || await isRecentlyLoggedIn()) {
    console.log('Fresh access token, completing login!');
    const token = await AccessToken.getCurrentAccessToken();
    if (token != null) {
      return await dispatch(loginComplete(token));
    } else {
      console.error('We have a recently logged-in token, but no token??');
    }
  } else {
    await refreshFullToken();
    // Okay, now we've either refreshed with a new valid authtoken, or we've logged the user out.
    // Let's send them back into the flow, which will start onboarding or start the main app.
    return autoLoginAtStartup(dispatch, true);
  }
}

async function loginOrLogout(): Promise<AccessToken> {
  console.log('Presenting FB Login Dialog...');
  const loginResult = await LoginManager.logInWithReadPermissions(['public_profile', 'email', 'user_friends', 'user_events']);
  console.log('LoginResult is ', loginResult);
  if (loginResult.isCancelled) {
    LoginManager.logOut();
    throw new Error('Canceled by user');
  }

  var accessToken = await AccessToken.getCurrentAccessToken();
  if (accessToken != null) {
    return accessToken;
  } else {
    throw new Error('No access token');
  }
}


async function isLoggedOut() {
  const accessToken = await AccessToken.getCurrentAccessToken();
  return !accessToken;
}

async function isRecentlyLoggedIn() {
  const accessToken = await AccessToken.getCurrentAccessToken();
  if (accessToken != null) {
    var howLongAgo = Math.round((Date.now() - accessToken.lastRefreshTime) / 1000);
    return (howLongAgo < 24 * 60 * 60);
  } else {
    // This shouldn't happen, since we check isLoggedOut() before isRecentlyLoggedIn().
    // But let's handle it correctly anyway.
    return false;
  }
}

async function refreshFullToken() {
  // If we need to refresh, there's a lot of things that can go wrong:
  // Errors refreshing, errors getting additional permissions, etc.
  // If they happen, let's log them out and send them back in through the flow above.
  try {
    // First refresh the token. This returns a list of permissions approved/declined,
    // which we don't care about using as such.
    await AccessToken.refreshCurrentAccessTokenAsync();
    // Let's grab the actual access token (which should now be cached from the refresh).
    // This has an easier API to work with too.
    const newAccessToken = await AccessToken.getCurrentAccessToken();
    // Don't want to log actual token to public log file, so check truthiness
    console.log('Refreshed Token result:', (newAccessToken != null));
    // Now check if this token has user_events permission (our most important permission)
    // For awhile many iOS users were being approved without this permission due to a bug.
    // So this requests they log in again to explicitly grab that permission.
    //
    // NOTE: We intentionally use != instead of !== due to the need to protect against undefined:
    // described more in http://flowtype.org/docs/nullable-types.html
    // This != fixes Flow, but then flags with ESLint!
    // Can remove _.includes when RN 0.27 is released:
    // https://github.com/facebook/react-native/commit/ed47efe4a17a6fa3f0a2a8a36600efdcd1c65b86
    if (newAccessToken != null && !_.includes(newAccessToken.getPermissions(), 'user_events')) {
      await loginOrLogout();
    }
  } catch (e) {
    // Something strange happened! (Maybe no internet: Error: The Internet connection appears to be offline.)
    console.log('Exception refreshing or logging in:', e, e.stack);
  }
}
