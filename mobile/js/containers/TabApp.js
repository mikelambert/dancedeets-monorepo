/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { Image, StyleSheet } from 'react-native';
import { addNavigationHelpers } from 'react-navigation';
import type {
  NavigationAction,
  NavigationParams,
} from 'react-navigation/src/TypeDefinition';
import { connect } from 'react-redux';
import { injectIntl, intlShape } from 'react-intl';
import { semiNormalize } from '../ui';
import type { Dispatch } from '../actions/types';
import TabNavigator from './TabNavigator';
import { TimeTracker } from '../util/timeTracker';
import { track } from '../store/track';

class TabApp extends React.Component<{
  // Self-managed props
  dispatch: Dispatch,
  screens: any,
  intl: intlShape,
}> {
  render() {
    const { dispatch, screens, intl, ...props } = this.props;
    const navigation = addNavigationHelpers({
      dispatch,
      state: screens,
    });

    const routeKey = screens.routes[screens.index].key;
    return (
      <TimeTracker eventName="Tab Time" eventValue={routeKey}>
        <TabNavigator
          screenProps={{
            intl,
          }}
          navigation={{
            ...navigation,
            navigate: (
              routeName: string,
              params?: NavigationParams,
              action?: NavigationAction
            ) => {
              // Override our navigation.navigate(), so we can track tab switchings
              track('Tab Selected', { Tab: routeName });
              navigation.navigate(routeName, params, action);
            },
          }}
          {...props}
        />
      </TimeTracker>
    );
  }
}
export default connect(store => ({
  screens: store.screens,
}))(injectIntl(TabApp));
