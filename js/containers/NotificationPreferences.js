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
    style?: any;

    value: boolean;
    onValueChange: (value: boolean) => any;

    disabled?: boolean;
  };

  render() {
    const {style, text, value, onValueChange, ...otherProps} = this.props;
    console.log(text, value);
    return <HorizontalView style={[style, {justifyContent: 'space-between'}]}>
      <Text>{text}:</Text>
      <Switch {...otherProps}
        value={value}
        onValueChange={onValueChange}
      />
    </HorizontalView>;
  }
}

class _NotificationPreferences extends React.Component {
  state: {[key: string]: boolean};

  constructor(props) {
    super(props);
    this.state = {
    };
  }

  static preferenceDefaults = {
    overall: true,
    sounds: true,
    vibration: true,
  };

  componentWillMount() {
    this.loadPreference();
  }

  async loadPreference() {
    const preferences = {};
    const defaults = this.constructor.preferenceDefaults;
    for (let key of Object.keys(defaults)) {
      preferences[key] = await getPreference(key, defaults[key]);
    }
    this.setState(preferences);
  }

  async onChange(key: string, value: boolean) {
    await setPreference(key, value);
    // Only set the state if the above doesn't error out
    this.setState({[key]: value});
  }

  render() {
    return <ScrollView style={styles.container} contentContainerStyle={styles.containerContent}>
      <Card title={
        <NamedSwitch
          text="Notifications"
          style={{
            margin: 5,
            alignItems: 'center',
          }}
          value={this.state.overall}
          onValueChange={(value) => this.onChange('overall', value)}
          />
        }>
        <NamedSwitch
          disabled={!this.state.overall}
          text="Play Sound"
          value={this.state.sounds}
          onValueChange={(value) => this.onChange('sounds', value)}
          />
        <NamedSwitch
          disabled={!this.state.overall}
          text="Vibration"
          value={this.state.vibration}
          onValueChange={(value) => this.onChange('vibration', value)}
          />
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
