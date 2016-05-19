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
  onChange: (index: number) => void,
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
    onChange: () => {},
    tintColor: 'blue',
    style: {},
  };

  constructor(props: Props) {
    super(props);

    this.state = {
      selectedIndex: this.props.defaultIndex,
    };
  }

  onChange(index: number) {
    this.setState({selectedIndex: index});
    if (this.props.onChange) {
      this.props.onChange(index);
    }
  }

  render() {
    if (Platform.OS === 'ios') {
      return <SegmentedControlIOS
        style={this.props.style}
        values={this.props.values}
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
