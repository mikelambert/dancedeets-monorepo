/**
 * Copyright 2016 DanceDeets.
 *
 * @providesModule DDText
 * @flow
 */

'use strict';

import React from 'react';
import {
  Text as RealText,
  StyleSheet,
} from 'react-native';
import {default as RealAutolink} from 'react-native-autolink';
import {
  semiNormalize,
} from '../ui/normalize';

export function Text({style, ...props}: Object): ReactElement<RealText> {
  return <RealText style={[styles.font, styles.text, style]} {...props} />;
}

export function Heading1({style, ...props}: Object): ReactElement<RealText> {
  return <RealText style={[styles.font, styles.h1, style]} {...props} />;
}

export function Paragraph({style, ...props}: Object): ReactElement<RealText> {
  return <RealText style={[styles.font, styles.p, style]} {...props} />;
}

export function Autolink({style, ...props}: Object): ReactElement<RealAutolink> {
  return <RealAutolink style={[styles.font, style]} {...props} />;
}

export const defaultFont = {
  // Disable this due to alignment issues:
  // https://github.com/facebook/react-native/issues/8540
  // fontFamily: 'Ubuntu',
  fontWeight: '300',
  color: 'white',
  backgroundColor: 'transparent',
};

const styles = StyleSheet.create({
  font: Object.assign({}, defaultFont),
  text: {
    fontSize: semiNormalize(15),
    lineHeight: semiNormalize(21),
  },
  h1: {
    fontSize: semiNormalize(24),
    lineHeight: semiNormalize(27),
    fontWeight: 'bold',
    letterSpacing: -1,
  },
  p: {
    fontSize: semiNormalize(15),
    lineHeight: semiNormalize(23),
  },
});
