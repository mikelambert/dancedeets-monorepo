/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { connect } from 'react-redux';
import TutorialScreen from './TutorialScreen';
import NoLoginScreen from './NoLoginScreen';
import {
  loginButtonPressed,
  skipLogin,
} from '../actions';
import { track } from '../store/track';

type ScreenState = 'CAROUSEL' | 'NO_LOGIN';

class OnboardingFlow extends React.Component {
  props: {
    onLogin: () => void,
    skipLogin: () => void,
  };

  state: {
    screen: ScreenState,
  };

  constructor(props) {
    super(props);
    this.state = {
      screen: 'CAROUSEL',
    };
    (this: any).onDontWantLoginPressed = this.onDontWantLoginPressed.bind(this);
    (this: any).onSkipLogin = this.onSkipLogin.bind(this);
  }

  onDontWantLoginPressed() {
    track('Login - Without Facebook');
    this.setState({...this.state, screen: 'NO_LOGIN'});
  }

  onSkipLogin() {
    track('Login - Skip Login');
    this.props.skipLogin();
  }

  render() {
    if (this.state.screen === 'CAROUSEL') {
      return <TutorialScreen
        onLogin={async () => {
          track('Login - FBLogin Button Pressed', {'Button': 'First Screen'});
          await this.props.onLogin();
        }}
        onNoLogin={this.onDontWantLoginPressed}
      />;
    } else if (this.state.screen === 'NO_LOGIN') {
      return <NoLoginScreen
        onLogin={async () => {
          track('Login - FBLogin Button Pressed', {'Button': 'Second Screen'});
          await this.props.onLogin();
        }}
        onNoLogin={this.onSkipLogin}
        />;
    }
  }
}

export default connect(
    null,
    (dispatch) => ({
      onLogin: async () => await loginButtonPressed(dispatch),
      skipLogin: () => dispatch(skipLogin()),
    }),
)(OnboardingFlow);
