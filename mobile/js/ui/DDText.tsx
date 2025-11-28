/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import {
  Platform,
  StyleProp,
  StyleSheet,
  Text as RealText,
  TextInput as RealTextInput,
  TextStyle,
} from 'react-native';
import RealAutolink from 'react-native-autolink';
import { semiNormalize } from '../ui/normalize';

export function Text({ style, ...props }: any) {
  return <RealText style={[styles.font, styles.text, style]} {...props} />;
}

export function DarkText({ style, ...props }: any) {
  return <RealText style={[styles.darkFont, styles.text, style]} {...props} />;
}

export function Heading1({ style, ...props }: any) {
  return <RealText style={[styles.font, styles.h1, style]} {...props} />;
}

export function Paragraph({ style, ...props }: any) {
  return <RealText style={[styles.font, styles.p, style]} {...props} />;
}

export function Autolink({ style, ...props }: any) {
  return <RealAutolink style={[styles.font, style]} {...props} />;
}

export function TextInput({ style, ...props }: any) {
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
  fontFamily: Platform.OS === 'android' ? 'Roboto' : undefined,
  fontWeight: '300' as const,
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
