/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import TabNavigator from 'react-native-tab-navigator';
import AppContainer from '../containers/AppContainer';
import Profile from '../containers/Profile';

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
    return <TabNavigator>
      <TabNavigator.Item
        selected={this.state.selectedTab === 'home'}
        title="Events"
        //renderIcon={() => <Image source={...} />}
        //renderSelectedIcon={() => <Image source={...} />}
        onPress={() => this.setState({ selectedTab: 'home' })}>
        <AppContainer />
      </TabNavigator.Item>
      <TabNavigator.Item
        selected={this.state.selectedTab === 'profile'}
        title="Profile"
        //renderIcon={() => <Image source={...} />}
        //renderSelectedIcon={() => <Image source={...} />}
        onPress={() => this.setState({ selectedTab: 'profile' })}>
        <Profile />
      </TabNavigator.Item>
    </TabNavigator>;
  }
}
