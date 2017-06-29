/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Platform,
  Text as RealText,
  TextInput as RealTextInput,
  StyleSheet,
} from 'react-native';
import RealAutolink from 'react-native-autolink';
import { semiNormalize } from '../ui/normalize';

export function Text({ style, ...props }: Object): React.Element<RealText> {
  return <RealText style={[styles.font, styles.text, style]} {...props} />;
}

export function DarkText({ style, ...props }: Object): React.Element<RealText> {
  return <RealText style={[styles.darkFont, styles.text, style]} {...props} />;
}

export function Heading1({ style, ...props }: Object): React.Element<RealText> {
  return <RealText style={[styles.font, styles.h1, style]} {...props} />;
}

export function Paragraph({
  style,
  ...props
}: Object): React.Element<RealText> {
  return <RealText style={[styles.font, styles.p, style]} {...props} />;
}

export function Autolink({ style, ...props }: Object): RealAutolink {
  return <RealAutolink style={[styles.font, style]} {...props} />;
}

export function TextInput({ style, ...props }: Object): TextInput {
  return (
    <RealTextInput
      {...props}
      style={[styles.font, style]}
      placeholderTextColor="rgba(255, 255, 255, 0.5)"
      keyboardAppearance="dark"
    />
  );
}

export const defaultFont = {
  // Disable this due to alignment issues on iOS:
  // https://github.com/facebook/react-native/issues/8540
  fontFamily: Platform.OS === 'android' ? 'Roboto' : null,
  fontWeight: '300',
  color: 'white',
  backgroundColor: 'transparent',
};

export const defaultDarkFont = {
  ...defaultFont,
  color: 'black',
};

const styles = StyleSheet.create({
  font: Object.assign({}, defaultFont),
  darkFont: Object.assign({}, defaultDarkFont),
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
