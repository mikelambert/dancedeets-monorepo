/**
 * Copyright 2016 DanceDeets.
 *
 * @providesModule F8Text
 * @flow
 */

'use strict';

import React, {StyleSheet, Dimensions} from 'react-native';
import RealAutoLink from 'react-native-autolink';

export function Text({style, ...props}: Object): ReactElement {
  return <React.Text style={[styles.font, styles.text, style]} {...props} />;
}

export function Heading1({style, ...props}: Object): ReactElement {
  return <React.Text style={[styles.font, styles.h1, style]} {...props} />;
}

export function Paragraph({style, ...props}: Object): ReactElement {
  return <React.Text style={[styles.font, styles.p, style]} {...props} />;
}

export function AutoLink({style, ...props}: Object): ReactElement {
  return <RealAutoLink style={[styles.font, style]} {...props} />;
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
