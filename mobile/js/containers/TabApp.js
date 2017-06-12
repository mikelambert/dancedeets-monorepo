/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Image, StyleSheet } from 'react-native';
import { addNavigationHelpers } from 'react-navigation';
import type {
  NavigationAction,
  NavigationParams,
} from 'react-navigation/src/TypeDefinition';
import { connect } from 'react-redux';
import WKWebView from 'react-native-wkwebview-reborn';
import {
  EventScreensView,
  LearnScreensView,
  AboutScreensView,
  BattleScreensView,
} from './screens';
import { semiNormalize } from '../ui';
import type { Dispatch } from '../actions/types';
import TabNavigator from './TabNavigator';
import { TimeTracker } from '../util/timeTracker';
import { track } from '../store/track';

class TabApp extends React.Component {
  props: {
    dispatch: Dispatch,
    screensOverall: any,
  };
  render() {
    const { dispatch, screensOverall, ...props } = this.props;
    const navigation = addNavigationHelpers({
      dispatch,
      state: screensOverall,
    });

    const routeKey = this.props.screensOverall.routes[
      this.props.screensOverall.index
    ].key;
    return (
      <TimeTracker eventName="Tab Time" eventValue={routeKey}>
        <TabNavigator
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
  screensOverall: store.screens.overall,
}))(TabApp);
