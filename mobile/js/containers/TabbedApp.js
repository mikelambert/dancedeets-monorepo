/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { AppState, Image, StyleSheet, View, ViewPropTypes } from 'react-native';
import TabNavigator from 'react-native-tab-navigator';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationSceneRendererProps,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { NavigationActions, StackNavigator } from 'react-navigation';
import LinearGradient from 'react-native-linear-gradient';
import { connect } from 'react-redux';
import WKWebView from 'react-native-wkwebview-reborn';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import { yellowColors, gradientBottom, gradientTop } from '../Colors';
import { semiNormalize, ZoomableImage } from '../ui';
import { selectTab } from '../actions';
import type { User } from '../actions/types';
import { track, trackWithEvent } from '../store/track';
import { TimeTracker } from '../util/timeTracker';
import { setDefaultState } from '../reducers/navigation';
import * as RemoteConfig from '../remoteConfig';
import EventScreens from './screens/Event';
import LearnScreens from './screens/Learn';
import AboutScreens from './screens/About';
import BattleScreens from './screens/Battle';

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

const mediumUrl = 'https://medium.dancedeets.com/';

class GradientTabBar extends React.Component {
  props: {
    style: ViewPropTypes.style,
    children: Array<React.Element<*>>,
  };

  render() {
    return (
      <LinearGradient
        start={{ x: 0.0, y: 0.0 }}
        end={{ x: 0.0, y: 1.0 }}
        colors={[gradientTop, gradientBottom]}
        style={this.props.style}
      >
        {this.props.children}
      </LinearGradient>
    );
  }
}

class _TabbedAppView extends React.Component {
  props: {
    // Self-managed props
    user: ?User,
    selectedTab: string,
    selectTab: (tab: string) => void,
    intl: intlShape,
  };

  state: {
    eventSignupUserIds: Array<string>,
  };

  _eventSignupsNavigator: StackNavigator;
  _eventNavigator: StackNavigator;
  _learnNavigator: StackNavigator;
  _articlesWebView: WKWebView;
  _aboutNavigator: StackNavigator;

  constructor(props) {
    super(props);
    this.state = { eventSignupUserIds: [] };
  }

  componentWillMount() {
    this.loadWhitelist();
  }

  async loadWhitelist() {
    const eventSignupUserIds =
      (await RemoteConfig.get('event_signup_user_ids')) || [];
    this.setState({ eventSignupUserIds });
  }

  icon(source) {
    return <Image source={source} style={styles.icon} />;
  }

  renderTabNavigator() {
    let extraTabs = null;
    if (
      this.props.user &&
      this.state.eventSignupUserIds.includes(this.props.user.profile.id)
    ) {
      extraTabs = (
        <TabNavigator.Item
          selected={this.props.selectedTab === 'event_signups'}
          title={'Event Signups'}
          titleStyle={styles.titleStyle}
          selectedTitleStyle={styles.selectedTitleStyle}
          renderIcon={() =>
            this.icon(require('../containers/icons/events.png'))}
          renderSelectedIcon={() =>
            this.icon(require('../containers/icons/events-highlighted.png'))}
          onPress={() => {
            if (this.props.selectedTab === 'event_signups') {
              this._eventSignupsNavigator._navigation.goBack();
            } else {
              track('Tab Selected', { Tab: 'Event Signups' });
              this.props.selectTab('event_signups');
            }
          }}
        >
          <BattleScreens
            navRef={x => {
              this._eventSignupsNavigator = x;
            }}
          />
        </TabNavigator.Item>
      );
    }
    return (
      <TabNavigator
        tabBarStyle={styles.tabBarStyle}
        sceneStyle={styles.tabBarSceneStyle}
        tabBarClass={GradientTabBar}
      >
        <TabNavigator.Item
          selected={this.props.selectedTab === 'events'}
          title={this.props.intl.formatMessage(messages.events)}
          titleStyle={styles.titleStyle}
          selectedTitleStyle={styles.selectedTitleStyle}
          renderIcon={() =>
            this.icon(require('../containers/icons/events.png'))}
          renderSelectedIcon={() =>
            this.icon(require('../containers/icons/events-highlighted.png'))}
          onPress={() => {
            if (this.props.selectedTab === 'events') {
              this._eventNavigator._navigation.goBack();
            } else {
              track('Tab Selected', { Tab: 'Events' });
              this.props.selectTab('events');
            }
          }}
        >
          <EventScreens
            navRef={nav => {
              this._eventNavigator = nav;
            }}
          />
        </TabNavigator.Item>
        <TabNavigator.Item
          selected={this.props.selectedTab === 'learn'}
          title={this.props.intl.formatMessage(messages.learn)}
          titleStyle={styles.titleStyle}
          selectedTitleStyle={styles.selectedTitleStyle}
          renderIcon={() => this.icon(require('../containers/icons/learn.png'))}
          renderSelectedIcon={() =>
            this.icon(require('../containers/icons/learn-highlighted.png'))}
          onPress={() => {
            if (this.props.selectedTab === 'learn') {
              this._learnNavigator._navigation.goBack();
            } else {
              track('Tab Selected', { Tab: 'Learn' });
              this.props.selectTab('learn');
              // this.setState({ selectedTab: 'learn' });
            }
          }}
        >
          <LearnScreens
            navRef={nav => {
              this._learnNavigator = nav;
            }}
          />
        </TabNavigator.Item>
        <TabNavigator.Item
          selected={this.props.selectedTab === 'articles'}
          title={this.props.intl.formatMessage(messages.articles)}
          titleStyle={styles.titleStyle}
          selectedTitleStyle={styles.selectedTitleStyle}
          renderIcon={() =>
            this.icon(require('../containers/icons/articles.png'))}
          renderSelectedIcon={() =>
            this.icon(require('../containers/icons/articles-highlighted.png'))}
          onPress={() => {
            if (this.props.selectedTab === 'articles') {
              this._articlesWebView.evaluateJavaScript(
                `window.location = "${mediumUrl}"`
              );
            } else {
              track('Tab Selected', { Tab: 'Articles' });
              this.props.selectTab('articles');
            }
          }}
        >
          <WKWebView
            ref={webView => {
              this._articlesWebView = webView;
            }}
            source={{ uri: mediumUrl }}
          />
        </TabNavigator.Item>
        <TabNavigator.Item
          selected={this.props.selectedTab === 'about'}
          title={this.props.intl.formatMessage(messages.about)}
          titleStyle={styles.titleStyle}
          selectedTitleStyle={styles.selectedTitleStyle}
          renderIcon={() =>
            this.icon(require('../containers/icons/profile.png'))}
          renderSelectedIcon={() =>
            this.icon(require('../containers/icons/profile-highlighted.png'))}
          onPress={() => {
            if (this.props.selectedTab === 'about') {
              this._aboutNavigator._navigation.goBack();
            } else {
              track('Tab Selected', { Tab: 'About' });
              this.props.selectTab('about');
            }
          }}
        >
          <AboutScreens
            navRef={nav => {
              this._aboutNavigator = nav;
            }}
          />
        </TabNavigator.Item>
        {extraTabs}
      </TabNavigator>
    );
  }

  render() {
    return (
      <TimeTracker eventName="Tab Time" eventValue={this.props.selectedTab}>
        {this.renderTabNavigator()}
      </TimeTracker>
    );
  }
}
export default connect(
  state => ({
    user: state.user.userData,
    selectedTab: state.mainTabs.selectedTab,
  }),
  dispatch => ({
    selectTab: x => dispatch(selectTab(x)),
  })
)(injectIntl(_TabbedAppView));

const tabBarHeight = semiNormalize(52);

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
