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
import {
  semiNormalize,
} from '../ui';
import {
  injectIntl,
  defineMessages,
} from 'react-intl'

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

const messages = defineMessages({
  events: {
    id: 'tab.events',
    defaultMessag: 'Events',
  },
  about: {
    id: 'tab.about',
    defaultMessag: 'About',
  },
});

class _TabbedAppView extends React.Component {
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
    const {intl} = this.props;
    return <TabNavigator
        tabBarStyle={styles.tabBarStyle}
        sceneStyle={styles.tabBarSceneStyle}
        tabBarClass={GradientTabBar}
      >
      <TabNavigator.Item
        selected={this.state.selectedTab === 'home'}
        title={intl.formatMessage(messages.events)}
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
        title={intl.formatMessage(messages.about)}
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
export default injectIntl(_TabbedAppView);

var tabBarHeight = semiNormalize(52);

let styles = StyleSheet.create({
  icon: {
    width: semiNormalize(28),
    height: semiNormalize(28),
  },
  tabBarStyle: {
    backgroundColor: 'transparent',
    height: tabBarHeight,
  },
  tabBarSceneStyle: {
    paddingBottom: tabBarHeight,
  },
  titleStyle: {
    color: 'white',
    fontSize: semiNormalize(14),
  },
  selectedTitleStyle: {
    color: yellowColors[1],
  },
});
