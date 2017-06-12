/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { AppState, Linking, StatusBar, StyleSheet, View } from 'react-native';
import CodePush from 'react-native-code-push';
import { connect } from 'react-redux';
import storeShape from 'react-redux/lib/utils/storeShape';
import { intlShape } from 'react-intl';
import LoginFlow from '../login/LoginFlow';
import TabbedApp from '../containers/TabbedApp';
import TabApp from '../containers/TabApp';
import { gradientTop } from '../Colors';
import { setup as setupNotifications } from '../notifications/setup';
import { processUrl } from '../actions';
import type { State } from '../reducers/user';

class App extends React.Component {
  props: {
    processUrl: (url: string) => void,
    userState: State,
  };

  constructor(props, context) {
    super(props, context);
    (this: any).componentDidMount = this.componentDidMount.bind(this);
    (this: any).handleOpenURL = this.handleOpenURL.bind(this);
    setupNotifications(context.store.dispatch, context.intl);
  }

  componentDidMount() {
    AppState.addEventListener('change', this.handleAppStateChange);
    CodePush.sync({
      installMode: CodePush.InstallMode.ON_NEXT_RESUME,
      minimumBackgroundDuration: 60 * 5,
    });
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
      CodePush.sync({
        installMode: CodePush.InstallMode.ON_NEXT_RESUME,
        minimumBackgroundDuration: 60 * 5,
      });
    }
  }

  render() {
    if (
      !this.props.userState.isLoggedIn &&
      !this.props.userState.hasSkippedLogin
    ) {
      return <LoginFlow />;
    }
    return (
      <View style={styles.container}>
        <StatusBar
          translucent={false}
          backgroundColor={gradientTop}
          barStyle="light-content"
        />
        <TabApp />
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
    userState: store.user,
  }),
  dispatch => ({
    processUrl: event => dispatch(processUrl(event)),
  })
)(App);

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
