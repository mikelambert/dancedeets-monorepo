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

  render() {
    return <TabNavigator tabBarStyle={styles.tabBarStyle} tabBarClass={GradientTabBar}>
      <TabNavigator.Item
        selected={this.state.selectedTab === 'home'}
        title="Events"
        titleStyle={styles.titleStyle}
        selectedTitleStyle={styles.selectedTitleStyle}
        renderIcon={() => <Image source={require('../containers/icons/events.png')} />}
        renderSelectedIcon={() => <Image source={require('../containers/icons/events-highlighted.png')} />}
        onPress={() => this.setState({ selectedTab: 'home' })}>
        <AppContainer />
      </TabNavigator.Item>
      <TabNavigator.Item
        selected={this.state.selectedTab === 'about'}
        title="App"
        titleStyle={styles.titleStyle}
        selectedTitleStyle={styles.selectedTitleStyle}
        renderIcon={() => <Image source={require('../containers/icons/profile.png')} />}
        renderSelectedIcon={() => <Image source={require('../containers/icons/profile-highlighted.png')} />}
        onPress={() => this.setState({ selectedTab: 'about' })}>
        <AboutApp />
      </TabNavigator.Item>
    </TabNavigator>;
  }
}


let styles = StyleSheet.create({

  tabBarStyle: {
    backgroundColor: 'transparent',
  },
  titleStyle: {
    color: 'white',
  },
  selectedTitleStyle: {
    color: yellowColors[1],
  },
});
