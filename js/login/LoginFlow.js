/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Platform,
  View,
} from 'react-native';
import LaunchScreen from './LaunchScreen';
import OnboardingFlow from './OnboardingFlow';
import { connect } from 'react-redux';
import { autoLoginAtStartup } from '../actions';

class LoginFlow extends React.Component {
  constructor(props) {
    super(props);
  }

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
    }
  }
}
export default connect(
  (state) => ({
    isOnboarding: state.user.isOnboarding,
  }),
  (dispatch) => ({
    autoLoginAtStartup: () => autoLoginAtStartup(dispatch),
  }),
)(LoginFlow);

