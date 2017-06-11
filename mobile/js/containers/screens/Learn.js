/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { AppState, Image, StyleSheet, View } from 'react-native';
import TabNavigator from 'react-native-tab-navigator';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationSceneRendererProps,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { NavigationActions } from 'react-navigation';
import { connect } from 'react-redux';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import { track, trackWithEvent } from '../../store/track';
import {
  PlaylistListView,
  PlaylistStylesView,
  PlaylistView,
} from '../../learn/playlistViews';
import StackNavigator from './Navigator';

const messages = defineMessages({
  learnTitle: {
    id: 'tutorialVideos.navigatorTitle',
    defaultMessage: 'Tutorials',
    description: 'Initial title bar for Learn tab',
  },
  styleTutorialTitle: {
    id: 'tutorialVideos.styleTutorialTitle',
    defaultMessage: '{style} Tutorials',
    description: "Title Bar for viewing a given style's tutorials",
  },
});

class TutorialStylesView extends React.Component {
  static navigationOptions = ({ screenProps }) => ({
    title: screenProps.intl.formatMessage(messages.learnTitle),
  });

  props: {
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
  };

  constructor(props) {
    super(props);
    (this: any).onSelected = this.onSelected.bind(this);
  }

  onSelected(category) {
    track('Tutorial Style Selected', {
      tutorialStyle: category.style.title,
    });
    this.props.navigation.navigate('TutorialList', { category });
  }

  render() {
    return <PlaylistStylesView onSelected={this.onSelected} />;
  }
}

class TutorialListView extends React.Component {
  static navigationOptions = ({ navigation, screenProps }) => {
    const category = navigation.state.params.category;
    return {
      title: screenProps.intl.formatMessage(messages.styleTutorialTitle, {
        style: category.style.title,
      }),
    };
  };

  props: {
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
  };

  constructor(props) {
    super(props);
    (this: any).onSelected = this.onSelected.bind(this);
  }

  onSelected(playlist) {
    track('Tutorial Selected', {
      tutorialName: playlist.title,
      tutorialStyle: playlist.style,
    });
    this.props.navigation.navigate('Tutorial', { playlist });
  }

  render() {
    const category: any = this.props.navigation.state.params.category;
    return (
      <PlaylistListView
        playlists={category.tutorials}
        onSelected={this.onSelected}
      />
    );
  }
}

class TutorialView extends React.Component {
  static navigationOptions = ({ navigation, screenProps }) => {
    const playlist = navigation.state.params.playlist;
    return { title: playlist.title };
  };

  props: {
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
  };

  render() {
    const playlist = this.props.navigation.state.params.playlist;
    return <PlaylistView playlist={playlist} />;
  }
}

export const LearnScreensNavigator = StackNavigator({
  TutorialStyles: { screen: TutorialStylesView },
  TutorialList: { screen: TutorialListView },
  Tutorial: { screen: TutorialView },
});

class _LearnScreensView extends React.Component {
  props: {
    navRef: (nav: StackNavigator) => void,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    return (
      <LearnScreensNavigator
        ref={nav => this.props.navRef(nav)}
        screenProps={{
          intl: this.props.intl,
        }}
      />
    );
  }
}

export const LearnScreensView = injectIntl(_LearnScreensView);
