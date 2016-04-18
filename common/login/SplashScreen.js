/**
 * Copyright 2016 DanceDeets.
 * @flow
 */
'use strict';

import Animated from 'Animated';
import Dimensions from 'Dimensions';
import F8Colors from '../Colors';
import Image from 'Image';
import React from 'React';
import StatusBarIOS from 'StatusBarIOS';
import StyleSheet from 'StyleSheet';
import View from 'View';
// TODO: Maybe when we have styles, use a DDText.js file?
import Text from 'Text';
// TODO: import LoginButton from '../common/LoginButton';
import TouchableWithoutFeedback from 'TouchableWithoutFeedback';

import { skipLogin } from '../actions';
import { connect } from 'react-redux';

class SplashScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  componentDidMount() {
    StatusBarIOS && StatusBarIOS.setStyle('default');
  }

  render() {
    return (
      <TouchableWithoutFeedback
        onPress={() => this.props.dispatch(skipLogin())}>
        <Image
          style={styles.container}
          source={require('./images/LaunchScreen.jpg')}>
          <Image
            style={styles.container}
            source={require('./images/LaunchScreenText.png')}>
          </Image>
        </Image>
      </TouchableWithoutFeedback>
    );
    //<LoginButton source="First screen" />
  }
}
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

module.exports = connect()(SplashScreen);
