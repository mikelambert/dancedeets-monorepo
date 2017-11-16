/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { defineMessages } from 'react-intl';
import { track } from '../../store/track';
import ProfilePage from '../Profile';
import NotificationPreferences from '../NotificationPreferences';
import StackNavigator from './Navigator';
import Credits from '../Credits';

const messages = defineMessages({
  notificationsTitle: {
    id: 'navigator.notificationsTitle',
    defaultMessage: 'Notification Settings',
    description: 'Titlebar for notification settings',
  },
  about: {
    id: 'tab.about',
    defaultMessage: 'About',
    description: 'Tab button to show general info, as well as panel title',
  },
  credits: {
    id: 'credits.title',
    defaultMessage: 'Dancedeets Credits',
    description: 'Header of our Credits section',
  },
});

class MainScreen extends React.Component<{
  navigation: NavigationScreenProp<any>,
}> {
  static navigationOptions = ({ screenProps }) => ({
    title: screenProps.intl.formatMessage(messages.about),
  });

  constructor(props) {
    super(props);
    (this: any).onNotificationPreferences = this.onNotificationPreferences.bind(
      this
    );
  }

  onNotificationPreferences() {
    track('Open Notification Preferences');
    this.props.navigation.navigate('NotificationPreferences');
  }

  render() {
    return (
      <ProfilePage
        onNotificationPreferences={this.onNotificationPreferences}
        openCredits={() => this.props.navigation.navigate('Credits')}
      />
    );
  }
}

class CreditsScreen extends React.Component<{}> {
  static navigationOptions = ({ screenProps }) => ({
    headerTitle: screenProps.intl.formatMessage(messages.credits),
  });

  render() {
    return <Credits />;
  }
}

class NotificationScreen extends React.Component<{}> {
  static navigationOptions = ({ screenProps }) => ({
    title: screenProps.intl.formatMessage(messages.notificationsTitle),
  });

  render() {
    return <NotificationPreferences />;
  }
}

export const AboutScreensNavigator = StackNavigator('about', {
  AboutMain: { screen: MainScreen },
  Credits: { screen: CreditsScreen },
  NotificationPreferences: { screen: NotificationScreen },
});
