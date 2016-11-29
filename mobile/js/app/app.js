/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  AppState,
  Linking,
  StatusBar,
  StyleSheet,
  View,
} from 'react-native';
import LoginFlow from '../login/LoginFlow';
import CodePush from 'react-native-code-push';
import { connect } from 'react-redux';
import TabbedApp from '../containers/TabbedApp';
import { gradientTop } from '../Colors';
import { setup as setupNotifications } from '../notifications/setup';
import storeShape from 'react-redux/lib/utils/storeShape';
import { intlShape } from 'react-intl';
import { processUrl } from '../actions';

class App extends React.Component {
  constructor(props, context) {
    super(props, context);
    (this: any).handleAppStateChange = this.handleAppStateChange.bind(this);
    (this: any).componentDidMount = this.componentDidMount.bind(this);
    (this: any).handleOpenURL = this.handleOpenURL.bind(this);
    setupNotifications(context.store.dispatch, context.intl);
  }

  loadAppData() {
    // TODO: Download any app-wide data we need, here.
  }

  componentDidMount() {
    AppState.addEventListener('change', this.handleAppStateChange);
    this.loadAppData();
    CodePush.sync({installMode: CodePush.InstallMode.ON_NEXT_RESUME, minimumBackgroundDuration: 60 * 5});
    Linking.addEventListener('url', this.handleOpenURL);
  }

  componentWillUnmount() {
    AppState.removeEventListener('change', this.handleAppStateChange);
    Linking.removeEventListener('url', this.handleOpenURL);
  }

  handleOpenURL(event) {
    this.props.processUrl(event.url);
  }

  handleAppStateChange(appState) {
    if (appState === 'active') {
      this.loadAppData();
      CodePush.sync({installMode: CodePush.InstallMode.ON_NEXT_RESUME, minimumBackgroundDuration: 60 * 5});
    }
  }

  render() {
    if (!this.props.user.isLoggedIn && !this.props.user.hasSkippedLogin) {
      return <LoginFlow />;
    }
    return (
      <View style={styles.container}>
        <StatusBar
          translucent={false}
          backgroundColor={gradientTop}
          barStyle="light-content"
         />
        <TabbedApp />
      </View>
    );
  }
  // Add <PushNotificationsController /> back in to <View>...
}
App.contextTypes = {
  store: storeShape,
  intl: intlShape,
};
export default connect(
  store => ({
    user: store.user,
  }),
  dispatch => ({
    processUrl: (event) => dispatch(processUrl(event)),
  }),
)(App);

var styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
