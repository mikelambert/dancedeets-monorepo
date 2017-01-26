/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Animated,
  Dimensions,
  Image,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import { connect } from 'react-redux';
import { GiftedForm } from 'react-native-gifted-form';
import type {
  NavigationRoute,
  NavigationScene,
  NavigationSceneRendererProps,
  NavigationState,
} from 'react-native/Libraries/NavigationExperimental/NavigationTypeDefinition';
import { track } from '../store/track';
import { FeedListView } from '../learn/BlogList';
import {
  Button,
  Card,
  HorizontalView,
  MyGiftedForm,
  MyGiftedSubmitWidget,
  normalize,
  ProportionalImage,
  semiNormalize,
  Text,
} from '../ui';
import {
  purpleColors,
  yellowColors,
} from '../Colors';
import {
  navigatePop,
  navigatePush,
} from '../actions';
import type {
  Dispatch,
  User,
} from '../actions/types';
import {
  categoryDisplayName,
} from './models';
import type {
  BattleCategory,
  BattleEvent,
  Signup,
} from './models';
import type {
  Navigatable,
} from '../containers/generateNavigator';
import {
  eventRegister,
  eventUnregister,
} from '../api/dancedeets';
import {
  TrackFirebase,
} from '../firestack';
import CategorySignupScreen from './categorySignupScreen';
import CategoryView from './categoryView';
import BattleEventView from './battleEventView';
import BattleEventHostView from './battleEventHostView';
import BattleHostCategoryView from './battleHostCategoryView';

type GiftedNavigationSceneRendererProps = NavigationSceneRendererProps & {
  scene: GiftedNavigationScene,
};
type GiftedNavigationScene = NavigationScene & {
  route: GiftedNavigationRoute,
};
type FakeNavigator = {
  pop: () => void;
};
type BattleNavigationRoute =
  // Choose which battle you are dealing with
    { key: 'BattleSelector', title: string }
  // Show the list of categories at the event
  | { key: 'BattleSignups', title: string, battleId: string }
  // Show the category and its contestants
  | { key: 'Category', title: string, battleId: string, categoryId: number }
  // Show the registration screen for the category
  | { key: 'Register', title: string, battleId: string, categoryId: number };

type GiftedNavigationRoute =
    NavigationRoute
  | BattleNavigationRoute
  | {
    renderScene: (navigator: FakeNavigator) => React.Element<*>,
  };

class _BattleSelector extends React.Component {
  props: {
    navigatable: Navigatable;    
  }

  onBattleSelected(battleId: string) {
    this.props.navigatable.onNavigate({ key: 'BattleSignups', title: `${battleId} Registration`, battleId });
  }

  onBattleHostSelected(battleId: string) {
    this.props.navigatable.onNavigate({ key: 'BattleHostView', title: `${battleId} MC Host View`, battleId });
  }

  render() {
    const battleId = 'justeDebout';
    return <HorizontalView style={{alignItems: 'center'}}>
      <Text>{battleId}</Text>
      <Button onPress={() => this.onBattleSelected(battleId)} caption="Dancer" />
      <Button onPress={() => this.onBattleHostSelected(battleId)} caption="Host" />
    </HorizontalView>;
  }
}
const BattleSelector = connect(
  state => ({
  }),
  (dispatch: Dispatch, props) => ({
    navigatePop: route => dispatch(navigatePop('EVENT_SIGNUPS_NAV')),
  }),
)(injectIntl(_BattleSelector));

class SelectedBattleBrackets extends React.Component {
  props: {
    battleEvent: BattleEvent;
    route: BattleNavigationRoute;
    navigatable: Navigatable;
  };

  constructor(props) {
    super(props);
    (this: any).onRegister = this.onRegister.bind(this);
    (this: any).onUnregister = this.onUnregister.bind(this);
  }

  onRegister(category) {
    const displayName = categoryDisplayName(category);
    this.props.navigatable.onNavigate({ key: 'Register', title: `${displayName} Registration`, battleId: this.props.battleEvent.id, categoryId: category.id });
  }

