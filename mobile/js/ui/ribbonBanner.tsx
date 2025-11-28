/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { StyleProp, StyleSheet, View, ViewStyle } from 'react-native';
import { semiNormalize } from './normalize';
import { Text } from './DDText';

const fontSize = semiNormalize(18);
const degrees = 30;

interface Props {
  text: string;
  width: number;
  overlayBackgroundColor: string;
}

interface State {
  dimensions?: {
    width: number;
    height: number;
  };
}

export default class RibbonBanner extends React.Component<Props, State> {
  static defaultProps: Partial<Props> = {
    overlayBackgroundColor: '#00000044',
  };

  constructor(props: Props) {
    super(props);

    this.onLayout = this.onLayout.bind(this);

    this.state = { dimensions: undefined };
  }

  onLayout(e: any) {
    const { nativeEvent } = e;
    const layout = nativeEvent.layout;
    this.setState({
      dimensions: {
        width: layout.width,
        height: layout.height,
      },
    });
  }

  renderBanner() {
    const { dimensions } = this.state;
    if (!dimensions) {
      return null;
    }
    const divisor = Math.tan(degrees / 180 * Math.PI);
    const placement: any = {
      top: (dimensions.height - fontSize) / 2,
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
