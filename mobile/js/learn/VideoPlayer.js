/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Animated, Image, Platform, StyleSheet, View } from 'react-native';
import VideoPlayer from 'react-native-video-controls';

export default class MyVideoPlayer extends VideoPlayer {
  constructor(props) {
    super(props);
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
          <View style={[styles.player.container, styles.controls.seekbar]}>
            {this.renderSeekbar()}
          </View>
          <View
            style={[styles.controls.column, styles.controls.bottomControlGroup]}
          >
            {this.renderPlayPause()}
            {this.renderTitle()}
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
      padding: 16,
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
      zIndex: 100,
      marginTop: 24,
      marginBottom: 8,
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
      marginLeft: 12,
      marginRight: 12,
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
      width: 80,
      zIndex: 0,
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
    timer: {
      width: 80,
    },
    timerText: {
      backgroundColor: 'transparent',
      color: '#FFF',
      fontSize: 11,
      textAlign: 'right',
    },
  }),
};
