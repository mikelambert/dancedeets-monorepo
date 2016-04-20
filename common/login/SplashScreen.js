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

async function performLoginTransitions(dispatch: Dispatch) {
  //await dispatch(loginWaitingForState())
  const accessToken = await AccessToken.getCurrentAccessToken();
  console.log('AccessToken is:', accessToken);
  if (!accessToken) {
    console.log('Wait for onboarding!');
    return dispatch(loginStartOnboard());
  } else {
    var howLongAgo = Math.round((Date.now() - accessToken.lastRefreshTime) / 1000);
    if (howLongAgo < 60 * 60) {
      console.log('Good access token, finishing login!');
      return dispatch(loginComplete());
    } else {
      try {
        await AccessToken.refreshCurrentAccessTokenAsync();
        const newAccessToken = await AccessToken.getCurrentAccessToken();
        console.log('Refreshed Token result:', newAccessToken);
        // We intentionally use != instead of !== due to the need to protect against undefined:
        // described more in http://flowtype.org/docs/nullable-types.html
        if (newAccessToken != null && !newAccessToken.getPermissions().includes('user_events')) {
          await loginOrLogout();
        }
      } catch (exc) {
        console.log('Exception refreshing or logging in:', exc);
        LoginManager.logOut();
      }
    }
    return performLoginTransitions(dispatch);
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
