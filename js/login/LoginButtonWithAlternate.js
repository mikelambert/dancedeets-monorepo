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
import {
  Button
} from '../ui';
import { Text } from '../ui';


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
    height: 125,
  },
  bottomLink: {
    color: 'white',
    fontWeight: 'normal',
    fontSize: 14,
  },
  bottomLinkBox: {
    top: 10,
  },
});
