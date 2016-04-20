/**
 * Copyright 2016 DanceDeets.
 * @flow
 */
'use strict';

import StatusBarIOS from 'StatusBarIOS';
import React, {
  Image,
  StyleSheet,
  TouchableWithoutFeedback,
} from 'react-native';
import OnboardingFlow from './OnboardingFlow';
// TODO: Maybe when we have styles, use a DDText.js file?
// TODO: import LoginButton from '../common/LoginButton';
import { connect } from 'react-redux';
import { autoLoginAtStartup } from './logic';

function select(store) {
  return {
    isLoggedIn: store.user.isLoggedIn,
    isOnboarding: store.user.isOnboarding,
  };
}


class SplashScreen extends React.Component {


  state: {
  };

  constructor(props) {
    super(props);
    this.state = {
    };
  }

  componentDidMount() {
    StatusBarIOS && StatusBarIOS.setStyle('default');
    autoLoginAtStartup(this.props.dispatch);
  }

  render() {
    if (this.props.isOnboarding) {
      return <OnboardingFlow />;
    }
    return (
      <TouchableWithoutFeedback
        //onPress={() => this.props.dispatch(skipLogin())}>
        >
        <Image
          style={styles.container}
          source={require('./images/LaunchScreen.jpg')}>
          <Image
            style={styles.container}
            source={require('./images/LaunchScreenText.png')} />
        </Image>
      </TouchableWithoutFeedback>
    );
    //<LoginButton source="First screen" />
  }
}
export default connect(select)(SplashScreen);


var styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    // Image's source contains explicit size, but we want
    // it to prefer flex: 1
    width: undefined,
    height: undefined,
  }
});
