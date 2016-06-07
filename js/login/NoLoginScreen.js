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
import { Text } from '../ui';
import { linkColor } from '../Colors';

const NoLoginText =
`Almost all our dance events are
found when dancers like you log in.

Logging in shares your dance events
with DanceDeets, so our algorithm
can sort through everyone's events,
and share them with dancers everywhere.

But without any logged-in dancers,
we’d have nothing to share with you.

So please consider logging in,
to help us help your dance scene.

Otherwise, you're always able to use
our website without any login:
`;

export default class NoLoginScreen extends React.Component {
  render() {
    return (
      <View style={styles.container}>
        <Image
          style={[styles.container, styles.centerItems, styles.topAndBottom]}
          source={require('./images/Onboard4.jpg')}>
          <Text style={styles.topText}>{NoLoginText}
            <Text
              style={{color: linkColor}}
              onPress={() => this.props.onNoLogin('Text Link')}
              >http://www.dancedeets.com/</Text>
          </Text>
          <View style={[styles.centerItems, styles.bottomBox]}>
            <LoginButtonWithAlternate
              onLogin={this.props.onLogin}
              onNoLogin={() => this.props.onNoLogin('Bottom Button')}
              noLoginText="USE WEBSITE WITHOUT LOGIN"
              />
          </View>
        </Image>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  topAndBottom: {
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  topText: {
    top: 40,
    color: 'white',
    fontSize: 15,
  },
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    // Image's source contains explicit size, but we want
    // it to prefer flex: 1
    width: undefined,
    height: undefined,
  },
});
