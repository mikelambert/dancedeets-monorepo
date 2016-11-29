/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import { View } from 'react-native';

export function HorizontalView({style, ...props}: Object): ReactElement<View> {
  return <View style={[{flexDirection: 'row'}, style]} {...props} />;
}
