/**
 * Copyright 2016 DanceDeets.
 *
 * React Navigation v6 Learn screens
 */

import * as React from 'react';
import { createStackNavigator, StackScreenProps } from '@react-navigation/stack';
import { useIntl, defineMessages } from 'react-intl';
import { track } from '../../store/track';
import {
  PlaylistListView,
  PlaylistStylesView,
  PlaylistView,
} from '../../learn/playlistViews';
import { gradientTop } from '../../Colors';

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

// Type definitions for navigation
type LearnStackParamList = {
  TutorialStyles: undefined;
  TutorialList: { category: any };
  Tutorial: { playlist: any };
};

const Stack = createStackNavigator<LearnStackParamList>();

// Tutorial Styles View Screen
interface TutorialStylesViewProps extends StackScreenProps<LearnStackParamList, 'TutorialStyles'> {}

function TutorialStylesViewScreen({ navigation }: TutorialStylesViewProps) {
  const onSelected = (category: any) => {
    track('Tutorial Style Selected', {
      tutorialStyle: category.style.title,
    });
    navigation.navigate('TutorialList', { category });
  };

  return <PlaylistStylesView onSelected={onSelected} />;
}

// Tutorial List View Screen
interface TutorialListViewProps extends StackScreenProps<LearnStackParamList, 'TutorialList'> {}

function TutorialListViewScreen({ navigation, route }: TutorialListViewProps) {
  const { category } = route.params;

  const onSelected = (playlist: any) => {
    track('Tutorial Selected', {
      tutorialName: playlist.title,
      tutorialStyle: playlist.style,
    });
    navigation.navigate('Tutorial', { playlist });
  };

  return (
    <PlaylistListView
      playlists={category.tutorials}
      onSelected={onSelected}
    />
  );
}

// Tutorial View Screen
interface TutorialViewProps extends StackScreenProps<LearnStackParamList, 'Tutorial'> {}

function TutorialViewScreen({ route }: TutorialViewProps) {
  const { playlist } = route.params;
  return <PlaylistView playlist={playlist} />;
}

// Main Learn Screens Navigator
export function LearnScreensNavigator() {
  const intl = useIntl();

  return (
    <Stack.Navigator
      screenOptions={{
        headerTintColor: 'white',
        headerStyle: {
          backgroundColor: gradientTop,
        },
        cardStyle: {
          backgroundColor: '#E9E9EF',
        },
      }}
    >
      <Stack.Screen
        name="TutorialStyles"
        component={TutorialStylesViewScreen}
        options={{
          title: intl.formatMessage(messages.learnTitle),
        }}
      />
      <Stack.Screen
        name="TutorialList"
        component={TutorialListViewScreen}
        options={({ route }) => ({
          title: intl.formatMessage(messages.styleTutorialTitle, {
            style: route.params.category.style.title,
          }),
        })}
      />
      <Stack.Screen
        name="Tutorial"
        component={TutorialViewScreen}
        options={({ route }) => ({
          title: route.params.playlist.title,
        })}
      />
    </Stack.Navigator>
  );
}
