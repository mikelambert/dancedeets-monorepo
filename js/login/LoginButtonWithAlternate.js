/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';
import { yellowColors } from '../Colors';
import {
  Button,
  Text,
} from '../ui';
import normalize from '../ui/normalize';

export default class LoginButtonWithAlternate extends React.Component {
  props: {
    noLoginText: string,
    onLogin: () => void,
    onNoLogin: () => void,
  };

  render() {
    return (
      <View style={[styles.centerItems, styles.bottomBox]}>
        <Button
          icon={require('./icons/facebook.png')}
          caption="Login with Facebook"
          onPress={this.props.onLogin}
          textStyle={styles.buttonStyle}
        />
        <TouchableOpacity
          style={styles.bottomLinkBox}
          activeOpacity={0.7}
          onPress={this.props.onNoLogin}
        >
          <Text style={styles.bottomLink}>{this.props.noLoginText}</Text>
        </TouchableOpacity>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  bottomBox: {
    alignItems: 'center',
    height: normalize(100),
  },
  bottomLink: {
    fontWeight: 'normal',
    color: yellowColors[0],
  },
  bottomLinkBox: {
    top: normalize(15),
  },
  buttonStyle: {
    fontSize: normalize(14),
    lineHeight: normalize(18),
  },
});
