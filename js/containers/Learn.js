/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  StyleSheet,
  View,
} from 'react-native';
import BlogList from '../learn/BlogList';

export default class LearnApp extends React.Component {

  render() {
    return <View style={styles.container}>
      <BlogList />
    </View>;
  }
}


const styles = StyleSheet.create({
  container: {
    //top: STATUSBAR_HEIGHT,
    flex: 1,
    backgroundColor: 'black',
  },
});
