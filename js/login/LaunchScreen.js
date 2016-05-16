/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Image,
  StyleSheet,
} from 'react-native';

export default class LaunchScreen extends React.Component {
  render() {
    return (
      <Image
        style={styles.container}
        source={require('./images/LaunchScreen.jpg')}>
        <Image
          style={styles.container}
          source={require('./images/LaunchScreenText.png')} />
      </Image>
    );
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
