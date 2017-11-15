/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { StyleSheet, View } from 'react-native';
import { Text } from '../ui';

const credits = [
  ['Web & App Programming', ['Mike Lambert']],
  ['Logo', ['James "Cricket" Colter']],
  ['App Login Photos', ['dancephotos.ch']],
  [
    'Translations',
    [
      'French: Mai Le, Hayet',
      'Japanese: Huu Rock',
      'Chinese: Wei, King Kong, Zoe',
    ],
  ],
];

class CreditSubList extends React.Component<{
  list: Array<string>,
}> {
  render() {
    const subcreditGroups = this.props.list.map(x => (
      <Text key={x} style={{ left: 5 }}>
        - {x}
      </Text>
    ));
    return <View>{subcreditGroups}</View>;
  }
}

export default class Credits extends React.Component<{
  style?: Object,
}> {
  render() {
    const creditGroups = credits.map(x => (
      <View key={x[0]}>
        <Text style={{ fontWeight: 'bold' }}>{x[0]}:</Text>
        <CreditSubList list={x[1]} />
      </View>
    ));
    return (
      <View style={[styles.outerStyle, this.props.style]}>{creditGroups}</View>
    );
  }
}

const styles = StyleSheet.create({
  outerStyle: {
    margin: 20,
  },
});
