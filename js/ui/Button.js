/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

var { purpleColors, yellowColors, redColors } = require('../Colors');
var Image = require('Image');
var LinearGradient = require('react-native-linear-gradient');
var React = require('React');
var StyleSheet = require('StyleSheet');
var { Text } = require('./DDText');
var TouchableOpacity = require('TouchableOpacity');
var View = require('View');
import {
  normalize,
} from './normalize';

class Button extends React.Component {
  props: {
    icon: ?number;
    caption: string;
    style: any;
    onPress: () => void;
    size: 'small' | 'large';
    textStyle: any;
    color: 'purple' | 'color';
  };

  static defaultProps = {
    caption: '',
    icon: null,
    style: {},
    onPress: () => {},
    size: 'large',
    textStyle: {},
    color: 'purple',
  };

  render() {
    const caption = this.props.caption;
    let icon;
    if (this.props.icon) {
      icon = <Image source={this.props.icon} style={[caption ? styles.iconSpacing : {}, styles.iconSize]} />;
    }
    const size = this.props.size === 'small' ? styles.smallButton : styles.largeButton;
    let colors = null;
    if (this.props.color === 'purple') {
      colors = [purpleColors[1], purpleColors[2], purpleColors[2]];
    } else if (this.props.color === 'yellow') {
      colors = [yellowColors[1], yellowColors[4], yellowColors[4]];
    } else if (this.props.color === 'red') {
      colors = [redColors[0], redColors[1], redColors[1]];
    }
    const content = (
      <LinearGradient
        start={[0, 0]} end={[0, 1]}
        locations={[0.0, 0.7, 1.0]}
        colors={colors}
        style={[styles.button, size]}>
        {icon}
        <Text style={[styles.caption, this.props.textStyle]}>
          {caption}
        </Text>
      </LinearGradient>
    );
    return (
      <TouchableOpacity
        accessibilityTraits="button"
        onPress={this.props.onPress}
        activeOpacity={0.8}
        style={[this.props.style]}>
        {content}
      </TouchableOpacity>
    );
  }
}

var styles = StyleSheet.create({
  button: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
  },
  smallButton: {
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 5,
  },
  largeButton: {
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
  },
  iconSize: {
    width: normalize(18),
    height: normalize(18),
  },
  border: {
    borderWidth: 1,
    borderColor: 'white',
  },
  iconSpacing: {
    marginRight: 10,
  },
  caption: {
    letterSpacing: 1,
    fontSize: normalize(16),
    lineHeight: normalize(19),
    color: 'white',
  },
  secondaryCaption: {
    color: 'white',
  }
});

module.exports = Button;
