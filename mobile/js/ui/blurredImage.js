/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Image, findNodeHandle, StyleSheet } from 'react-native';
import { BlurView } from 'react-native-blur';

export default class BlurredImage extends React.Component {
  props: Image.propTypes;

  state: {
    viewRef: any,
  };

  _imageRef: ?Image;

  constructor(props: Image.propTypes) {
    super(props);

    this.state = {
      viewRef: 0,
    };

    (this: any).imageLoaded = this.imageLoaded.bind(this);
  }

  imageLoaded() {
    this.setState({ viewRef: findNodeHandle(this._imageRef) });
  }

  render() {
    const { children, ...props } = this.props;
    return (
      <Image
        {...props}
        ref={x => (this._imageRef = x)}
        onLoadEnd={this.imageLoaded}
      >
        <BlurView
          // iOS props
          blurType="dark"
          blurAmount={30}
          // Android props
          blurRadius={15}
          downsampleFactor={5}
          overlayColor={'rgba(255, 255, 255, .25)'}
          style={styles.blurView}
          viewRef={this.state.viewRef}
        />
        {children}
      </Image>
    );
  }
}

const styles = StyleSheet.create({
  blurView: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    right: 0,
  },
});
