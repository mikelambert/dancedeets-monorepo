/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { addNavigationHelpers } from 'react-navigation';
import type {
  NavigationNavigateAction,
  NavigationParams,
} from 'react-navigation/src/TypeDefinition';
import { connect } from 'react-redux';
import { injectIntl, intlShape } from 'react-intl';
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
              action?: NavigationNavigateAction
            ) => {
              // Override our navigation.navigate(), so we can track tab switchings
              track('Tab Selected', { Tab: routeName });
              navigation.navigate(routeName, params, action);
              return true;
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
