/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Image,
  StyleSheet
} from 'react-native';
import TabNavigator from 'react-native-tab-navigator';
import AppContainer from '../containers/AppContainer';
import AboutApp from '../containers/Profile';
import { yellowColors, gradientBottom, gradientTop } from '../Colors';
import LinearGradient from 'react-native-linear-gradient';
import { track } from '../store/track';
import normalize from '../ui/normalize';

class GradientTabBar extends React.Component {
  render() {
    return <LinearGradient
      start={[0.0, 0.0]} end={[0.0, 1]}
      colors={[gradientTop, gradientBottom]}
      style={this.props.style}>
      {this.props.children}
    </LinearGradient>;
  }
}

export default class TabbedAppView extends React.Component {
  state: {
    selectedTab: string,
  };

  constructor(props: any) {
    super(props);
    this.state = {
      selectedTab: 'home',
    };
  }

  icon(source) {
    return <Image source={source} style={styles.icon}/>;
  }

  render() {
    return <TabNavigator tabBarStyle={styles.tabBarStyle} tabBarClass={GradientTabBar}>
      <TabNavigator.Item
        selected={this.state.selectedTab === 'home'}
        title="Events"
        titleStyle={styles.titleStyle}
        selectedTitleStyle={styles.selectedTitleStyle}
        renderIcon={() => this.icon(require('../containers/icons/events.png'))}
        renderSelectedIcon={() => this.icon(require('../containers/icons/events-highlighted.png'))}
        onPress={() => {
          if (this.state.selectedTab === 'home') {
            this.refs.app_container.dispatchProps.goHome();
          } else {
            track('Tab Selected', {Tab: 'Home'});
            this.setState({ selectedTab: 'home' });
          }
        }}>
        <AppContainer ref="app_container" />
      </TabNavigator.Item>
      <TabNavigator.Item
        selected={this.state.selectedTab === 'about'}
        title="About"
        titleStyle={styles.titleStyle}
        selectedTitleStyle={styles.selectedTitleStyle}
        renderIcon={() => this.icon(require('../containers/icons/profile.png'))}
        renderSelectedIcon={() => this.icon(require('../containers/icons/profile-highlighted.png'))}
        onPress={() => {
          if (this.state.selectedTab !== 'about') {
            track('Tab Selected', {Tab: 'About'});
            this.setState({ selectedTab: 'about' });
          }
        }}>
        <AboutApp />
      </TabNavigator.Item>
    </TabNavigator>;
  }
}


let styles = StyleSheet.create({
  icon: {
    width: normalize(30),
    height: normalize(30),
  },
  tabBarStyle: {
    backgroundColor: 'transparent',
    height: normalize(49),
  },
  titleStyle: {
    color: 'white',
    fontSize: normalize(14),
  },
  selectedTitleStyle: {
    color: yellowColors[1],
  },
});
