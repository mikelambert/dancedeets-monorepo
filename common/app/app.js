/**
 * Copyright 2016 DanceDeets.
 *
 * @providesModule App
 * @flow
 */

'use strict';

import React from 'React';
import AppState from 'AppState';
import LoginScreen from '../login/LoginScreen';
import StyleSheet from 'StyleSheet';
import AppContainer from '../containers/AppContainer';
// import CodePush from 'react-native-code-push';
import View from 'View';
import StatusBar from 'StatusBar';
import { connect } from 'react-redux';
import { version } from './env.js';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.loadAppData = this.loadAppData.bind(this);
    this.componentDidMount = this.componentDidMount.bind(this);
  }
  loadAppData() {
    // TODO: Download any app-wide data we need, here.
  }

  componentDidMount() {
    AppState.addEventListener('change', this.handleAppStateChange);
    this.loadAppData();
    // TODO: Enable CodePush at some point before launch
    // CodePush.sync({installMode: CodePush.InstallMode.ON_NEXT_RESUME});
  }

  componentWillUnmount() {
    AppState.removeEventListener('change', this.handleAppStateChange);
  }

  handleAppStateChange(appState) {
    if (appState === 'active') {
      loadAppData();
      // CodePush.sync({installMode: CodePush.InstallMode.ON_NEXT_RESUME});
    }
  }

  render() {
    if (!this.props.isLoggedIn) {
      return <LoginScreen />;
    }
    return (
      <View style={styles.container}>
        <StatusBar
          translucent={true}
          backgroundColor="rgba(0, 0, 0, 0.2)"
          barStyle="light-content"
         />
        <AppContainer />
      </View>
    );
  }
  // Add <PushNotificationsController /> back in to <View>...

}

var styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

function select(store) {
  return {
    isLoggedIn: store.user.isLoggedIn || store.user.hasSkippedLogin,
  };
}

module.exports = connect(select)(App);
