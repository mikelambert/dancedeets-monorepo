/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { ImageBackground, Platform, StyleSheet } from 'react-native';

interface Props {
  children?: React.ReactNode;
}

export default class LaunchScreen extends React.Component<Props> {
  render() {
    return (
      <ImageBackground
        style={styles.container}
        source={{
          uri: Platform.OS === 'ios' ? 'launch_screen.jpg' : 'launch_screen',
        }}
      >
        {this.props.children}
      </ImageBackground>
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
