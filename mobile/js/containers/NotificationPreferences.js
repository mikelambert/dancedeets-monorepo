/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Platform, ScrollView, StyleSheet, Switch } from 'react-native';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import { Card, HorizontalView, Text } from '../ui';
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

class NamedSwitch extends React.Component {
  props: {
    text: string,
    style?: any,
  };

  state: {
    value: boolean,
  };

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

class _NotificationPreferences extends React.Component {
  static preferenceDefaults = {
    overall: true,
    sounds: true,
    vibration: true,
  };

  props: {
    intl: intlShape,
  };

  state: {
    [key: string]: boolean,
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
    const preferences = {};
    const defaults = this.constructor.preferenceDefaults;
    for (const key of Object.keys(defaults)) {
      preferences[key] = await getPreference(key, defaults[key]);
    }
    this.setState(preferences);
  }

  render() {
    return (
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.containerContent}
      >
        <Card
          title={
            <NamedSwitch
              text={this.props.intl.formatMessage(messages.notificationHeader)}
              style={{
                margin: 5,
                alignItems: 'center',
              }}
              value={this.state.overall}
              onValueChange={value =>
                this.onChange(PreferenceNames.overall, value)}
            />
          }
        >
          <NamedSwitch
            disabled={!this.state.overall}
            text={this.props.intl.formatMessage(messages.notificationSounds)}
            value={this.state.sounds}
            onValueChange={value =>
              this.onChange(PreferenceNames.sounds, value)}
          />
          <NamedSwitch
            disabled={!this.state.overall}
            text={this.props.intl.formatMessage(messages.notificationVibration)}
            value={this.state.vibration}
            onValueChange={value =>
              this.onChange(PreferenceNames.vibration, value)}
          />
        </Card>
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
});
