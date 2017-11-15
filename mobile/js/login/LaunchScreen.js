/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { Image, Platform, StyleSheet } from 'react-native';

export default class LaunchScreen extends React.Component<{
  children: React.Node,
}> {
  render() {
    return (
      <Image
        style={styles.container}
        source={{
          uri: Platform.OS === 'ios' ? 'launch_screen.jpg' : 'launch_screen',
        }}
      >
        {this.props.children}
      </Image>
    );
  }
}

let styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    // Image's source contains explicit size, but we want
    // it to prefer flex: 1
    width: undefined,
    height: undefined,
  },
});
