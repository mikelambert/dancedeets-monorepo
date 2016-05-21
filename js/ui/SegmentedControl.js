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

import SegmentedControlAndroid from 'react-native-segmented-android';

type Props = {
  values: [string],
  defaultIndex: number,
  enabled: boolean,
  tryOnChange: (index: number, oldIndex: number) => Promise,
  tintColor: string,
  style: any,
};

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
    const oldIndex = this.state.selectedIndex;
    this.setState({selectedIndex: index});
    if (this.props.tryOnChange) {
      try {
        await this.props.tryOnChange(index, oldIndex);
      } catch (error) {
        console.warn('Undoing SegmentedControl due to rrror setting RSVP:', error);
        this.setState({selectedIndex: oldIndex});
      }
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
        tintColor={this.props.tintColor}
      />;
    } else {
      return <SegmentedControlAndroid
        style={this.props.style}
        childText={this.props.values}
        orientation="horizontal"
        selectedPosition={this.state.selectedIndex}
        onChange={(event) => this.onChange(event.selected)}
        tintColor={[this.props.tintColor, '#000000ff']}
      />;
    }
  }
}
