/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import zip from 'lodash/zip';
import * as React from 'react';
import { Platform, ScrollView, StyleSheet, Switch } from 'react-native';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import { HorizontalView, Text } from '../ui';
import { purpleColors } from '../Colors';
import {
  PreferenceNames,
  getPreference,
  setPreference,
} from '../notifications/prefs';

const STATUSBAR_HEIGHT = Platform.OS === 'ios' ? 20 : 0;

const messages = defineMessages({
  notificationHeader: {
    id: 'notifications.header',
    defaultMessage: 'Notifications:',
    description: 'Title for the Notifications Preferences card',
  },
  notificationSounds: {
    id: 'notifications.sounds',
    defaultMessage: 'Play Sound:',
    description: 'Should we play a sound on notification',
  },
  notificationVibration: {
    id: 'notifications.vibration',
    defaultMessage: 'Vibrate:',
    description: 'Should we vibrate on notification',
  },
});

class NamedSwitch extends React.Component<
  {
    text: string,
    style?: any,
  },
  {
    value: boolean,
  }
> {
  render() {
    const { style, text, ...otherProps } = this.props;
    return (
      <HorizontalView style={[style, { justifyContent: 'space-between' }]}>
        <Text>{text}</Text>
        <Switch {...otherProps} />
      </HorizontalView>
    );
  }
}

class _NotificationPreferences extends React.Component<
  {
    intl: intlShape,
  },
  {
    [key: string]: boolean,
  }
> {
  static preferenceDefaults = {
    overall: true,
    sounds: true,
    vibration: true,
  };

  constructor(props) {
    super(props);
    this.state = {};
  }

  componentWillMount() {
    this.loadPreference();
  }

  async onChange(key: string, value: boolean) {
    await setPreference(key, value);
    // Only set the state if the above doesn't error out
    this.setState({ [key]: value });
  }

  async loadPreference() {
    const defaults = this.constructor.preferenceDefaults;
    const keys = Object.keys(defaults);
    const promises = keys.map(key => getPreference(key, defaults[key]));
    const values = Promise.all(promises);
    const preferences = {};
    zip(keys, values).forEach(([key, value]) => {
      preferences[key] = value;
    });
    this.setState(preferences);
  }

  render() {
    return (
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.containerContent}
      >
        <NamedSwitch
          text={this.props.intl.formatMessage(messages.notificationHeader)}
          style={styles.regularSwitch}
          value={this.state.overall}
          onValueChange={value => this.onChange(PreferenceNames.overall, value)}
        />
        <NamedSwitch
          disabled={!this.state.overall}
          style={styles.indentedSwitch}
          text={this.props.intl.formatMessage(messages.notificationSounds)}
          value={this.state.sounds}
          onValueChange={value => this.onChange(PreferenceNames.sounds, value)}
        />
        <NamedSwitch
          disabled={!this.state.overall}
          style={styles.indentedSwitch}
          text={this.props.intl.formatMessage(messages.notificationVibration)}
          value={this.state.vibration}
          onValueChange={value =>
            this.onChange(PreferenceNames.vibration, value)}
        />
      </ScrollView>
    );
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
  regularSwitch: {
    marginVertical: 5,
    marginLeft: 5,
    alignItems: 'center',
  },
  indentedSwitch: {
    marginVertical: 5,
    marginLeft: 20,
    alignItems: 'center',
  },
});
