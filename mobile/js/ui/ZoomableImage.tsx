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
 */

import React from 'react';
import {
  Image,
  Platform,
  ScrollView,
  StyleSheet,
  TouchableWithoutFeedback,
  View,
} from 'react-native';
import PhotoView from 'react-native-photo-view';

type Layout = {
  x: number;
  y: number;
  width: number;
  height: number;
};

interface Props {
  url: string;
  width: number;
  height: number;
}

interface State {
  lastTapTimestamp: number;
  isZoomed: boolean;
  layout?: Layout;
}

export default class ZoomableImage extends React.Component<Props, State> {
  _zoomableScroll?: ScrollView | null;

  constructor(props: Props) {
    super(props);
    this.state = {
      lastTapTimestamp: 0,
      isZoomed: false,
      layout: undefined,
    };

    this.onZoomChanged = this.onZoomChanged.bind(this);
    this.toggleZoom = this.toggleZoom.bind(this);
    this.onLayout = this.onLayout.bind(this);
  }

  onLayout(e: any) {
    this.setState({ layout: e.nativeEvent.layout });
  }

  onZoomChanged(e: any) {
    this.setState({ isZoomed: e.nativeEvent.zoomScale > 1 });
  }

  toggleZoom(e: any) {
    const timestamp = new Date().getTime();
    if (timestamp - this.state.lastTapTimestamp <= 500) {
      const { locationX, locationY } = e.nativeEvent;
      const size = this.state.isZoomed
        ? { width: 10000, height: 10000 }
        : { width: 0, height: 0 };
      if (this._zoomableScroll) {
        (this._zoomableScroll as any).scrollResponderZoomTo({
          x: locationX,
          y: locationY,
          ...size,
        });
      }
    }
    this.setState({ lastTapTimestamp: timestamp });
  }

  renderIOS(zoomScale: number, horizontal: boolean) {
    return (
      <ScrollView
        ref={x => {
          this._zoomableScroll = x;
        }}
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
        centerContent
        contentContainerStyle={{
          alignItems: 'center',
          justifyContent: 'center',
        }}
        style={{ flex: 1 }}
      >
        <TouchableWithoutFeedback onPress={this.toggleZoom} style={{ flex: 1 }}>
          <Image
            style={[
              styles.image,
              { width: this.props.width, height: this.props.height },
            ]}
            source={{ uri: this.props.url }}
          />
        </TouchableWithoutFeedback>
      </ScrollView>
    );
  }

  render() {
    let contents = null;
    if (this.state.layout) {
      const widthScale = this.state.layout.width / this.props.width;
      const heightScale = this.state.layout.height / this.props.height;
      const zoomScale = Math.min(widthScale, heightScale);

      if (Platform.OS === 'android') {
        contents = (
          <PhotoView
            maximumZoomScale={Math.max(zoomScale, 4.0)}
            minimumZoomScale={Math.min(zoomScale, 1.0)}
            androidScaleType="fitCenter"
            style={[{ flex: 1 }]}
            source={{
              uri: this.props.url,
              width: this.props.width,
              height: this.props.height,
            }}
          />
        );
      } else if (Platform.OS === 'ios') {
        const horizontal = widthScale < heightScale;
        contents = this.renderIOS(zoomScale, horizontal);
      }
    }
    return (
      <View style={{ flex: 1 }} onLayout={this.onLayout}>
        {contents}
      </View>
    );
  }
}

const styles = StyleSheet.create({
  image: {
    flex: 1,
    resizeMode: Image.resizeMode.contain,
  },
});
