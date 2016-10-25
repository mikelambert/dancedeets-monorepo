/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Image,
  StyleSheet,
  View,
} from 'react-native';
import LoginButtonWithAlternate from './LoginButtonWithAlternate';
import {
  normalize,
  Text,
} from '../ui';
import { linkColor } from '../Colors';
import {
  defineMessages,
  injectIntl,
} from 'react-intl';

const messages = defineMessages({
  useWebsite: {
    id: 'tutorial.nologin.website',
    defaultMessage: 'Use website without login',
    description: 'Link to use the website without logging into the app',
  },
  'useWithoutLogin': {
    id: 'tutorial.nologin.usewithoutlogin',
    defaultMessage: 'Use without login',
    description: 'Use the app without FB login',
  },
  loginJustification: {
    id: 'tutorial.nologin.justification',
    defaultMessage: `Almost all our dance events are
found when dancers like you log in.

Logging in shares your dance events
with DanceDeets, so our algorithm
can sort through everyone's events,
and share them with dancers everywhere.

But without any logged-in dancers,
we’d have nothing to share with you.

So please consider logging in,
to help us help your dance scene.
`,
    description: 'A long explanation of why we need login',
  }
});

class _NoLoginScreen extends React.Component {
  render() {
    return (
      <View style={styles.container}>
        <Image
          style={[styles.container, styles.topAndBottom]}
          source={require('./images/Onboard4.jpg')}>
          <Text style={[styles.topText, styles.text]}>{this.props.intl.formatMessage(messages.loginJustification)}</Text>
          <LoginButtonWithAlternate
            onLogin={this.props.onLogin}
            onNoLogin={() => this.props.onNoLogin('Bottom Button')}
            noLoginText={this.props.intl.formatMessage(messages.useWithoutLogin)}
            />
        </Image>
      </View>
    );
  }
}
export default injectIntl(_NoLoginScreen);

const styles = StyleSheet.create({
  topAndBottom: {
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  text: {
    fontSize: normalize(15),
    lineHeight: normalize(18),
  },
  topText: {
    top: 40,
    color: 'white',
  },
  container: {
    flex: 1,
    backgroundColor: 'black',
    // Image's source contains explicit size, but we want
    // it to prefer flex: 1
    width: undefined,
    height: undefined,
  },
});
