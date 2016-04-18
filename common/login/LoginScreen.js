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
import { Text } from 'react-native';
// TODO: import LoginButton from '../common/LoginButton';
import TouchableOpacity from 'TouchableOpacity';

import { skipLogin } from '../actions';
import { connect } from 'react-redux';

class LoginScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      anim: new Animated.Value(0),
    };
  }

  componentDidMount() {
    StatusBarIOS && StatusBarIOS.setStyle('default');
    Animated.timing(this.state.anim, {toValue: 3000, duration: 3000}).start();
  }

  render() {
    return (
      <Image
        style={styles.container}
        source={require('./images/LaunchScreen.jpg')}>
        <Image
          style={styles.container}
            source={require('./images/LaunchScreenText.png')}>
          <TouchableOpacity
            accessibilityLabel="Skip login"
            accessibilityTraits="button"
            style={styles.skip}
            onPress={() => this.props.dispatch(skipLogin())}>
            <Animated.Image
              style={this.fadeIn(2800)}
              source={require('./images/x.png')}
            />
          </TouchableOpacity>
          <View style={styles.section}>
            <Animated.Image
              style={this.fadeIn(0)}
              source={require('./images/devconf-logo.png')}
            />
          </View>
          <View style={styles.section}>
            <Animated.Text style={[styles.h1, this.fadeIn(700, -20)]}>
              code to
            </Animated.Text>
            <Animated.Text style={[styles.h1, {marginTop: -30}, this.fadeIn(700, 20)]}>
              connect
            </Animated.Text>
            <Animated.Text style={[styles.h2, this.fadeIn(1000, 10)]}>
              April 12 + 13 / Fort Mason Center
            </Animated.Text>
            <Animated.Text style={[styles.h3, this.fadeIn(1200, 10)]}>
              SAN FRANCISCO, CALIFORNIA
            </Animated.Text>
          </View>
          <Animated.View style={[styles.section, styles.last, this.fadeIn(2500, 20)]}>
            <Text style={styles.loginComment}>
              Use Facebook to find your friends at F8.
            </Text>
          </Animated.View>
        </Image>
      </Image>
    );
    //<LoginButton source="First screen" />
  }

  fadeIn(delay, from = 0) {
    const {anim} = this.state;
    return {
      opacity: anim.interpolate({
        inputRange: [delay, Math.min(delay + 500, 3000)],
        outputRange: [0, 1],
        extrapolate: 'clamp',
      }),
      transform: [{
        translateY: anim.interpolate({
          inputRange: [delay, Math.min(delay + 500, 3000)],
          outputRange: [from, 0],
          extrapolate: 'clamp',
        }),
      }],
    };
  }
}
export default connect(select)(LoginScreen);

const scale = Dimensions.get('window').width / 375;

var styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    padding: 26,
    // Image's source contains explicit size, but we want
    // it to prefer flex: 1
    width: undefined,
    height: undefined,
  },
  section: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  last: {
    justifyContent: 'flex-end',
  },
  h1: {
    fontWeight: 'bold',
    textAlign: 'center',
    fontSize: Math.round(74 * scale),
    color: F8Colors.darkText,
    backgroundColor: 'transparent',
  },
  h2: {
    textAlign: 'center',
    fontSize: 17,
    color: F8Colors.darkText,
    marginVertical: 20,
  },
  h3: {
    fontSize: 12,
    textAlign: 'center',
    color: F8Colors.lightText,
    letterSpacing: 1,
  },
  loginComment: {
    marginBottom: 14,
    fontSize: 12,
    color: F8Colors.darkText,
    textAlign: 'center',
  },
  skip: {
    position: 'absolute',
    right: 0,
    top: 20,
    padding: 15,
  },
});
