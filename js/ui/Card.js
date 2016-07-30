import React from 'react';
import {
  Dimensions,
  StyleSheet,
  View,
} from 'react-native';
import { purpleColors } from '../Colors';

export default class Card extends React.Component {
  render() {
    return <View style={[styles.card, this.props.style]}>
      <View style={styles.titleBackground}>{this.props.title}</View>
      <View style={styles.mainBackground}>{this.props.children}</View>
    </View>;
  }
}

const styles = StyleSheet.create({
  titleBackground: {
    backgroundColor: purpleColors[2],
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  mainBackground: {
    padding: 10,
  },
  card: {
    backgroundColor: purpleColors[4],
    borderColor: purpleColors[0],
    //borderWidth: 1,
    borderRadius: 10,
    margin: 10,
  },
});
