/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { StyleSheet, View } from 'react-native';
import { semiNormalize } from './normalize';
import { Text } from './DDText';

const fontSize = semiNormalize(18);
const degrees = 30;

export default class RibbonBanner extends React.Component {
  static defaultProps = {
    overlayBackgroundColor: '#00000044',
  };

  props: {
    text: string,
    width: number,
    overlayBackgroundColor: string,
  };

  state: {
    dimensions: ?{
      width: number,
      height: number,
    },
  };

  constructor(props: Object) {
    super(props);

    (this: any).onLayout = this.onLayout.bind(this);

    this.state = { dimensions: null };
  }

  onLayout(e: SyntheticEvent) {
    const nativeEvent: any = e.nativeEvent;
    const layout = nativeEvent.layout;
    this.setState({
      dimensions: {
        width: layout.width,
        height: layout.height,
      },
    });
  }

  renderBanner() {
    const dimensions = this.state.dimensions;
    if (!dimensions) {
      return null;
    }
    const divisor = Math.tan(degrees / 180 * Math.PI);
    const placement = {
      // Easy to center this one vertically
      top: (dimensions.height - fontSize) / 2,
      // Use the tangent to figure out how much to offset horizontally from the left
      // To ensure that it basically touches the bottom-right corner at all times
      // But on small views, we don't want it going off to the right.
      // So only use this calculation to move things left, if we can. But clamp at 0.
      left: Math.min(
        0,
        -dimensions.width / 2 + dimensions.height / 2 / divisor
      ),
    };
    return (
      <View style={placement}>
        <View style={styles.redRibbon}>
          <Text style={[styles.redRibbonText]}>{this.props.text}</Text>
        </View>
      </View>
    );
  }

  render() {
    const overlayStyle = {
      backgroundColor: this.props.overlayBackgroundColor,
    };
    return (
      <View
        style={[styles.disabledOverlay, overlayStyle]}
        onLayout={this.onLayout}
      >
        {this.renderBanner()}
      </View>
    );
  }
}

const styles = StyleSheet.create({
  disabledOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    overflow: 'hidden',
  },
  redRibbon: {
    position: 'absolute',
    transform: [{ rotate: `-${degrees}deg` }],
    backgroundColor: '#c00',
    borderWidth: 0.5,
    left: -300,
    right: -300,

    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  redRibbonText: {
    fontSize,
  },
});
