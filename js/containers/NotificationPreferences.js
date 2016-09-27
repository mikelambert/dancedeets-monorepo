/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Platform,
  ScrollView,
  StyleSheet,
  Switch,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import {
  HorizontalView,
  normalize,
  Text,
} from '../ui';
import { purpleColors } from '../Colors';
import { track } from '../store/track';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';

const STATUSBAR_HEIGHT = Platform.OS === 'ios' ? 20 : 0;

const messages = defineMessages({
});

class NamedSwitch extends React.Component {
  render() {
    return <HorizontalView style={{justifyContent: 'space-between'}}>
      <Text>{this.props.text}:</Text><Switch />
    </HorizontalView>;
  }
}
class _NotificationPreferences extends React.Component {

  render() {
    return <ScrollView style={styles.container} contentContainerStyle={styles.containerContent}>
      <NamedSwitch text="Notifications" />
      <NamedSwitch text="Play Sound" />
    </ScrollView>;
  }
}
export default injectIntl(_NotificationPreferences);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: purpleColors[4],
  },
  containerContent: {
    top: STATUSBAR_HEIGHT,
    alignItems: 'stretch',
    justifyContent: 'space-around',
  },
});
