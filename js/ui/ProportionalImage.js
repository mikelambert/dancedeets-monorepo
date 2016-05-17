/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
'use strict';

import React from 'react';
import {
  Image,
  View,
} from 'react-native';

type Props = {
  originalWidth: number,
  originalHeight: number,
  style?: any,
};

export default class ProportionalImage extends React.Component {
  props: Props;

  state: {
    style: {height: number} | {},
  };

  _root: { setNativeProps(props: Object): void };

  constructor(props: Props) {
    super(props);
    this.state = {
      style: {}
    };
    (this: any).onLayout = this.onLayout.bind(this);
  }

  setNativeProps(nativeProps: Object) {
    this._root.setNativeProps(nativeProps);
  }

  onLayout(e: SyntheticEvent) {
    const nativeEvent: any = e.nativeEvent;
    const layout = nativeEvent.layout;
    const aspectRatio = this.props.originalWidth / this.props.originalHeight;
    const measuredHeight = layout.width / aspectRatio;
    const currentHeight = layout.height;

    if (measuredHeight !== currentHeight) {
      this.setState({
        style: {
          height: measuredHeight
        }
      });
    }
  }

  render() {
    // We catch the onLayout in the view, find the size, then resize the child (before it is laid out?)
    return (
      <View
        onLayout={this.onLayout}
        ref={function (component) { this._root = component; }}
        {...this.props}
        >
        <Image
          {...this.props}
          style={[this.props.style, this.state.style]}
        />
      </View>
    );
  }
}
