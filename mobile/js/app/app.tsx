/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { AppState, Linking, StatusBar, StyleSheet, View } from 'react-native';
import CodePush from 'react-native-code-push';
import { connect } from 'react-redux';
import storeShape from 'react-redux/lib/utils/storeShape';
import { intlShape, IntlShape } from 'react-intl';
import LoginFlow from '../login/LoginFlow';
import TabApp from '../containers/TabApp';
import { gradientTop } from '../Colors';
import { setup as setupNotifications } from '../notifications/setup';
import { processUrl } from '../actions';
import { State } from '../reducers/user';
import { Store } from 'redux';

interface Props {
  processUrl: (url: string) => void;
  userState: State;
}

interface Context {
  store: Store;
  intl: IntlShape;
}

class App extends React.Component<Props> {
  static contextTypes = {
    store: storeShape,
    intl: intlShape,
  };

  context!: Context;

  constructor(props: Props, context: Context) {
    super(props, context);
    this.componentDidMount = this.componentDidMount.bind(this);
    this.handleOpenURL = this.handleOpenURL.bind(this);
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

  handleOpenURL = (event: { url: string }) => {
    this.props.processUrl(event.url);
  };

  handleAppStateChange = (appState: string) => {
    if (appState === 'active') {
      CodePush.sync({
        installMode: CodePush.InstallMode.ON_NEXT_RESUME,
        minimumBackgroundDuration: 60 * 5,
      });
    }
  };

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

export default connect(
  (store: any) => ({
    userState: store.user,
  }),
  (dispatch: any) => ({
    processUrl: (event: string) => dispatch(processUrl(event)),
  })
)(App);

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
