/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { Text } from '../ui';

const credits: Array<[string, Array<string>]> = [
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

interface CreditSubListProps {
  list: Array<string>;
}

class CreditSubList extends React.Component<CreditSubListProps> {
  render() {
    const subcreditGroups = this.props.list.map(x => (
      <Text key={x} style={{ left: 5 }}>
        - {x}
      </Text>
    ));
    return <View>{subcreditGroups}</View>;
  }
}

interface CreditsProps {
  style?: ViewStyle;
}

export default class Credits extends React.Component<CreditsProps> {
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
