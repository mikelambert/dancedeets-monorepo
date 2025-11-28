/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { StyleProp, View, ViewStyle } from 'react-native';

interface HorizontalViewProps {
  style?: StyleProp<ViewStyle>;
  children?: React.ReactNode;
  [key: string]: any;
}

export function HorizontalView({ style, ...props }: HorizontalViewProps) {
  return <View style={[{ flexDirection: 'row' }, style]} {...props} />;
}
