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
  Card,
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
import {
  getPreference,
  setPreference,
} from '../notifications/prefs';

const STATUSBAR_HEIGHT = Platform.OS === 'ios' ? 20 : 0;

const messages = defineMessages({
});

class NamedSwitch extends React.Component {
  state: {
    value: boolean;
  };
  props: {
    text: string;
    style: any;

    pref: string;
    defaultValue: boolean;
  }

  constructor(props) {
    super(props);
    this.state = {
      value: this.props.defaultValue,
    };
  }

  componentWillMount() {
    this.loadPreference();
  }

  async loadPreference() {
    this.setState({value: await getPreference(this.props.pref) === '1'});
  }

  async onChange(value: boolean) {
    await setPreference(this.props.pref, value ? '1' : '0');
    // Only set the state if the above doesn't error out
    this.setState({value});
  }

  render() {
    const {style, pref, defaultValue, ...otherProps} = this.props;

    return <HorizontalView style={[style, {justifyContent: 'space-between'}]}>
      <Text>{this.props.text}:</Text>
      <Switch {...otherProps}
        value={this.state.value}
        onValueChange={(value) => this.onChange(value)}
      />
    </HorizontalView>;
  }
}
class _NotificationPreferences extends React.Component {

  render() {
    return <ScrollView style={styles.container} contentContainerStyle={styles.containerContent}>
    <Card title={
      <NamedSwitch text="Notifications"
        style={{
          margin: 5,
          alignItems: 'center',
        }}
        pref="overall"
        defaultValue={true}
        />
      }>
      <NamedSwitch text="Play Sound" pref="sounds" defaultValue={true} />
      <NamedSwitch text="Vibration" pref="vibration" defaultValue={true} />
    </Card>
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
