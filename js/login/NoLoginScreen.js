/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  Image,
  StyleSheet,
  View,
} from 'react-native';
import LoginButtonWithAlternate from './LoginButtonWithAlternate';
import { Text } from '../ui';

const NoLoginText =
`Almost all our dance events are
found when dancers like you log in.

Logging in shares your dance events
with DanceDeets, so our algorithm
can sort through everyone's events,
and share them with dancers everywhere.

But without any logged-in dancers,
we’d have nothing to share,
and promoting your events gets harder.

So please consider logging in,
to help us help your dance scene.

But if not, you're always able to use
our website without any login:

http://www.dancedeets.com/
`;

export default class NoLoginScreen extends React.Component {
  render() {
    return (
      <View style={styles.container}>
        <Image
          style={[styles.container, styles.centerItems, styles.topAndBottom]}
          source={require('./images/Onboard4.jpg')}>
          <Text style={styles.topText}>{NoLoginText}</Text>
          <View style={[styles.centerItems, styles.bottomBox]}>
            <LoginButtonWithAlternate
              onLogin={this.props.onLogin}
              onNoLogin={this.props.onNoLogin}
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
