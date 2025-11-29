/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { AppState, Linking, StatusBar, StyleSheet, View, NativeEventSubscription } from 'react-native';
import type { EmitterSubscription } from 'react-native';
import CodePush from 'react-native-code-push';
import { connect } from 'react-redux';
import { injectIntl, WrappedComponentProps } from 'react-intl';
import LoginFlow from '../login/LoginFlow';
import TabApp from '../containers/TabApp';
import { gradientTop } from '../Colors';
import { setup as setupNotifications } from '../notifications/setup';
import { processUrl } from '../actions';
import { State } from '../reducers/user';
import { Dispatch } from 'redux';

interface StateProps {
  userState: State;
}

interface DispatchProps {
  processUrl: (url: string) => void;
  dispatch: Dispatch;
}

type Props = StateProps & DispatchProps & WrappedComponentProps;

class App extends React.Component<Props> {
  private notificationsInitialized = false;
  private appStateSubscription: NativeEventSubscription | null = null;
  private linkingSubscription: EmitterSubscription | null = null;

  constructor(props: Props) {
    super(props);
    this.handleOpenURL = this.handleOpenURL.bind(this);
  }

  componentDidMount() {
    // Initialize notifications with dispatch and intl from props
    if (!this.notificationsInitialized) {
      setupNotifications(this.props.dispatch, this.props.intl);
      this.notificationsInitialized = true;
    }

    // In RN 0.72+, addEventListener returns a subscription to remove
    this.appStateSubscription = AppState.addEventListener('change', this.handleAppStateChange);
    CodePush.sync({
      installMode: CodePush.InstallMode.ON_NEXT_RESUME,
      minimumBackgroundDuration: 60 * 5,
    });
    this.linkingSubscription = Linking.addEventListener('url', this.handleOpenURL);
  }

  componentWillUnmount() {
    // Use subscription.remove() instead of deprecated removeEventListener
    this.appStateSubscription?.remove();
    this.linkingSubscription?.remove();
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

// Use injectIntl to get intl prop, and connect for Redux state/dispatch
const mapStateToProps = (state: any): StateProps => ({
  userState: state.user,
});

const mapDispatchToProps = (dispatch: Dispatch): DispatchProps => ({
  processUrl: (url: string) => dispatch(processUrl(url) as any),
  dispatch,
});

export default connect(mapStateToProps, mapDispatchToProps)(injectIntl(App));

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
