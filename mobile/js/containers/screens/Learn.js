/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { defineMessages } from 'react-intl';
import { track } from '../../store/track';
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

class TutorialStylesView extends React.Component<{
  navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
}> {
  static navigationOptions = ({ screenProps }) => ({
    title: screenProps.intl.formatMessage(messages.learnTitle),
  });

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

class TutorialListView extends React.Component<{
  navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
}> {
  static navigationOptions = ({ navigation, screenProps }) => {
    const { category } = navigation.state.params;
    return {
      title: screenProps.intl.formatMessage(messages.styleTutorialTitle, {
        style: category.style.title,
      }),
    };
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
    const { category } = this.props.navigation.state.params;
    return (
      <PlaylistListView
        playlists={category.tutorials}
        onSelected={this.onSelected}
      />
    );
  }
}

class TutorialView extends React.Component<{
  navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
}> {
  static navigationOptions = ({ navigation, screenProps }) => {
    const { playlist } = navigation.state.params;
    return { title: playlist.title };
  };

  render() {
    const { playlist } = this.props.navigation.state.params;
    return <PlaylistView playlist={playlist} />;
  }
}

export const LearnScreensNavigator = StackNavigator(
  'learn',
  {
    TutorialStyles: { screen: TutorialStylesView },
    TutorialList: { screen: TutorialListView },
    Tutorial: { screen: TutorialView },
  },
  {
    cardStyle: {
      backgroundColor: '#E9E9EF',
    },
  }
);
