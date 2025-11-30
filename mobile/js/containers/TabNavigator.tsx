/**
 * Copyright 2016 DanceDeets.
 *
 * React Navigation v6 bottom tab navigator
 */

import * as React from 'react';
import { Platform, StyleSheet } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useIntl, IntlShape } from 'react-intl';
import { defineMessages } from 'react-intl';
import { WebView } from 'react-native-webview';
import Icon from 'react-native-vector-icons/Ionicons';
import {
  EventScreensNavigator,
  LearnScreensNavigator,
  AboutScreensNavigator,
} from './screens';
import { semiNormalize } from '../ui';
import { purpleColors } from '../Colors';

const Tab = createBottomTabNavigator();

const messages = defineMessages({
  events: {
    id: 'tab.events',
    defaultMessage: 'Events',
    description: 'Tab button to show list of events',
  },
  learn: {
    id: 'tab.learn',
    defaultMessage: 'Tutorials',
    description: 'Tab button to help folks learn about dance',
  },
  about: {
    id: 'tab.about',
    defaultMessage: 'About',
    description:
      'Tab button to show general info about Dancedeets, Profile, and Share info',
  },
  articles: {
    id: 'tab.articles',
    defaultMessage: 'Articles',
    description:
      'Tab button to show the blog articles and essays on the DanceDeets Medium page',
  },
});

function getTabBarIcon(name: string) {
  return ({ focused, color }: { focused: boolean; color: string }) => {
    let iconName: string;
    if (Platform.OS === 'android') {
      iconName = `md-${name}`;
    } else if (Platform.OS === 'ios') {
      iconName = focused ? `ios-${name}` : `ios-${name}-outline`;
    } else {
      iconName = name;
    }
    return <Icon name={iconName} size={30} style={styles.icon} color={color} />;
  };
}

const mediumUrl =
  'https://medium.dancedeets.com/?utm_source=articles_tab&utm_medium=mobile_app&utm_campaign=articles_tab';

function ArticlesScreen(): React.ReactElement {
  return <WebView source={{ uri: mediumUrl }} />;
}

interface TabNavigatorProps {
  intl?: IntlShape;
}

function TabNavigatorInner({ intl }: TabNavigatorProps): React.ReactElement {
  // Use hook if intl not provided via props
  const intlFromHook = useIntl();
  const intlToUse = intl || intlFromHook;

  return (
    <Tab.Navigator
      id="MainTabs"
      screenOptions={{
        tabBarActiveTintColor: purpleColors[2],
        tabBarInactiveTintColor: '#909090',
        tabBarStyle: {
          backgroundColor: '#F2F2F2',
        },
        headerShown: false, // Nested navigators handle their own headers
      }}
    >
      <Tab.Screen
        name="Events"
        component={EventScreensNavigator}
        options={{
          title: intlToUse.formatMessage(messages.events),
          tabBarIcon: getTabBarIcon('calendar'),
        }}
      />
      <Tab.Screen
        name="Learn"
        component={LearnScreensNavigator}
        options={{
          title: intlToUse.formatMessage(messages.learn),
          tabBarIcon: getTabBarIcon('school'),
        }}
      />
      <Tab.Screen
        name="Articles"
        component={ArticlesScreen}
        options={{
          title: intlToUse.formatMessage(messages.articles),
          tabBarIcon: getTabBarIcon('paper'),
          headerShown: true,
        }}
      />
      <Tab.Screen
        name="About"
        component={AboutScreensNavigator}
        options={{
          title: intlToUse.formatMessage(messages.about),
          tabBarIcon: getTabBarIcon('person'),
        }}
      />
    </Tab.Navigator>
  );
}

export default TabNavigatorInner;

const styles = StyleSheet.create({
  icon: {
    textAlign: 'center',
    width: semiNormalize(28),
    height: semiNormalize(28),
  },
});
