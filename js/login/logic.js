/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import _ from 'lodash/collection';
import {
  LoginManager,
  AccessToken,
} from 'react-native-fbsdk';
import { loginStartOnboard, loginComplete } from '../actions';
import type { Dispatch } from '../actions/types';

export async function loginButtonPressed(dispatch: Dispatch) {
  try {
    const token = await loginOrLogout();
    dispatch(loginComplete(token));
  } catch (e) {
    console.log('Staying on this screen, failed to login: ', e, e.stack);
  }
}

export async function autoLoginAtStartup(dispatch: Dispatch, allowRecursion: boolean = true) {
  // When they open the app, check for their existing FB token.
  if (await isLoggedOut()) {
    console.log('Wait for onboarding!');
    return dispatch(loginStartOnboard());
  // Now let's check how old the token is. We want to refresh old tokens,
  // but not delay/block users who have recently refreshed.
  } else if (await isRecentlyLoggedIn()) {
    console.log('Fresh access token, completing login!');
    // TODO: send up /auth /user API call now
    const token = await AccessToken.getCurrentAccessToken();
    if (token != null) {
      return dispatch(loginComplete(token));
    } else {
      console.error('We have a recently logged-in token, but no token??');
    }
  } else if (allowRecursion) {
    await refreshFullToken();
    // Okay, now we've either refreshed with a new valid authtoken, or we've logged the user out.
    // Let's send them back into the flow, which will start onboarding or start the main app.
    return autoLoginAtStartup(dispatch, false);
  } else {
    // This "Shouldn't Happen"...the recursive case should have been handled
    // by one of the first two functions. But in either case, let's log as best we can.
    // And then ensure the user still has a pleasant experience.
    // The user didn't pass isLoggedOut, so they must be loggedIn with an old token.
    // That should be good enough to use our app and associated FB SDK calls!
    const token = await AccessToken.getCurrentAccessToken();
    if (token != null) {
      // Log in with our old/expired token
      return dispatch(loginComplete(token));
    } else {
      console.error("We aren't logged out, but we still don't have a token??");
    }
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
    console.log('Refreshed Token result:', newAccessToken);
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
    // Something strange happened!
    // Let's log them out, and send them back in from the top without a token.
    // This effectively drops them back in the onboarding flow.
    console.log('Exception refreshing or logging in:', e, e.stack);
    LoginManager.logOut();
  }
}
