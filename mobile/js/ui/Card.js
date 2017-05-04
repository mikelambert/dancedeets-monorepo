import React from 'react';
import { StyleSheet, View } from 'react-native';
import { purpleColors } from '../Colors';

export default class Card extends React.Component {
  props: {
    style: View.propTypes.style,
    titleBackgroundStyle: View.propTypes.style,
    mainBackgroundStyle: View.propTypes.style,
    title: string,
    children: Array<React.Element<*>>,
  };

  _root: React.Component;

  setNativeProps(props) {
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
    backgroundColor: purpleColors[2],
    borderColor: purpleColors[0],
    // borderWidth: 1,
    borderRadius: 10,
    margin: 10,
  },
});
