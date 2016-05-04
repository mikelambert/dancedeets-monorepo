/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import LaunchScreen from './LaunchScreen';
import OnboardingFlow from './OnboardingFlow';
import { connect } from 'react-redux';
import { autoLoginAtStartup } from './logic';

function select(store) {
  return {
    isOnboarding: store.user.isOnboarding,
  };
}

class LoginFlow extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    autoLoginAtStartup(this.props.dispatch);
  }

  render() {
    if (this.props.isOnboarding) {
      return <OnboardingFlow />;
    } else {
      // This is used when we're starting up, before we know
      // whether to drop them into the <OnboardingFlow/> process.
      return <LaunchScreen />;
    }
  }
}
export default connect(select)(LoginFlow);

