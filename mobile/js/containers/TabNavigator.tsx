/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Platform, StyleSheet, WebView } from 'react-native';
import { TabBarBottom, TabNavigator } from 'react-navigation';
import type { SceneRendererProps } from 'react-native-tab-view/src/TabViewTypeDefinitions';
import { defineMessages } from 'react-intl';
import WKWebView from 'react-native-wkwebview-reborn';
import Icon from 'react-native-vector-icons/Ionicons';
import {
  EventScreensNavigator,
  LearnScreensNavigator,
  AboutScreensNavigator,
} from './screens';
import { semiNormalize } from '../ui';
import { purpleColors } from '../Colors';

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

function image(focused: boolean, name: string) {
  let imageName = null;
  if (Platform.OS === 'android') {
    imageName = `md-${name}`;
  } else if (Platform.OS === 'ios') {
    if (focused) {
      imageName = `ios-${name}`;
    } else {
      imageName = `ios-${name}-outline`;
    }
  }
  const color = focused ? purpleColors[2] : '#909090';
  return <Icon name={imageName} size={30} style={styles.icon} color={color} />;
}

const mediumUrl =
  'https://medium.dancedeets.com/?utm_source=articles_tab&utm_medium=mobile_app&utm_campaign=articles_tab';

class ArticlesScreensNavigator extends React.Component<{}> {
  render() {
    if (Platform.OS === 'ios') {
      return <WKWebView source={{ uri: mediumUrl }} />;
    } else {
      return <WebView source={{ uri: mediumUrl }} />;
    }
  }
}

const routeConfiguration = {
  Events: {
    screen: EventScreensNavigator,
    onSameTabClick: ({ navigation }: any) => navigation.goBack(),
    navigationOptions: ({ screenProps }: any) => ({
      title: screenProps.intl.formatMessage(messages.events),
      tabBarIcon: ({ focused }: any) => image(focused, 'calendar'),
    }),
  },
  Learn: {
    screen: LearnScreensNavigator,
    onSameTabClick: ({ navigation }: any) => navigation.goBack(),
    navigationOptions: ({ screenProps }: any) => ({
      title: screenProps.intl.formatMessage(messages.learn),
      tabBarIcon: ({ focused }: any) => image(focused, 'school'),
    }),
  },
  Articles: {
    screen: ArticlesScreensNavigator,
    onSameTabClick: ({ navigation }: any) =>
      console.log('Cannot go back on Articles tab'),
    navigationOptions: ({ screenProps }: any) => ({
      title: screenProps.intl.formatMessage(messages.articles),
      tabBarIcon: ({ focused }: any) => image(focused, 'paper'),
    }),
  },
  About: {
    screen: AboutScreensNavigator,
    onSameTabClick: ({ navigation }: any) => navigation.goBack(),
    navigationOptions: ({ screenProps }: any) => ({
      title: screenProps.intl.formatMessage(messages.about),
      tabBarIcon: ({ focused }: any) => image(focused, 'person'),
    }),
  },
};

interface SameClickProps extends SceneRendererProps<any> {
  navigation: any;
  jumpToIndex: (index: number) => void;
}

class SameClickTabBar extends React.PureComponent<SameClickProps> {
  jumpToIndex(i: number) {
    // check if clicked on same tab
    if (i === this.props.navigationState.index) {
      const route = this.props.navigationState.routes[i];
      const routeConfig = (routeConfiguration as any)[route.key];
      if (routeConfig.onSameTabClick) {
        routeConfig.onSameTabClick(this.props);
      }
    }
    this.props.jumpToIndex(i);
  }

  render() {
    return (
      <TabBarBottom {...this.props} jumpToIndex={i => this.jumpToIndex(i)} />
    );
  }
}

const tabBarConfiguration = {
  // Use iOS bottom navigation system
  ...TabNavigator.Presets.iOSBottomTabs,
  // but override the tabbar with one that handles same-clicks
  tabBarComponent: SameClickTabBar,

  tabBarOptions: {
    // tint color is passed to text and icons (if enabled) on the tab bar
    activeTintColor: purpleColors[2],
    inactiveTintColor: '#909090',
    // background color is for the tab component
    activeBackgroundColor: '#F2F2F2',
    inactiveBackgroundColor: '#F2F2F2',
  },
  backBehavior: 'none',
};

export default TabNavigator(routeConfiguration, tabBarConfiguration);

let styles = StyleSheet.create({
  icon: {
    textAlign: 'center',
    width: semiNormalize(28),
    height: semiNormalize(28),
  },
});
