/**
 * Copyright 2016 DanceDeets.
 *
 * React Navigation v6 root navigation container
 */

import * as React from 'react';
import { NavigationContainer, NavigationContainerRef } from '@react-navigation/native';
import TabNavigator from './TabNavigator';
import { track } from '../store/track';

// Navigation ref for programmatic navigation from outside components
export const navigationRef = React.createRef<NavigationContainerRef<any>>();

// Helper function to navigate from outside components
export function navigate(name: string, params?: object): void {
  navigationRef.current?.navigate(name, params);
}

function TabApp(): React.ReactElement {
  return (
    <NavigationContainer
      ref={navigationRef}
      onStateChange={(state) => {
        // Track tab changes
        if (state) {
          const currentRoute = state.routes[state.index];
          track('Tab Selected', { Tab: currentRoute.name });
        }
      }}
    >
      <TabNavigator />
    </NavigationContainer>
  );
}

export default TabApp;
