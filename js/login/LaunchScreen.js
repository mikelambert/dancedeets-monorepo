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
    console.log('launch screen!');
    return <Image
      style={styles.container}
      source={{uri: 'launch_screen.jpg', isStatic: true}}
      >
      {this.props.children}
    </Image>;
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
