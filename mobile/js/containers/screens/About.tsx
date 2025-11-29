/**
 * Copyright 2016 DanceDeets.
 *
 * React Navigation v6 About screens
 */

import * as React from 'react';
import { createStackNavigator, StackScreenProps } from '@react-navigation/stack';
import { useIntl, defineMessages } from 'react-intl';
import { track } from '../../store/track';
import ProfilePage from '../Profile';
import NotificationPreferences from '../NotificationPreferences';
import Credits from '../Credits';
import { gradientTop } from '../../Colors';

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

// Type definitions for navigation
type AboutStackParamList = {
  AboutMain: undefined;
  Credits: undefined;
  NotificationPreferences: undefined;
};

const Stack = createStackNavigator<AboutStackParamList>();

// Main Screen
interface MainScreenProps extends StackScreenProps<AboutStackParamList, 'AboutMain'> {}

function MainScreen({ navigation }: MainScreenProps) {
  const onNotificationPreferences = () => {
    track('Open Notification Preferences');
    navigation.navigate('NotificationPreferences');
  };

  const openCredits = () => {
    navigation.navigate('Credits');
  };

  return (
    <ProfilePage
      onNotificationPreferences={onNotificationPreferences}
      openCredits={openCredits}
    />
  );
}

// Credits Screen
function CreditsScreen() {
  return <Credits />;
}

// Notification Screen
function NotificationScreen() {
  return <NotificationPreferences />;
}

// Main About Screens Navigator
export function AboutScreensNavigator() {
  const intl = useIntl();

  return (
    <Stack.Navigator
      screenOptions={{
        headerTintColor: 'white',
        headerStyle: {
          backgroundColor: gradientTop,
        },
        cardStyle: {
          backgroundColor: 'black',
        },
      }}
    >
      <Stack.Screen
        name="AboutMain"
        component={MainScreen}
        options={{
          title: intl.formatMessage(messages.about),
        }}
      />
      <Stack.Screen
        name="Credits"
        component={CreditsScreen}
        options={{
          title: intl.formatMessage(messages.credits),
        }}
      />
      <Stack.Screen
        name="NotificationPreferences"
        component={NotificationScreen}
        options={{
          title: intl.formatMessage(messages.notificationsTitle),
        }}
      />
    </Stack.Navigator>
  );
}
