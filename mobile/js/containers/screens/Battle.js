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
import { categoryDisplayName } from '../../event_signups/models';
import { BattleSelector } from '../../event_signups/views';
import { TrackFirebase } from '../../firestack';
import CategorySignupScreen from '../../event_signups/categorySignupScreen';
import CategoryView from '../../event_signups/categoryView';
import BattleEventView from '../../event_signups/battleEventView';
import BattleEventHostView from '../../event_signups/battleEventHostView';
import BattleHostCategoryView from '../../event_signups/battleHostCategoryView';
import { eventRegister, eventUnregister } from '../../api/dancedeets';
import StackNavigator from './Navigator';

const messages = defineMessages({});

function onRegister(navigation, category) {
  const battleId = navigation.state.params.battleId;
  const displayName = categoryDisplayName(category);
  navigation.navigate('Register', {
    battleId,
    categoryId: category.id,
  });
}

async function onUnregister(navigation, category, teamToDelete) {
  const battleId = navigation.state.params.battleId;
  const [teamKey] = Object.entries(category.signups || {}).filter(
    ([key, team]) => team === teamToDelete
  )[0];
  await eventUnregister(battleId, category.id, teamKey);
}

class BattleSelectorScreen extends React.Component {
  static navigationOptions = ({ screenProps }) => ({
    title: 'Battle Signups',
  });

  render() {
    const battleId = this.props.navigation.state.params.battleId;
    return (
      <BattleSelector
        onBattleSelected={() =>
          this.props.navigation.navigate('BattleSignups', { battleId })}
        onBattleHostSelected={() =>
          this.props.navigation.navigate('BattleHostView', { battleId })}
      />
    );
  }
}

class BattleSignupsScreen extends React.Component {
  static navigationOptions = ({ navigation, screenProps }) => ({
    title: `${navigation.state.params.battleId} Registration`,
  });

  constructor(props) {
    super(props);
  }

  render() {
    const battleId = this.props.navigation.state.params.battleId;
    const categoryId = this.props.navigation.state.params.categoryId;
    return (
      <TrackFirebase
        path={`events/${battleId}`}
        renderContents={battleEvent => {
          return (
            <BattleEventView
              battleEvent={battleEvent}
              onSelected={selectedCategory => {
                // trackWithEvent('View Event', event);
                const displayName = categoryDisplayName(selectedCategory);
                this.props.navigation.navigate('Category', {
                  battleId: battleId,
                  categoryId: selectedCategory.id,
                });
              }}
              onRegister={category =>
                onRegister(this.props.navigation, category)}
              onUnregister={(category, teamToDelete) =>
                onUnregister(this.props.navigate, category, teamToDelete)}
            />
          );
        }}
      />
    );
  }
}

class RegisterScreen extends React.Component {
  static navigationOptions = ({ navigation, screenProps }) => {
    //TODO:
    // title: `${displayName} Registration`,
  };

  render() {
    const battleId = this.props.navigation.state.params.battleId;
    const categoryId = this.props.navigation.state.params.categoryId;
    return (
      <TrackFirebase
        path={`events/${battleId}`}
        renderContents={battleEvent => {
          const category = battleEvent.categories[categoryId];
          return (
            <CategorySignupScreen
              battle={this.props.battleEvent}
              category={category}
            />
          );
        }}
      />
    );
  }
}

class BattleHostCategory extends React.Component {
  static navigationOptions = ({ navigation, screenProps }) => {
    //TODO(navigation): fix title
    /*
    const selectedCategory = null;
    return {
      title: categoryDisplayName(selectedCategory),
    };
    */
  };

  render() {
    const battleId = this.props.navigation.state.params.battleId;
    const categoryId = this.props.navigation.state.params.categoryId;
    return (
      <TrackFirebase
        path={`events/${battleId}`}
        renderContents={battleEvent => {
          const category = battleEvent.categories[categoryId];
          return <BattleHostCategoryView category={category} />;
        }}
      />
    );
  }
}

class CategoryScreen extends React.Component {
  render() {
    const battleId = this.props.navigation.state.params.battleId;
    const categoryId = this.props.navigation.state.params.categoryId;
    return (
      <TrackFirebase
        path={`events/${battleId}`}
        renderContents={battleEvent => {
          const category = battleEvent.categories[categoryId];
          return (
            <CategoryView
              category={category}
              onRegister={category =>
                onRegister(this.props.navigation, category)}
              onUnregister={(category, teamToDelete) =>
                onUnregister(this.props.navigate, category, teamToDelete)}
            />
          );
        }}
      />
    );
  }
}

class BattleHostScreen extends React.Component {
  static navigationOptions = ({ navigation, screenProps }) => ({
    title: `${navigation.state.params.battleId} MC Host View`,
  });

  render() {
    const battleId = this.props.navigation.state.params.battleId;
    <TrackFirebase
      path={`events/${battleId}`}
      renderContents={battleEvent => (
        <BattleEventHostView
          battleEvent={battleEvent}
          onSelected={selectedCategory => {
            // trackWithEvent('View Event', event);
            this.props.navigation.navigate('BattleHostCategory', {
              battleId,
              categoryId: selectedCategory.id,
            });
          }}
        />
      )}
    />;
  }
}

const BattleScreens = StackNavigator({
  BattleSelector: { screen: BattleSelectorScreen },
  BattleSignups: { screen: BattleSignupsScreen },
  Category: { screen: CategoryScreen },
  Register: { screen: RegisterScreen },
  BattleHostView: { screen: BattleHostScreen },
});

class _BattleScreensView extends React.Component {
  props: {
    navRef: (nav: StackNavigator) => void,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    return (
      <BattleScreens
        ref={nav => this.props.navRef(nav)}
        screenProps={{
          intl: this.props.intl,
        }}
      />
    );
  }
}

export default injectIntl(_BattleScreensView);
