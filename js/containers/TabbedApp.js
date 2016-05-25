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
import Profile from '../containers/Profile';
import { yellowColors } from '../Colors';
import LinearGradient from 'react-native-linear-gradient';

class GrandientTabBar extends React.Component {
  render() {
    return <LinearGradient
      start={[0.0, 0.0]} end={[0.0, 1]}
      colors={['#5F70B6', '#4F5086']}
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
    return <TabNavigator tabBarStyle={styles.tabBarStyle} tabBarClass={GrandientTabBar}>
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
        selected={this.state.selectedTab === 'profile'}
        title="Profile"
        titleStyle={styles.titleStyle}
        selectedTitleStyle={styles.selectedTitleStyle}
        renderIcon={() => <Image source={require('../containers/icons/profile.png')} />}
        renderSelectedIcon={() => <Image source={require('../containers/icons/profile-highlighted.png')} />}
        onPress={() => this.setState({ selectedTab: 'profile' })}>
        <Profile />
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
