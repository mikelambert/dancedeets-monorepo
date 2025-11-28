import * as React from 'react';
import { StyleProp, StyleSheet, View, ViewStyle } from 'react-native';
import { gradientBottom, purpleColors } from '../Colors';

interface Props {
  style?: StyleProp<ViewStyle>;
  titleBackgroundStyle?: StyleProp<ViewStyle>;
  mainBackgroundStyle?: StyleProp<ViewStyle>;
  title: React.ReactNode;
  children: React.ReactNode;
}

export default class Card extends React.Component<Props> {
  _root: any;

  setNativeProps(props: any) {
    this._root.setNativeProps(props);
  }

  render() {
    return (
      <View
        ref={x => {
          this._root = x;
        }}
        style={[styles.card, this.props.style]}
      >
        <View style={[styles.titleBackground, this.props.titleBackgroundStyle]}>
          {this.props.title}
        </View>
        <View style={[styles.mainBackground, this.props.mainBackgroundStyle]}>
          {this.props.children}
        </View>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  titleBackground: {
    backgroundColor: purpleColors[1],
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  mainBackground: {
    padding: 10,
  },
  card: {
    backgroundColor: gradientBottom,
    borderColor: purpleColors[0],
    borderRadius: 10,
    margin: 10,
  },
});