  async onUnregister(category, teamToDelete) {
    const [teamKey] = Object.entries(category.signups || {}).filter(([key, team]) => team === teamToDelete)[0];
    await eventUnregister(this.props.battleEvent.id, category.id, teamKey);
  }

  render() {
    if (!this.props.battleEvent) {
      return <Text>Loading Battle Info...</Text>;
    }
    const route = this.props.route;
    const battleEvent = this.props.battleEvent;

    let category = null;
    switch (route.key) {
      // Host Views
      case 'BattleHostView':
        return <BattleEventHostView
          battleEvent={battleEvent}
          onSelected={(selectedCategory) => {
          // trackWithEvent('View Event', event);
            const displayName = categoryDisplayName(selectedCategory);
            this.props.navigatable.onNavigate({ key: 'BattleHostCategory', title: displayName, battleId: this.props.battleEvent.id, categoryId: selectedCategory.id });
          }}
          />;
      case 'BattleHostCategory':
        category = this.props.battleEvent.categories[route.categoryId];
        return (<BattleHostCategoryView
          category={category}
        />);
      // Dancer Views
      case 'BattleSignups':
        return (<BattleEventView
          battleEvent={battleEvent}
          onSelected={(selectedCategory) => {
          // trackWithEvent('View Event', event);
            const displayName = categoryDisplayName(selectedCategory);
            this.props.navigatable.onNavigate({ key: 'Category', title: displayName, battleId: this.props.battleEvent.id, categoryId: selectedCategory.id });
          }}
          onRegister={this.onRegister}
          onUnregister={this.onUnregister}
        />);
      case 'Category':
        category = this.props.battleEvent.categories[route.categoryId];
        return (<CategoryView
          category={category}
          onRegister={this.onRegister}
          onUnregister={this.onUnregister}
        />);
      case 'Register':
        category = this.props.battleEvent.categories[route.categoryId];
        return (<CategorySignupScreen
          battle={this.props.battleEvent}
          category={category}
        />);
      default:
        return null;
    }
  }
}

class _BattleBrackets extends React.Component {
  props: {
    sceneProps: GiftedNavigationSceneRendererProps;
    navigatable: Navigatable;

    // Self-managed props
    navigatePop: () => void;
  }

  fakeNavigator() {
    return {
      pop: () => this.props.navigatePop(),
    };
  }

  render() {
    const { scene } = this.props.sceneProps;
    const { route } = scene;
    // Handle Gifted Form navigation
    if (route.renderScene) {
      return route.renderScene(this.fakeNavigator());
    }

    let category = null;

    switch (route.key) {
      case 'BattleSelector':
        return <BattleSelector navigatable={this.props.navigatable} />;
      default:
        return <TrackFirebase
          path={`events/${route.battleId}`}
          renderContents={(battleEvent) => (
            <SelectedBattleBrackets
              battleEvent={battleEvent}
              route={route}
              navigatable={this.props.navigatable}
            />)
          }
        />;
    }
  }
}
export const BattleBrackets = connect(
  state => ({
  }),
  (dispatch: Dispatch, props) => ({
    navigatePop: route => dispatch(navigatePop('EVENT_SIGNUPS_NAV')),
  }),
)(injectIntl(_BattleBrackets));

const checkSize = 20;
const checkMargin = 10;
let styles = StyleSheet.create({
  container: {
  },
  miniThumbnail: {
    height: 50,
    flex: 1,
  },
  registrationLine: {
    alignItems: 'center',
  },
  registrationLineOuter: {
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  registrationStatusIcon: {
    width: checkSize,
    height: checkSize,
    marginRight: checkMargin,
  },
  registrationIndent: {
    marginLeft: checkSize + checkMargin,
  },
  registrationStatusText: {
    fontSize: semiNormalize(20),
    lineHeight: semiNormalize(24),
  },
});
