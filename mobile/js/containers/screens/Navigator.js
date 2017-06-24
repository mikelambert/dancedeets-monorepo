/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  addNavigationHelpers,
  NavigationActions,
  StackNavigator,
} from 'react-navigation';
import { connect } from 'react-redux';
import type { NavigationRouteConfigMap } from 'react-navigation/src/TypeDefinition';
import type { StackNavigatorConfig } from 'react-navigation/src/navigators/StackNavigator';
import { gradientTop, purpleColors } from '../../Colors';
import type { Dispatch } from '../../actions/types';

const navigateOnce = getStateForAction => (action, state) => {
  const { type, routeName } = action;
  return state &&
    type === NavigationActions.NAVIGATE &&
    routeName === state.routes[state.routes.length - 1].routeName
    ? state
    : getStateForAction(action, state);
};

export default (
  stateName: string,
  routeConfigMap: NavigationRouteConfigMap,
  stackConfig: StackNavigatorConfig = {}
) => {
  const Navigator = StackNavigator(routeConfigMap, {
    navigationOptions: {
      headerTintColor: 'white',
      headerStyle: {
        backgroundColor: gradientTop,
      },
    },
    cardStyle: {
      backgroundColor: purpleColors[4],
    },
    ...stackConfig,
  });

  Navigator.router.getStateForAction = navigateOnce(
    Navigator.router.getStateForAction
  );
  return Navigator;
};
