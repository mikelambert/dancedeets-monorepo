/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Image,
  StyleSheet,
} from 'react-native';
import TabNavigator from 'react-native-tab-navigator';
import generateNavigator from '../containers/generateNavigator';
import AboutApp from '../containers/Profile';
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
  BlogList,
  BlogPostList,
  BlogPostContents,
} from '../learn/BlogList';
import {
  ZoomableImage,
} from '../ui';
import AddEvents from '../containers/AddEvents';
import { track, trackWithEvent } from '../store/track';
import { setDefaultState } from '../reducers/navigation';
import {
  PlaylistListView,
  PlaylistStylesView,
  PlaylistView,
} from '../learn/playlistViews';

const EventNavigator = generateNavigator('EVENT_NAV');
setDefaultState('EVENT_NAV', { key: 'EventList', title: 'DanceDeets' });

const LearnNavigator = generateNavigator('LEARN_NAV');
setDefaultState('LEARN_NAV', { key: 'TutorialStyles', title: 'Learn' });

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
  //TODO: move this to redux state!
  state: {
    selectedTab: string,
  };

  constructor(props: any) {
    super(props);
    this.state = {
      selectedTab: 'home',
    };
    (this: any).renderEventScene = this.renderEventScene.bind(this);
    (this: any).renderLearnScene = this.renderLearnScene.bind(this);
  }

  icon(source) {
    return <Image source={source} style={styles.icon}/>;
  }

  renderEventScene(scene, navigatable) {
    const { route } = scene;
    switch (route.key) {
    case 'EventList':
      return <EventListContainer
        onEventSelected={(event) => {
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

  renderLearnScene(scene, navigatable) {
    const { route } = scene;
    switch (route.key) {
    case 'BlogList':
      return <BlogList
        onSelected={(blog) => {
          // TODO: Track blog details
          track('Blog Selected');
          //navigatable.onNavigate({key: 'BlogPostList', title: blog.title, blog: blog});
          navigatable.onNavigate({key: 'Tutorial', title: blog.title, tutorial: blog});
        }}
        />;
    case 'TutorialStyles':
      return <PlaylistStylesView
        onSelected={(style) => {
          track('Tutorial Style Selected', {
            tutorialStyle: style.title,
          });
          navigatable.onNavigate({key: 'TutorialList', title: style.title, tutorials: style.tutorials});
        }}
        />;
    case 'TutorialList':
      return <PlaylistListView
        playlists={route.tutorials}
        onSelected={(playlist) => {
          track('Tutorial Selected', {
            tutorialName: playlist.title,
            tutorialStyle: playlist.style,
          });
          navigatable.onNavigate({key: 'Tutorial', title: playlist.title, tutorial: playlist});
        }}
        />;
    case 'Tutorial':
      return <PlaylistView
        playlist={route.tutorial}
        />;
    case 'BlogPostList':
      return <BlogPostList
        blog={route.blog}
        onSelected={(post) => {
          // TODO: Track post details
          track('Blog Post Selected');
          navigatable.onNavigate({key: 'BlogPostItem', title: post.title, post: post});
        }}
        />;
    case 'BlogPostItem':
      return <BlogPostContents
        post={route.post}
        />;
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
            this.refs.event_navigator.dispatchProps.goHome();
          } else {
            track('Tab Selected', {Tab: 'Home'});
            this.setState({ selectedTab: 'home' });
          }
        }}>
        <EventNavigator
          ref="event_navigator"
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
          if (this.state.selectedTab === 'learn') {
            this.refs.learn_navigator.dispatchProps.goHome();
          } else {
            track('Tab Selected', {Tab: 'Learn'});
            this.setState({ selectedTab: 'learn' });
          }
        }}>
        <LearnNavigator
          ref="learn_navigator"
          renderScene={this.renderLearnScene}
          />
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
