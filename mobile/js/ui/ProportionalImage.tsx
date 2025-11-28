/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Animated, Platform, StyleProp, View, ViewStyle } from 'react-native';

type Dimension = {
  width: number;
  height: number;
};

interface Props {
  originalWidth: number;
  originalHeight: number;
  style?: StyleProp<ViewStyle>;
  duration: number;
  resizeDirection: 'width' | 'height';
  initialDimensions?: Dimension;
  [key: string]: any;
}

interface State {
  dimensions?: Dimension;
  opacity: Animated.Value;
}

export default class ProportionalImage extends React.PureComponent<Props, State> {
  static defaultProps: Partial<Props> = {
    duration: 200,
    resizeDirection: 'height',
  };

  view?: View | null;

  constructor(props: Props) {
    super(props);
    let initialValue = 0;
    if (Platform.OS === 'android') {
      initialValue = 1.0;
    }
    this.state = {
      dimensions: this.props.initialDimensions,
      opacity: new Animated.Value(initialValue),
    };
    this.onLayout = this.onLayout.bind(this);
    this.onLoad = this.onLoad.bind(this);
  }

  onLayout(e: any) {
    const { nativeEvent } = e;
    const { layout } = nativeEvent;
    this.setState({
      dimensions: {
        width: layout.width,
        height: layout.height,
      },
    });
  }

  onLoad() {
    Animated.timing(this.state.opacity, {
      toValue: 1,
      duration: this.props.duration,
      useNativeDriver: true,
    }).start();
  }

  getComputedWidthHeight() {
    const { dimensions } = this.state;
    if (!dimensions) {
      return {};
    }
    const aspectRatio = this.props.originalWidth / this.props.originalHeight;
    if (this.props.resizeDirection === 'width') {
      return {
        height: dimensions.height,
        width: dimensions.height * aspectRatio,
      };
    } else {
      return {
        width: dimensions.width,
        height: dimensions.width / aspectRatio,
      };
    }
  }

  setNativeProps(nativeProps: any) {
    if (this.view) {
      (this.view as any).setNativeProps(nativeProps);
    }
  }

  render() {
    const resizedDimensions = this.getComputedWidthHeight();
    return (
      <View
        onLayout={this.onLayout}
        ref={x => {
          this.view = x;
        }}
        {...this.props}
      >
        <Animated.Image
          {...this.props}
          style={[
            { opacity: this.state.opacity, ...resizedDimensions },
            this.props.style,
          ]}
          onLoad={this.onLoad}
        />
      </View>
    );
  }
}
