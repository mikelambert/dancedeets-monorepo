/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
import React from 'react';
import { Animated, View } from 'react-native';
import SyntheticEvent from 'react-native/Libraries/Renderer/src/renderers/shared/shared/event/SyntheticEvent';

type Props = {
  originalWidth: number,
  originalHeight: number,
  style?: any,
  duration: number,
  resizeDirection: 'width' | 'height',
  initialDimensions?: {
    width: number,
    height: number,
  },
};

export default class ProportionalImage extends React.Component {
  static defaultProps = {
    duration: 200,
    resizeDirection: 'height',
  };

  props: Props;

  state: {
    dimensions: ?{
      width: number,
      height: number,
    },
    opacity: any,
  };

  constructor(props: Props) {
    super(props);
    this.state = {
      dimensions: this.props.initialDimensions,
      opacity: new Animated.Value(0),
    };
    (this: any).onLayout = this.onLayout.bind(this);
    (this: any).onLoad = this.onLoad.bind(this);
  }

  // onLayout will only get called once when this view is re-used.
  // So don't do any computations that are dependent on this.props here.
  // Instead just save the necessary bits of state and do the computation elsewhere.
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

  onLoad() {
    Animated.timing(this.state.opacity, {
      toValue: 1,
      duration: this.props.duration,
    }).start();
  }

  getComputedWidthHeight() {
    const dimensions = this.state.dimensions;
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

  view: View;

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
