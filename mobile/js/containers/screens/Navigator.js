/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { NavigationActions, StackNavigator } from 'react-navigation';
import type {
  NavigationRouteConfigMap,
  StackNavigatorConfig,
} from 'react-navigation/src/TypeDefinition';
import { hardwareBackPress } from 'react-native-back-android';
import { gradientTop } from '../../Colors';

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
  const newRouteConfigMap = { ...routeConfigMap };
  Object.keys(newRouteConfigMap).forEach(key => {
    const newScreen = hardwareBackPress(routeConfigMap[key].screen, props =>
      props.navigation.goBack()
    );
    // TODO: This is necessary until https://github.com/awesomejerry/react-native-back-android/issues/11 is fixed/deployed:
    newScreen.navigationOptions = routeConfigMap[key].screen.navigationOptions;
    newRouteConfigMap[key] = {
      ...routeConfigMap[key],
      screen: newScreen,
    };
  });

  const Navigator = StackNavigator(newRouteConfigMap, {
    navigationOptions: {
      headerTintColor: 'white',
      headerStyle: {
        backgroundColor: gradientTop,
      },
    },
    cardStyle: {
      backgroundColor: 'black',
    },
    ...stackConfig,
  });

  Navigator.router.getStateForAction = navigateOnce(
    Navigator.router.getStateForAction
  );
  return Navigator;
};
