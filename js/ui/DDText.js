/**
 * Copyright 2016 DanceDeets.
 *
 * @providesModule DDText
 * @flow
 */

'use strict';

import React from 'react';
import {Text as RealText} from 'react-native';
import {StyleSheet, Dimensions} from 'react-native';
import {default as RealAutolink} from 'react-native-autolink';

export function Text({style, ...props}: Object): ReactElement {
  return <RealText style={[styles.font, styles.text, style]} {...props} />;
}

export function Heading1({style, ...props}: Object): ReactElement {
  return <RealText style={[styles.font, styles.h1, style]} {...props} />;
}

export function Paragraph({style, ...props}: Object): ReactElement {
  return <RealText style={[styles.font, styles.p, style]} {...props} />;
}

export function Autolink({style, ...props}: Object): ReactElement {
  return <RealAutolink style={[styles.font, style]} {...props} />;
}

const scale = Dimensions.get('window').width / 375;

function normalize(size: number): number {
  return Math.round(scale * size);
}

export const defaultFont = {
  fontFamily: 'Ubuntu',
  fontWeight: '300',
  color: 'white',
};

const styles = StyleSheet.create({
  font: Object.assign({}, defaultFont),
  text: {
  },
  h1: {
    fontSize: normalize(24),
    lineHeight: normalize(27),
    fontWeight: 'bold',
    letterSpacing: -1,
  },
  p: {
    fontSize: normalize(15),
    lineHeight: normalize(23),
  },
});
