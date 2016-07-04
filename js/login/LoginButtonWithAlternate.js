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
  normalize,
  Text,
} from '../ui';
import {
  defineMessages,
  injectIntl,
  intlShape,
} from 'react-intl';

const messages = defineMessages({
  loginButton: {
    id: 'tutorial.login',
    defaultMessage: 'Login with Facebook',
    description: 'Login button',
  },
});

class _LoginButtonWithAlternate extends React.Component {
  props: {
    noLoginText: string,
    onLogin: () => void,
    onNoLogin: () => void,
    intl: intlShape.isRequired,
  };

  render() {
    return (
      <View style={[styles.centerItems, styles.bottomBox]}>
        <Button
          icon={require('./icons/facebook.png')}
          caption={this.props.intl.formatMessage(messages.loginButton)}
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
export default injectIntl(_LoginButtonWithAlternate);

const styles = StyleSheet.create({
  bottomBox: {
    alignItems: 'center',
    height: normalize(130),
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
