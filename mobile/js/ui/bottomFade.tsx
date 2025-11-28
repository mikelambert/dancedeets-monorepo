/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { StyleProp, StyleSheet, ViewStyle } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';

interface BottomFadeProps {
  style?: StyleProp<ViewStyle>;
  height?: number;
  [key: string]: any;
}

export default function BottomFade({
  style,
  height = 100,
  ...props
}: BottomFadeProps) {
  return (
    <LinearGradient
      start={{ x: 0.0, y: 0.0 }}
      end={{ x: 0.0, y: 1.0 }}
      locations={[0.0, 0.8, 1.0]}
      colors={['#00000000', '#000000CC', '#000000CC']}
      style={[styles.bottomFade, style, { height }]}
      {...props}
    />
  );
}

const styles = StyleSheet.create({
  bottomFade: {
    position: 'absolute',
    flex: 1,
    bottom: 0,
    left: 0,
    right: 0,
  },
});
