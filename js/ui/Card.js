import React from 'react';
import {
  Dimensions,
  StyleSheet,
  View,
} from 'react-native';
import { purpleColors } from '../Colors';

export default class Card extends React.Component {
  render() {
    return <View style={[styles.card, this.props.style]}>{this.props.children}</View>;
  }
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: purpleColors[3],
    borderColor: purpleColors[0],
    borderWidth: 1,
    borderRadius: 10,
    padding: 10,
    margin: 10,
  },
});
