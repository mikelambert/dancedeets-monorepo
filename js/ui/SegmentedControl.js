/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';

import {
  Platform,
  SegmentedControlIOS,
} from 'react-native';

import normalizeColor from 'normalizeColor';
import SegmentedControlAndroid from 'react-native-segmented-android';

type Props = {
  values: [string],
  defaultIndex: number,
  enabled: boolean,
  tryOnChange: (index: number, oldIndex: number) => Promise,
  tintColor: string,
  style: any,
};

function disabledColor(color: string, multiplier: number = 0.5) {
  const colorNumber = normalizeColor(color);
  if (colorNumber == null) {
    // No color, give up and return existing color
    return color;
  }
  const colorComponents = [
    ((colorNumber & 0xff000000) >> 24) + 256, // r
    (colorNumber & 0x00ff0000) >> 16,         // g
    (colorNumber & 0x0000ff00) >> 8,          // b
  ];
  const disabledColorComponents = colorComponents.map((d) => d * multiplier);
  const disabledNumber = (
    (disabledColorComponents[0] << 16) |
    (disabledColorComponents[1] << 8)  |
    (disabledColorComponents[2] << 0)
  );
  const disabledHex = '#' + ('000000' + disabledNumber.toString(16)).substr(-6);
  return disabledHex;
}

export default class SegmentedControl extends React.Component {
  state: {
    selectedIndex: number,
  };

  props: Props;

  static defaultProps = {
    values: [],
    defaultIndex: -1,
    enabled: true,
    tryOnChange: async (index, oldIndex) => {},
    tintColor: 'blue',
    style: {},
  };

  constructor(props: Props) {
    super(props);
    this.state = {
      selectedIndex: this.props.defaultIndex,
    };
  }

  async onChange(index: number) {
    // On android, we get called anytime it changes, including when initializing to the passed-in selectedPosition.
    // We don't want to trigger a "set" (and associated reloads) if there's been no change (init-ing),
    // as that triggers a set and get, potentially triggering infinite cycle of reloads.
    // Instead, we eary-exit if this is a no-op change.
    if (this.state.selectedIndex === index) {
      return;
    }
    // If we're not enabled, don't actually attempt to do anything
    // This is important for Android, which doesn't support enabled natively,
    // and so will still call onChange.
    const oldIndex = this.state.selectedIndex;
    if (!this.props.enabled) {
      // Make sure we trigger an 'update' even though nothing should happen while we're disabled.
      // Triggering forceUpdate() isn't sufficient, since it recognizes there is no "change"
      // to our rendered stated (selectedIndex did not change), and so does not update the native control,
      // which then ends up with an out-of-sync native selectedIndex relative to this.props.selectedIndex.
      //
      // By changing the state back-and-forth, we force a native update and re-render,
      // which ensures the native component will point at selectedIndex.
      this.setState({selectedIndex: index});
      this.setState({selectedIndex: oldIndex});
      return;
    }
    // Only we're enabled, let's try our update (and rolling back, if there were any failures)
    if (this.props.tryOnChange) {
      try {
        await this.props.tryOnChange(index, oldIndex);
      } catch (e) {
        console.warn('Undoing SegmentedControl due to error calling tryOnChange:', e, e.stack);
        this.setState({selectedIndex: oldIndex});
      }
    } else {
      this.setState({selectedIndex: index});
    }
  }


  render() {
    if (Platform.OS === 'ios') {
      return <SegmentedControlIOS
        style={this.props.style}
        values={this.props.values}
        enabled={this.props.enabled}
        selectedIndex={this.state.selectedIndex}
        onChange={(event) => this.onChange(event.nativeEvent.selectedSegmentIndex)}
        tintColor={this.props.tintColor} // iOS handles the disabled color automatically
      />;
    } else {
      const tintColor = this.props.enabled ? this.props.tintColor : disabledColor(this.props.tintColor);
      return <SegmentedControlAndroid
        key="selected"
        style={this.props.style}
        childText={this.props.values}
        orientation="horizontal"
        onChange={(event) => this.onChange(event.selected)}
        tintColor={[tintColor, '#000000']}
        selectedPosition={this.state.selectedIndex}
        />;
    }
  }
}
