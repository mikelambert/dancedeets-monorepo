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
  semiNormalize,
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

  state: {
    enabled: boolean,
  };

  constructor(props) {
    super(props);
    this.state = {enabled: true};
  }

  render() {
    return (
      <View style={styles.bottomBox}>
        <Button
          icon={require('./icons/facebook.png')}
          caption={this.props.intl.formatMessage(messages.loginButton)}
          onPress={async () => {
            this.setState({enabled: false});
            await this.props.onLogin();
            this.setState({enabled: true});
          }}
          enabled={this.state.enabled}
          textStyle={styles.buttonStyle}
          testID="loginButton"
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
    height: semiNormalize(120),
  },
  bottomLink: {
    fontWeight: 'normal',
    color: yellowColors[0],
  },
  bottomLinkBox: {
    top: semiNormalize(15),
  },
  buttonStyle: {
    fontSize: normalize(14),
    lineHeight: normalize(18),
  },
});
