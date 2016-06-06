/**
 * Copyright DanceDeets.
 * @providesModule LoginButton
 * @flow
 */

'use strict';

import * as Colors from '../Colors';
import LinearGradient from 'react-native-linear-gradient';
import React from 'react';
import {
  Image,
  StyleSheet,
  TouchableOpacity,
  View
} from 'react-native';
import { Text } from '../ui';
import { gradientBottom, gradientTop } from '../Colors';

export default class LoginButton extends React.Component {
  props: {
    type: 'primary' | 'secondary' | 'bordered';
    icon: number;
    caption: string;
    style?: any;
    onPress: () => void;
  };

  render() {
    const caption = this.props.caption.toUpperCase();
    let icon = null;
    if (this.props.icon) {
      icon = <Image source={this.props.icon} style={styles.icon} />;
    }
    let content;
    if (this.props.type === 'primary' || this.props.type === undefined) {
      content = (
        <LinearGradient
          start={[0.0, 0.0]} end={[0.0, 1]}
          colors={[gradientBottom, gradientTop]}
          style={[styles.button, styles.primaryButton]}>
          {icon}
          <Text style={[styles.caption, styles.primaryCaption]}>
            {caption}
          </Text>
        </LinearGradient>
      );
    } else {
      var border = this.props.type === 'bordered' && styles.border;
      content = (
        <View style={[styles.button, border]}>
          {icon}
          <Text style={[styles.caption, styles.secondaryCaption]}>
            {caption}
          </Text>
        </View>
      );
    }
    return (
      <TouchableOpacity
        accessibilityTraits="button"
        onPress={this.props.onPress}
        activeOpacity={0.8}
        style={[styles.container, this.props.style]}>
        {content}
      </TouchableOpacity>
    );
  }
}

const HEIGHT = 50;

var styles = StyleSheet.create({
  container: {
    // borderRadius: HEIGHT / 2,
    // borderWidth: 1 / PixelRatio.get(),
  },
  button: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 25,
    paddingVertical: 15,
  },
  border: {
    borderWidth: 1,
    borderColor: Colors.lightText,
    borderRadius: HEIGHT / 2,
  },
  primaryButton: {
    borderRadius: HEIGHT / 2,
    backgroundColor: 'transparent',
  },
  icon: {
    marginRight: 12,
  },
  caption: {
    letterSpacing: 1,
    fontSize: 13,
  },
  primaryCaption: {
    color: 'white',
  },
  secondaryCaption: {
    color: Colors.lightText,
  }
});
