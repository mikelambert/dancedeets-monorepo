/**
 * Copyright 2016 DanceDeets.
 */

import { NavigationActions, StackNavigator } from 'react-navigation';
import type {
  NavigationAction,
  NavigationRouteConfigMap,
  NavigationState,
  StackNavigatorConfig,
} from 'react-navigation/src/TypeDefinition';
import { hardwareBackPress } from 'react-native-back-android';
import { gradientTop } from '../../Colors';

const navigateOnce = (
  getStateForAction: (
    action: NavigationAction,
    lastState: NavigationState | null
  ) => NavigationState | null
) => (action: NavigationAction, state: NavigationState) => {
  const { type } = action;
  if (state && type === NavigationActions.NAVIGATE) {
    const { routeName } = action as any;
    if (routeName === state.routes[state.routes.length - 1].routeName) {
      return state;
    }
  }
  return getStateForAction(action, state);
};

export default (
  stateName: string,
  routeConfigMap: NavigationRouteConfigMap,
  stackConfig: StackNavigatorConfig = {}
) => {
  const newRouteConfigMap = { ...routeConfigMap };
  Object.keys(newRouteConfigMap).forEach(key => {
    const newScreen = hardwareBackPress((routeConfigMap as any)[key].screen, (props: any) =>
      props.navigation.goBack()
    );
    // TODO: This is necessary until https://github.com/awesomejerry/react-native-back-android/issues/11 is fixed/deployed:
    (newScreen as any).navigationOptions = (routeConfigMap as any)[key].screen.navigationOptions;
    (newRouteConfigMap as any)[key] = {
      ...(routeConfigMap as any)[key],
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
