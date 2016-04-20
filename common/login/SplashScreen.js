/**
 * Copyright 2016 DanceDeets.
 * @flow
 */
'use strict';

import StatusBarIOS from 'StatusBarIOS';
import React, {
  Image,
  StyleSheet,
  TouchableWithoutFeedback,
} from 'react-native';
import {
  LoginManager,
  AccessToken,
} from 'react-native-fbsdk';
import OnboardingFlow from './OnboardingFlow';
// TODO: Maybe when we have styles, use a DDText.js file?
// TODO: import LoginButton from '../common/LoginButton';
import { loginOrLogout } from '../FacebookSDK';
import { loginStartOnboard, loginComplete } from '../actions';
import { connect } from 'react-redux';
import type { Dispatch } from '../actions/types';


function select(store) {
  return {
    isLoggedIn: store.user.isLoggedIn,
    isOnboarding: store.user.isOnboarding,
  };
}


class SplashScreen extends React.Component {


  state: {
  };

  constructor(props) {
    super(props);
    this.state = {
    };
  }

  componentDidMount() {
    StatusBarIOS && StatusBarIOS.setStyle('default');
    performLoginTransitions(this.props.dispatch);
  }

  render() {
    if (this.props.isOnboarding) {
      return <OnboardingFlow />;
    }
    return (
      <TouchableWithoutFeedback
        //onPress={() => this.props.dispatch(skipLogin())}>
        >
        <Image
          style={styles.container}
          source={require('./images/LaunchScreen.jpg')}>
          <Image
            style={styles.container}
            source={require('./images/LaunchScreenText.png')} />
        </Image>
      </TouchableWithoutFeedback>
    );
    //<LoginButton source="First screen" />
  }
}
export default connect(select)(SplashScreen);


async function isLoggedOut() {
  const accessToken = await AccessToken.getCurrentAccessToken();
  return !accessToken;
}

async function isRecentlyLoggedIn() {
  const accessToken = await AccessToken.getCurrentAccessToken();
  if (accessToken != null) {
    var howLongAgo = Math.round((Date.now() - accessToken.lastRefreshTime) / 1000);
    return (howLongAgo < 60 * 60);
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
    if (newAccessToken != null && !newAccessToken.getPermissions().includes('user_events')) {
      await loginOrLogout();
    }
  } catch (exc) {
    // Something strange happened!
    // Let's log them out, and send them back in from the top without a token.
    // This effectively drops them back in the onboarding flow.
    console.log('Exception refreshing or logging in:', exc);
    LoginManager.logOut();
  }
}

async function performLoginTransitions(dispatch: Dispatch, allowRecursion = true) {
  // When they open the app, check for their existing FB token.
  if (await isLoggedOut()) {
    console.log('Wait for onboarding!');
    return dispatch(loginStartOnboard());
  // Now let's check how old the token is. We want to refresh old tokens,
  // but not delay/block users who have recently refreshed.
  } else if (await isRecentlyLoggedIn()) {
    console.log('Fresh access token, completing login!');
    return dispatch(loginComplete());
  } else if (allowRecursion) {
    refreshFullToken();
    // Okay, now we've either refreshed with a new valid authtoken, or we've logged the user out.
    // Let's send them back into the flow, which will start onboarding or start the main app.
    return performLoginTransitions(dispatch, false);
  } else {
    // This "Shouldn't Happen"...the recursive case should have been handled
    // by one of the first two functions. But in either case, let's log as best we can.
    // And then ensure the user still has a pleasant experience.
    // The user didn't pass isLoggedOut, so they must be loggedIn with an old token.
    // That should be good enough to use our app and associated FB SDK calls!
    return dispatch(loginComplete());
  }
}

var styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    // Image's source contains explicit size, but we want
    // it to prefer flex: 1
    width: undefined,
    height: undefined,
  }
});
