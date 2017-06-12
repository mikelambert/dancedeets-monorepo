/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Image, StyleSheet } from 'react-native';
import { addNavigationHelpers, TabNavigator } from 'react-navigation';
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
import TabBar from './TabBar';

class TabBarView extends React.Component {
  props: {
    dispatch: Dispatch,
    screens: any,
  };
  render() {
    const { dispatch, screens, ...props } = this.props;
    return (
      <TabBar
        navigation={addNavigationHelpers({
          dispatch,
          state: screens.overall,
        })}
        {...props}
      />
    );
  }
}
export default connect(store => ({
  screens: store.screens,
}))(TabBarView);
