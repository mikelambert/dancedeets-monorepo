/**
 * Copyright 2016 DanceDeets.
 *
 * React Navigation v6 stack navigator factory
 */

import * as React from 'react';
import { createStackNavigator, StackNavigationOptions } from '@react-navigation/stack';
import { gradientTop } from '../../Colors';

const Stack = createStackNavigator();

export interface ScreenConfig {
  screen: React.ComponentType<any>;
  options?: StackNavigationOptions | ((props: any) => StackNavigationOptions);
}

export type RouteConfigMap = Record<string, ScreenConfig>;

const defaultScreenOptions: StackNavigationOptions = {
  headerTintColor: 'white',
  headerStyle: {
    backgroundColor: gradientTop,
  },
};

export default function createMyStackNavigator(
  stateName: string,
  routeConfigMap: RouteConfigMap,
  stackConfig: StackNavigationOptions = {}
): React.ComponentType<any> {
  const screenNames = Object.keys(routeConfigMap);
  const initialRouteName = screenNames[0];

  function StackNavigatorComponent() {
    return (
      <Stack.Navigator
        initialRouteName={initialRouteName}
        screenOptions={{
          ...defaultScreenOptions,
          cardStyle: {
            backgroundColor: 'black',
          },
          ...stackConfig,
        }}
      >
        {screenNames.map(name => {
          const config = routeConfigMap[name];
          return (
            <Stack.Screen
              key={name}
              name={name}
              component={config.screen}
              options={config.options}
            />
          );
        })}
      </Stack.Navigator>
    );
  }

  return StackNavigatorComponent;
}
