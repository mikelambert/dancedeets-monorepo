/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { connect } from 'react-redux';
import TutorialScreen from './TutorialScreen';
import NoLoginScreen from './NoLoginScreen';
import { loginButtonPressed, skipLogin } from '../actions';
import { track } from '../store/track';
import type { Dispatch } from '../actions/types';

type ScreenState = 'CAROUSEL' | 'NO_LOGIN';

interface Props {
  onLogin: () => void;
  skipLogin: () => void;
}

interface State {
  screen: ScreenState;
}

class OnboardingFlow extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      screen: 'CAROUSEL',
    };
    this.onDontWantLoginPressed = this.onDontWantLoginPressed.bind(this);
    this.onSkipLogin = this.onSkipLogin.bind(this);
  }

  onDontWantLoginPressed() {
    track('Login - Without Facebook');
    this.setState({ ...this.state, screen: 'NO_LOGIN' });
  }

  onSkipLogin() {
    track('Login - Skip Login');
    this.props.skipLogin();
  }

  render() {
    if (this.state.screen === 'CAROUSEL') {
      return (
        <TutorialScreen
          onLogin={async () => {
            track('Login - FBLogin Button Pressed', { Button: 'First Screen' });
            await this.props.onLogin();
          }}
          onNoLogin={this.onDontWantLoginPressed}
        />
      );
    } else if (this.state.screen === 'NO_LOGIN') {
      return (
        <NoLoginScreen
          onLogin={async () => {
            track('Login - FBLogin Button Pressed', {
              Button: 'Second Screen',
            });
            await this.props.onLogin();
          }}
          onNoLogin={this.onSkipLogin}
        />
      );
    } else {
      console.error('Unknown state screen: ', this.state.screen);
      return null;
    }
  }
}

export default connect(null, (dispatch: Dispatch) => ({
  onLogin: async () => await loginButtonPressed(dispatch),
  skipLogin: () => dispatch(skipLogin()),
}))(OnboardingFlow);
