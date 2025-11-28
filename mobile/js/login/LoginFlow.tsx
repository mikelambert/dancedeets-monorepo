/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Platform, View } from 'react-native';
import { connect } from 'react-redux';
import { Dispatch } from 'redux';
import LaunchScreen from './LaunchScreen';
import OnboardingFlow from './OnboardingFlow';
import { autoLoginAtStartup } from '../actions';

interface Props {
  // Self-managed props
  isOnboarding: boolean;
  autoLoginAtStartup: () => void;
}

class LoginFlow extends React.Component<Props> {
  componentDidMount() {
    this.props.autoLoginAtStartup();
  }

  render() {
    if (this.props.isOnboarding) {
      return <OnboardingFlow />;
    }

    // This is used when we're starting up, before we know
    // whether to drop them into the <OnboardingFlow/> process.

    if (Platform.OS === 'ios') {
      // On iOS, we can do some easy scale-to-fit-window on our launch screen,
      // so let's use our good launch image that can match the LaunchScreen.xib.
      return <LaunchScreen />;
    } else if (Platform.OS === 'android') {
      // On Android, background drawables are limited, and we can really only center things.
      // So instead, let's draw a no-op, and let the application background show through,
      // which ends up being a continuation of our launch screen as the app loads.
      return <View />;
    } else {
      return null;
    }
  }
}
export default connect(
  (state: any) => ({
    isOnboarding: state.user.isOnboarding,
  }),
  (dispatch: Dispatch) => ({
    autoLoginAtStartup: () => autoLoginAtStartup(dispatch),
  })
)(LoginFlow);
