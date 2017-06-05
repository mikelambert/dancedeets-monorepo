/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { NavigationActions, StackNavigator } from 'react-navigation';
import type {
  NavigationRouteConfigMap,
} from 'react-navigation/src/TypeDefinition';
import type {
  StackNavigatorConfig,
} from 'react-navigation/src/navigators/StackNavigator';
import { gradientTop, purpleColors } from '../../Colors';

export default (
  routeConfigMap: NavigationRouteConfigMap,
  stackConfig: StackNavigatorConfig = {}
) =>
  StackNavigator(routeConfigMap, {
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
