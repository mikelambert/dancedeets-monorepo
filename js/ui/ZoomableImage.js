/**
 * Copyright 2016 Facebook, Inc.
 *
 * You are hereby granted a non-exclusive, worldwide, royalty-free license to
 * use, copy, modify, and distribute this software in source code or binary
 * form for use in connection with the web services and APIs provided by
 * Facebook.
 *
 * As with any software that integrates with the Facebook platform, your use
 * of this software is subject to the Facebook Developer Principles and
 * Policies [http://developers.facebook.com/policy/]. This copyright notice
 * shall be included in all copies or substantial portions of the software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE
 *
 * @flow
 */
'use strict';

import React from 'react';
import {
  Dimensions,
  Image,
  Platform,
  ScrollView,
  StyleSheet,
  TouchableWithoutFeedback,
} from 'react-native';
import PhotoView from 'react-native-photo-view';

export default class ZoomableImage extends React.Component {
  props: {
    url: string;
    width: number;
    height: number;
  };

  state: {
    lastTapTimestamp: number;
    isZoomed: boolean;
  };

  zoomable_scroll: ReactElement<ScrollView>;

  constructor() {
    super();
    this.state = {
      lastTapTimestamp: 0,
      isZoomed: false,
    };

    (this: any).onZoomChanged = this.onZoomChanged.bind(this);
    (this: any).toggleZoom = this.toggleZoom.bind(this);
  }

/*
  componentDidMount() {
    const zoomScale = this.getNaturalZoomScale();
    console.log(zoomScale);
    this.zoomable_scroll.setNativeProps({
      //zoomScale: zoomScale,
    });
    console.log(this.props);
    console.log(this.props.width * zoomScale);
    //this.zoomable_scroll.scrollTo({x: 205, y: 0, animated: false});
 //= 0.5;
    this.zoomable_scroll.scrollResponderZoomTo({
      width: this.props.width,
      height: this.props.height,
      x: 0,
      y: 0,
    });
  }

  getNaturalZoomScale() {
    const windowSize = Dimensions.get('window');
    const widthScale = windowSize.width / this.props.width;
    const heightScale = windowSize.height / this.props.height;
    const zoomScale = Math.min(widthScale, heightScale);
    return zoomScale;
  }
*/

  render() {
    const windowSize = Dimensions.get('window');
    const widthScale = windowSize.width / this.props.width;
    const heightScale = windowSize.height / this.props.height;
    const zoomScale = Math.min(widthScale, heightScale);
    const horizontal = (widthScale < heightScale);

    if (Platform.OS == 'android') {
      return <PhotoView
        maximumZoomScale={Math.max(zoomScale, 4.0)}
        minimumZoomScale={Math.min(zoomScale, 1.0)}
        style={[styles.image, {flex: 1, width: this.props.width, height: this.props.height}]}
        source={{uri: this.props.url}}
        />;
    } else {
      this.renderIOS(zoomScale, horizontal);
    }
  }

  renderIOS(zoomScale: number, horizontal: boolean) {
    return (
      <ScrollView
        ref={(x) => {this.zoomable_scroll = x;}}
        onScroll={this.onZoomChanged}
        scrollEventThrottle={100}
        scrollsToTop={false}
        alwaysBounceVertical={false}
        alwaysBounceHorizontal={false}
        showsHorizontalScrollIndicator={false}
        showsVerticalScrollIndicator={false}
        maximumZoomScale={Math.max(zoomScale, 4.0)}
        minimumZoomScale={Math.min(zoomScale, 1.0)}
        horizontal={horizontal}
        directionalLockEnabled={false}
        centerContent={true}
        style={{flex: 1}}
        >
        <TouchableWithoutFeedback onPress={this.toggleZoom} style={{flex: 1}}>
          <Image
            style={[styles.image, {width: this.props.width, height: this.props.height}]}
            source={{uri: this.props.url}}
          />
        </TouchableWithoutFeedback>
      </ScrollView>
    );
  }

  toggleZoom(e: any) {
    var timestamp = new Date().getTime();
    if (timestamp - this.state.lastTapTimestamp <= 500) {
      var {locationX, locationY} = e.nativeEvent;
      var size = this.state.isZoomed ? {width: 10000, height: 10000} : {width: 0, height: 0};
      this.zoomable_scroll.scrollResponderZoomTo({x: locationX, y: locationY, ...size});
    }
    this.setState({lastTapTimestamp: timestamp});
  }

  onZoomChanged(e: any) {
    this.setState({isZoomed: e.nativeEvent.zoomScale > 1});
  }
}

var styles = StyleSheet.create({
  image: {
    flex: 1,
    resizeMode: Image.resizeMode.contain,
  },
});
