/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Platform, SegmentedControlIOS, StyleProp, ViewStyle } from 'react-native';
import normalizeColor from 'react-native/Libraries/StyleSheet/normalizeColor';
import SegmentedControlAndroid from 'react-native-segmented-android';

interface Props {
  values: string[];
  defaultIndex: number;
  enabled: boolean;
  tryOnChange: (index: number, oldIndex: number) => void | Promise<void>;
  tintColor: string;
  style?: StyleProp<ViewStyle>;
}

interface State {
  selectedIndex: number;
}

function disabledColor(color: string, multiplier: number = 0.5): string {
  const colorNumber = normalizeColor(color);
  if (colorNumber == null) {
    return color;
  }
  /* eslint-disable no-bitwise */
  const colorComponents = [
    ((colorNumber & 0xff000000) >> 24) + 256, // r
    (colorNumber & 0x00ff0000) >> 16, // g
    (colorNumber & 0x0000ff00) >> 8, // b
  ];
  const disabledColorComponents = colorComponents.map(d => d * multiplier);
  const disabledNumber =
    (disabledColorComponents[0] << 16) |
    (disabledColorComponents[1] << 8) |
    (disabledColorComponents[2] << 0);
  /* eslint-enable no-bitwise */
  const disabledHex = `#${`000000${disabledNumber.toString(16)}`.substr(-6)}`;
  return disabledHex;
}

export default class SegmentedControl extends React.Component<Props, State> {
  static defaultProps: Partial<Props> = {
    values: [],
    defaultIndex: -1,
    enabled: true,
    tryOnChange: (index, oldIndex) => {},
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
    if (this.state.selectedIndex === index) {
      return;
    }
    if (Platform.OS === 'ios') {
      this.setState({ selectedIndex: index });
    }
    const oldIndex = this.state.selectedIndex;
    if (!this.props.enabled) {
      this.setState({ selectedIndex: index });
      this.setState({ selectedIndex: oldIndex });
      return;
    }
    if (this.props.tryOnChange) {
      try {
        await this.props.tryOnChange(index, oldIndex);
      } catch (e) {
        console.warn(
          'Undoing SegmentedControl due to error calling tryOnChange:',
          e,
          (e as any).stack
        );
        this.setState({ selectedIndex: oldIndex });
      }
    } else {
      this.setState({ selectedIndex: index });
    }
  }

  render() {
    if (Platform.OS === 'ios') {
      return (
        <SegmentedControlIOS
          style={this.props.style}
          values={this.props.values}
          enabled={this.props.enabled}
          selectedIndex={this.state.selectedIndex}
          onChange={event =>
            this.onChange(event.nativeEvent.selectedSegmentIndex)}
          tintColor={this.props.tintColor}
        />
      );
    } else if (Platform.OS === 'android') {
      const tintColor = this.props.enabled
        ? this.props.tintColor
        : disabledColor(this.props.tintColor);
      return (
        <SegmentedControlAndroid
          key="selected"
          style={[{ height: 30 }, this.props.style]}
          childText={this.props.values}
          orientation="horizontal"
          onChange={(event: any) => this.onChange(event.selected)}
          tintColor={[tintColor, '#000000']}
          selectedPosition={this.state.selectedIndex}
        />
      );
    }
    return null;
  }
}
