/**
 * Copyright 2016 DanceDeets.
 * @flow
 */
'use strict';

import F8Colors from '../Colors';
import StatusBarIOS from 'StatusBarIOS';
import React, {
  Animated,
  Component,
  Dimensions,
  Image,
  ListView,
  StyleSheet,
  Text,
  TouchableWithoutFeedback,
  View,
} from 'react-native';
import {
  LoginManager,
  AccessToken,
} from 'react-native-fbsdk';
// TODO: Maybe when we have styles, use a DDText.js file?
// TODO: import LoginButton from '../common/LoginButton';

import { skipLogin, loginWaitingForState, loginStartTutorial, loginComplete } from '../actions';
import { connect } from 'react-redux';



function select(store) {
  return {
    isLoggedIn: store.user.isLoggedIn,
    inTutorial: store.user.inTutorial,
  };
}

class SplashScreen extends React.Component {
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
    if (this.props.inTutorial) {
      return <Text>Heeeeey</Text>;
    }
    var onPress=null;
    return (
      <TouchableWithoutFeedback
        //onPress={() => this.props.dispatch(skipLogin())}>
        onPress={onPress}>
        <Image
          style={styles.container}
          source={require('./images/LaunchScreen.jpg')}>
          <Image
            style={styles.container}
            source={require('./images/LaunchScreenText.png')}>
          </Image>
        </Image>
      </TouchableWithoutFeedback>
    );
    //<LoginButton source="First screen" />
  }
}
export default connect(select)(SplashScreen);

async function loginOrLogout() {
  console.log("loginOrLogout");
  try {
    var loginResult = await LoginManager.logInWithReadPermissions(["public_profile", "email", "user_friends", "user_events"]);
    console.log("LoginResult is " + loginResult);
    if (loginResult.isCancelled) {
      LoginManager.logOut();
    }
  } catch (exc) {
    console.log('Error calling logInWithReadPermissions' + exc);
  }
}

async function performLoginTransitions(dispatch) {
  //await dispatch(loginWaitingForState())
  const accessToken = await AccessToken.getCurrentAccessToken();
  console.log("AccessToken is " + accessToken);
  if (!accessToken) {
    console.log("Wait for click!");
    return dispatch(loginStartTutorial());
  } else {
    var howLongAgo = Math.round((Date.now() - accessToken.refreshDate) / 1000);
    if (howLongAgo < 60 * 60) {
      console.log("Good click, logging in!");
      return dispatch(loginComplete())
    } else {
      try {
        const token = await AccessToken.refreshCurrentAccessTokenAsync();
        console.log("Refreshed Token result is " + token);
        if (!token.hasGranted("user_events")) {
          await loginOrLogout();
        }
      } catch (exc) {
        console.log("Exception refreshing or logging in: " + exc);
        LoginManager.logOut();
      }
    }
    return performLoginTransitions();
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
