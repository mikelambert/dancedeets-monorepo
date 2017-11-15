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
  const { battleId } = navigation.state.params;
  navigation.navigate('Register', {
    battleId,
    categoryId: category.id,
  });
}

async function onUnregister(navigation, category, teamToDelete) {
  const { battleId } = navigation.state.params;
  const [teamKey] = Object.entries(category.signups || {}).filter(
    ([key, team]) => team === teamToDelete
  )[0];
  await eventUnregister(battleId, category.id, teamKey);
}

class BattleSelectorScreen extends React.Component<any> {
  static navigationOptions = ({ screenProps }) => ({
    title: 'Battle Signups',
  });

  render() {
    const { battleId } = this.props.navigation.state.params;
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

class BattleSignupsScreen extends React.Component<any> {
  static navigationOptions = ({ navigation, screenProps }) => ({
    title: `${navigation.state.params.battleId} Registration`,
  });

  render() {
    const { battleId } = this.props.navigation.state.params;
    return (
      <TrackFirebase
        path={`events/${battleId}`}
        renderContents={battleEvent => (
          <BattleEventView
            battleEvent={battleEvent}
            onSelected={selectedCategory => {
              // trackWithEvent('View Event', event);
              this.props.navigation.navigate('Category', {
                battleId,
                categoryId: selectedCategory.id,
              });
            }}
            onRegister={category => onRegister(this.props.navigation, category)}
            onUnregister={(category, teamToDelete) =>
              onUnregister(this.props.navigate, category, teamToDelete)}
          />
        )}
      />
    );
  }
}

class RegisterScreen extends React.Component<any> {
  static navigationOptions = ({ navigation, screenProps }) => {
    // TODO:
    // title: `${displayName} Registration`,
  };

  render() {
    const { battleId, categoryId } = this.props.navigation.state.params;
    return (
      <TrackFirebase
        path={`events/${battleId}`}
        renderContents={battleEvent => {
          const category = battleEvent.categories[categoryId];
          return (
            <CategorySignupScreen
              battle={this.props.battleEvent}
              category={category}
              navigation={this.props.navigation}
            />
          );
        }}
      />
    );
  }
}

class BattleHostCategory extends React.Component<any> {
  static navigationOptions = ({ navigation, screenProps }) => {
    // TODO(navigation): fix title
    /*
    const selectedCategory = null;
    return {
      title: categoryDisplayName(selectedCategory),
    };
    */
  };

  render() {
    const { battleId, categoryId } = this.props.navigation.state.params;
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

class CategoryScreen extends React.Component<any> {
  render() {
    const { battleId, categoryId } = this.props.navigation.state.params;
    return (
      <TrackFirebase
        path={`events/${battleId}`}
        renderContents={battleEvent => {
          const category = battleEvent.categories[categoryId];
          return (
            <CategoryView
              category={category}
              onRegister={category2 =>
                onRegister(this.props.navigation, category2)}
              onUnregister={(category2, teamToDelete) =>
                onUnregister(this.props.navigate, category2, teamToDelete)}
            />
          );
        }}
      />
    );
  }
}

class BattleHostScreen extends React.Component<any> {
  static navigationOptions = ({ navigation, screenProps }) => ({
    title: `${navigation.state.params.battleId} MC Host View`,
  });

  render() {
    const { battleId } = this.props.navigation.state.params;
    return (
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
      />
    );
  }
}

export const BattleScreensNavigator = StackNavigator('battle', {
  BattleSelector: { screen: BattleSelectorScreen },
  BattleSignups: { screen: BattleSignupsScreen },
  Category: { screen: CategoryScreen },
  Register: { screen: RegisterScreen },
  BattleHostView: { screen: BattleHostScreen },
});
