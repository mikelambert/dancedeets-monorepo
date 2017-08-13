/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Animated,
  Image,
  Platform,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import VideoPlayer from 'react-native-video-controls';

export default class MyVideoPlayer extends VideoPlayer {
  constructor(props) {
    super(props);

    this.events.onScreenPress = () => {};
  }

  setControlTimeout() {
    // Disable the timeout that hides the controls
  }

  /**
     * Animation to hide controls. We fade the
     * display to 0 then move them off the
     * screen so they're not interactable
     */
  hideControlAnimation() {
    Animated.parallel([
      Animated.timing(this.animations.bottomControl.opacity, {
        toValue: 0,
        useNativeDriver: true,
      }),
      Animated.timing(this.animations.bottomControl.marginBottom, {
        toValue: 100,
        useNativeDriver: true,
      }),
    ]).start();
  }

  /**
     * Animation to show controls...opposite of
     * above...move onto the screen and then
     * fade in.
     */
  showControlAnimation() {
    Animated.parallel([
      Animated.timing(this.animations.bottomControl.opacity, {
        toValue: 1,
        useNativeDriver: true,
      }),
      Animated.timing(this.animations.bottomControl.marginBottom, {
        toValue: 0,
        useNativeDriver: true,
      }),
    ]).start();
  }

  renderTopControls() {
    return null;
  }

  renderPlayPause() {
    let source = this.state.paused === true
      ? require('react-native-video-controls/assets/img/play.png')
      : require('react-native-video-controls/assets/img/pause.png');
    return this.renderControl(
      <Image source={source} />,
      this.methods.togglePlayPause,
      styles.controls.playPause
    );
  }

  /**
     * Render the seekbar and attach its handlers
     */
  renderSeekbar() {
    return (
      <View style={styles.seek.trackOuter}>
        <View
          style={styles.seek.track}
          onLayout={event => {
            this.player.seekerWidth = event.nativeEvent.layout.width;
          }}
        >
          <View
            style={[
              styles.seek.fill,
              {
                width: this.state.seekerFillWidth,
                backgroundColor: this.props.seekColor || '#FFF',
              },
            ]}
          />
        </View>
        <View
          style={[
            styles.seek.handle,
            {
              left: this.state.seekerPosition - 10,
              padding: 10,
            },
          ]}
          // Necessary on android to ensure this View doesn't get "collapsed"
          // If it does get collapsed, the panresponder only applies to our tiny circle
          collapsable={false}
          {...this.player.seekPanResponder.panHandlers}
        >
          <View style={[styles.seek.circle, { backgroundColor: '#FFF' }]} />
        </View>
      </View>
    );
  }

  /**
     * Show our timer.
     */
  renderTimer() {
    return this.renderControl(
      <Text style={styles.controls.timerText}>
        {this.calculateTime()}
      </Text>,
      this.methods.toggleTimer,
      styles.controls.timer
    );
  }

  /**
     * Render bottom control group and wrap it in a holder
     */
  renderBottomControls() {
    return (
      <Animated.View
        style={[
          styles.controls.bottom,
          {
            opacity: this.animations.bottomControl.opacity,
            transform: [
              {
                translateY: this.animations.bottomControl.marginBottom,
              },
            ],
          },
        ]}
      >
        <Image
          source={require('react-native-video-controls/assets/img/bottom-vignette.png')}
          style={[styles.controls.column, styles.controls.vignette]}
        >
          <View
            style={[styles.controls.column, styles.controls.bottomControlGroup]}
          >
            {this.renderPlayPause()}
            <View style={styles.controls.seekbar}>{this.renderSeekbar()}</View>
            {this.renderTimer()}
          </View>
        </Image>
      </Animated.View>
    );
  }
}

/**
 * This object houses our styles. There's player
 * specific styles and control specific ones.
 * And then there's volume/seeker styles.
 */
const styles = {
  player: StyleSheet.create({
    container: {
      flex: Platform.OS === 'ios' ? 1 : null,
      alignSelf: 'stretch',
      justifyContent: 'space-between',
    },
  }),
  seek: StyleSheet.create({
    trackOuter: {
      alignSelf: 'stretch',
      justifyContent: 'center',
      marginLeft: 8,
      marginRight: 8,
    },
    track: {
      backgroundColor: '#333',
      height: 4,
    },
    fill: {
      alignSelf: 'flex-start',
      marginTop: 1,
      height: 2,
      width: 1,
    },
    handle: {
      position: 'absolute',
    },
    circle: {
      borderRadius: 20,
      height: 12,
      width: 12,
    },
  }),
  controls: StyleSheet.create({
    row: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: null,
      width: null,
    },
    column: {
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: null,
      width: null,
    },
    vignette: {
      resizeMode: 'stretch',
    },
    control: {
      padding: 8,
    },
    text: {
      backgroundColor: 'transparent',
      color: '#FFF',
      fontSize: 16,
      textAlign: 'center',
    },
    pullRight: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
    },
    top: {
      flex: 1,
      alignItems: 'stretch',
      justifyContent: 'flex-start',
    },
    bottom: {
      alignItems: 'stretch',
      flex: 2,
      justifyContent: 'flex-end',
    },
    seekbar: {
      alignSelf: 'stretch',
      alignItems: 'center',
      justifyContent: 'center',
      flex: 1,
      flexDirection: 'column',
      zIndex: 100,
    },
    topControlGroup: {
      alignSelf: 'stretch',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexDirection: 'row',
      width: null,
      margin: 12,
      marginBottom: 18,
    },
    bottomControlGroup: {
      alignSelf: 'stretch',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexDirection: 'row',
      marginBottom: 0,
    },
    volume: {
      flexDirection: 'row',
    },
    fullscreen: {
      flexDirection: 'row',
    },
    playPause: {
      position: 'relative',
      zIndex: 0,
      width: 40,
    },
    title: {
      alignItems: 'center',
      flex: 0.6,
      flexDirection: 'column',
      padding: 0,
    },
    titleText: {
      textAlign: 'center',
    },
    timer: {},
    timerText: {
      backgroundColor: 'transparent',
      color: '#FFF',
      fontSize: 11,
      textAlign: 'right',
    },
  }),
};
