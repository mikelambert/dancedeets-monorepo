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
import generateAppContainer from '../containers/generateAppContainer';
import AboutApp from '../containers/Profile';
import LearnApp from '../containers/Learn';
import { yellowColors, gradientBottom, gradientTop } from '../Colors';
import LinearGradient from 'react-native-linear-gradient';
import {
  semiNormalize,
} from '../ui';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import EventListContainer from '../events/list';
import EventPager from '../events/EventPager';
import {
  ZoomableImage,
} from '../ui';
import AddEvents from '../containers/AddEvents';
import { track, trackWithEvent } from '../store/track';

const AppContainer = generateAppContainer('EVENT_NAV');

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
    defaultMessage: 'Events',
    description: 'Tab button to show list of events',
  },
  learn: {
    id: 'tab.learn',
    defaultMessage: 'Learn',
    description: 'Tab button to help folks learn about dance',
  },
  about: {
    id: 'tab.about',
    defaultMessage: 'About',
    description: 'Tab button to show general info about Dancedeets, Profile, and Share info',
  },
  addEvent: {
    id: 'navigator.addEvent',
    defaultMessage: 'Add Event',
    description: 'Title Bar for Adding Event',
  },
  viewFlyer: {
    id: 'navigator.viewFlyer',
    defaultMessage: 'View Flyer',
    description: 'Title Bar for Viewing Flyer',
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

  renderEventScene(scene, navigatable) {
    const { route } = scene;
    switch (route.key) {
    case 'EventList':
      return <EventListContainer
        onEventSelected={(event)=> {
          trackWithEvent('View Event', event);
          navigatable.onNavigate({key: 'EventView', title: event.name, event: event});
        }}
        onAddEventClicked={(source) => {
          track('Add Event', {source: source});
          navigatable.onNavigate({key: 'AddEvent', title: this.props.intl.formatMessage(messages.addEvent)});
        }}
      />;
    case 'EventView':
      return <EventPager
        onEventNavigated={(event)=> {
          trackWithEvent('View Event', event);
          navigatable.onSwap('EventView', {key: 'EventView', title: event.name, event: event});
        }}
        onFlyerSelected={(event)=> {
          trackWithEvent('View Flyer', event);
          navigatable.onNavigate({
            key: 'FlyerView',
            title: this.props.intl.formatMessage(messages.viewFlyer),
            image: event.cover.images[0].source,
            width: event.cover.images[0].width,
            height: event.cover.images[0].height,
          });
        }}
        selectedEvent={route.event}
      />;
    case 'FlyerView':
      return <ZoomableImage
        url={route.image}
        width={route.width}
        height={route.height}
      />;
    case 'AddEvent':
      return <AddEvents />;
    }
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
        <AppContainer
          ref="app_container"
          renderScene={this.renderEventScene}
          />
      </TabNavigator.Item>
      <TabNavigator.Item
        selected={this.state.selectedTab === 'learn'}
        title={intl.formatMessage(messages.learn)}
        titleStyle={styles.titleStyle}
        selectedTitleStyle={styles.selectedTitleStyle}
        renderIcon={() => this.icon(require('../containers/icons/learn.png'))}
        renderSelectedIcon={() => this.icon(require('../containers/icons/learn-highlighted.png'))}
        onPress={() => {
          if (this.state.selectedTab !== 'learn') {
            track('Tab Selected', {Tab: 'Learn'});
            this.setState({ selectedTab: 'learn' });
          }
        }}>
        <LearnApp />
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
