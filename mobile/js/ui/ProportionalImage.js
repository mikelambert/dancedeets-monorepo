/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
import * as React from 'react';
import { Animated, Platform, View } from 'react-native';

type Dimension = {
  width: number,
  height: number,
};

type Props = {
  originalWidth: number,
  originalHeight: number,
  style?: any,
  duration: number,
  resizeDirection: 'width' | 'height',
  initialDimensions?: Dimension,
};

export default class ProportionalImage extends React.PureComponent<
  Props,
  {
    dimensions: ?Dimension,
    opacity: any,
  }
> {
  static defaultProps = {
    duration: 200,
    resizeDirection: 'height',
  };

  constructor(props: Props) {
    super(props);
    let initialValue = 0;
    // TODO(android): It seems that onLoad/onLoadEnd doesn't register on android
    // So we disable this animation altogether
    if (Platform.OS === 'android') {
      initialValue = 1.0;
    }
    this.state = {
      dimensions: this.props.initialDimensions,
      opacity: new Animated.Value(initialValue),
    };
    (this: any).onLayout = this.onLayout.bind(this);
    (this: any).onLoad = this.onLoad.bind(this);
  }

  // onLayout will only get called once when this view is re-used.
  // So don't do any computations that are dependent on this.props here.
  // Instead just save the necessary bits of state and do the computation elsewhere.
  onLayout(e: SyntheticEvent<>) {
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

  setNativeProps(nativeProps: Object) {
    this.view.setNativeProps(nativeProps);
  }

  view: ?View;

  render() {
    const resizedDimensions = this.getComputedWidthHeight();
    // We catch the onLayout in the view, find the size, then resize the child (before it is laid out?)
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
