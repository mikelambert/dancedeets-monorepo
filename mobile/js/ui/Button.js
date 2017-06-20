/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import LinearGradient from 'react-native-linear-gradient';
import React from 'react';
import {
  ActivityIndicator,
  Image,
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';
import { purpleColors, yellowColors, redColors, greenColors } from '../Colors';
import { HorizontalView } from './Misc';
import { Text } from './DDText';
import { semiNormalize } from './normalize';

type Props = {
  icon: ?number,
  iconView: ?React.Element<*>,
  caption: string,
  style: any,
  onPress: () => Promise<void> | void,
  size: 'small' | 'large',
  textStyle: any,
  color:
    | 'translucent'
    | 'purple'
    | 'purple-gradient'
    | 'yellow'
    | 'red'
    | 'green',
  testID: ?string,
  isLoading: boolean,
  enabled: ?boolean,
  activityIndicatorColor: string,
};

class Button extends React.Component {
  static defaultProps: Props = {
    caption: '',
    icon: null,
    iconView: null,
    style: {},
    onPress: () => {},
    size: 'large',
    textStyle: {},
    color: 'translucent',
    testID: null,
    isLoading: false,
    enabled: true,
    activityIndicatorColor: 'white',
  };

  props: Props;

  renderRealContent() {
    const caption = this.props.caption;
    let icon = this.props.iconView;
    if (this.props.icon) {
      icon = (
        <Image
          source={this.props.icon}
          style={[caption ? styles.iconSpacing : {}, styles.iconSize]}
        />
      );
    }
    const content = (
      <HorizontalView>
        {icon}
        <Text style={[styles.caption, this.props.textStyle]}>
          {caption}
        </Text>
      </HorizontalView>
    );
    return content;
  }

  renderContent() {
    let contentOpacity = 1.0;
    let activityIndicator = null;
    if (this.props.isLoading) {
      activityIndicator = (
        <View style={styles.spinnerContainer}>
          <ActivityIndicator
            animating
            size="small"
            color={this.props.activityIndicatorColor}
          />
        </View>
      );
      contentOpacity = 0;
    }
    return (
      <View>
        {activityIndicator}
        <View style={{ opacity: contentOpacity }}>
          {this.renderRealContent()}
        </View>
      </View>
    );
  }

  render() {
    const size = this.props.size === 'small'
      ? styles.smallButton
      : styles.largeButton;

    let buttonContents = null;
    if (this.props.color === 'translucent') {
      buttonContents = (
        <View style={[styles.regularButton, styles.translucentButton]}>
          {this.renderContent()}
        </View>
      );
    } else if (this.props.color === 'purple') {
      buttonContents = (
        <View style={[styles.regularButton, styles.purpleButton]}>
          {this.renderContent()}
        </View>
      );
    } else {
      let colors = null;
      if (this.props.color === 'purple-gradient') {
        colors = [purpleColors[1], purpleColors[3], purpleColors[3]];
      } else if (this.props.color === 'yellow') {
        colors = [yellowColors[1], yellowColors[4], yellowColors[4]];
      } else if (this.props.color === 'red') {
        colors = [redColors[0], redColors[1], redColors[1]];
      } else if (this.props.color === 'green') {
        colors = [greenColors[0], greenColors[1], greenColors[1]];
      }
      buttonContents = (
        <LinearGradient
          start={{ x: 0.0, y: 0.0 }}
          end={{ x: 0.0, y: 1.0 }}
          locations={[0.0, 0.7, 1.0]}
          colors={colors}
          style={[styles.button, size]}
        >
          {this.renderContent()}
        </LinearGradient>
      );
    }
    if (this.props.enabled) {
      return (
        <TouchableOpacity
          accessibilityTraits="button"
          onPress={this.props.onPress}
          activeOpacity={0.8}
          style={[this.props.style]}
          testID={this.props.testID}
        >
          {buttonContents}
        </TouchableOpacity>
      );
    } else {
      return <View>{buttonContents}</View>;
    }
  }
}

let styles = StyleSheet.create({
  regularButton: {
    padding: 5,
  },
  translucentButton: {
    borderColor: purpleColors[0],
    borderWidth: 1,
    borderRadius: 5,
  },
  purpleButton: {
    borderColor: purpleColors[2],
    borderWidth: 1,
    borderRadius: 5,
    backgroundColor: purpleColors[3],
  },
  button: {
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
    width: semiNormalize(18),
    height: semiNormalize(18),
  },
  spinnerContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
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
    fontSize: semiNormalize(16),
    lineHeight: semiNormalize(19),
    color: 'white',
  },
  secondaryCaption: {
    color: 'white',
  },
});

module.exports = Button;
