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
  // Add this ourselves, since it's useful for us for others to be able to find the 'zeroth index route name'
  Navigator.routeConfig = routeConfigMap;
  return Navigator;
};
