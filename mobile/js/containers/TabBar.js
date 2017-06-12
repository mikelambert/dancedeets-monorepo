/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Image, StyleSheet } from 'react-native';
import {
  addNavigationHelpers,
  TabBarBottom,
  TabNavigator,
} from 'react-navigation';
import type { SceneRendererProps } from 'react-native-tab-view/src/TabViewTypeDefinitions';
import { connect } from 'react-redux';
import WKWebView from 'react-native-wkwebview-reborn';
import {
  EventScreensNavigator,
  EventScreensView,
  LearnScreensView,
  AboutScreensView,
  BattleScreensView,
} from './screens';
import { semiNormalize } from '../ui';
import type { Dispatch } from '../actions/types';

function image(focused, focusedSource, unfocusedSource) {
  return (
    <Image
      source={focused ? focusedSource : unfocusedSource}
      style={styles.icon}
    />
  );
}

const mediumUrl = 'https://medium.dancedeets.com/';

const routeConfiguration = {
  Events: {
    screen: EventScreensView,
    onSameTabClick: ({ navigation }) => navigation.goBack(),
    navigationOptions: {
      tabBarIcon: ({ focused }) =>
        image(
          focused,
          require('../containers/icons/events-highlighted.png'),
          require('../containers/icons/events.png')
        ),
    },
  },
  Tutorials: {
    screen: LearnScreensView,
    onSameTabClick: ({ navigation }) => navigation.goBack(),
    navigationOptions: {
      tabBarIcon: ({ focused }) =>
        image(
          focused,
          require('../containers/icons/learn-highlighted.png'),
          require('../containers/icons/learn.png')
        ),
    },
  },
  Articles: {
    screen: () => <WKWebView source={{ uri: mediumUrl }} />,
    onSameTabClick: obj => navigation.goBack(),
    navigationOptions: {
      tabBarIcon: ({ focused }) =>
        image(
          focused,
          require('../containers/icons/articles-highlighted.png'),
          require('../containers/icons/articles.png')
        ),
    },
  },
  About: {
    screen: AboutScreensView,
    onSameTabClick: ({ navigation }) => navigation.goBack(),
    navigationOptions: {
      tabBarIcon: ({ focused }) =>
        image(
          focused,
          require('../containers/icons/profile-highlighted.png'),
          require('../containers/icons/profile.png')
        ),
    },
  },
};

class SameClickTabBar extends React.PureComponent {
  props: SceneRendererProps<*> & {
    navigation: any, // NavigationScreenProp<NavigationState, NavigationAction>,
  };

  jumpToIndex(i) {
    // check if clicked on same tab
    if (i === this.props.navigationState.index) {
      const route = this.props.navigationState.routes[i];
      const routeConfig = routeConfiguration[route.key];
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
    //activeTintColor: 'white',
    //inactiveTintColor: 'blue',
    // background color is for the tab component
    //activeBackgroundColor: 'blue',
    //inactiveBackgroundColor: 'white',
  },
  backBehavior: 'none',
};

export default TabNavigator(routeConfiguration, tabBarConfiguration);

let styles = StyleSheet.create({
  icon: {
    width: semiNormalize(28),
    height: semiNormalize(28),
  },
});
