/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { View } from 'react-native';

export function HorizontalView({
  style,
  ...props
}: Object): React.Element<View> {
  return <View style={[{ flexDirection: 'row' }, style]} {...props} />;
}
