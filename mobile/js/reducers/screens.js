/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { combineReducers } from 'redux';
import {
  EventScreensNavigator,
  LearnScreensNavigator,
  AboutScreensNavigator,
  BattleScreensNavigator,
} from '../containers/screens';
import TabNavigator from '../containers/TabNavigator';

export default combineReducers({
  overall: (state, action) =>
    TabNavigator.router.getStateForAction(action, state),

  events: (state, action) =>
    EventScreensNavigator.router.getStateForAction(action, state),
  learn: (state, action) =>
    LearnScreensNavigator.router.getStateForAction(action, state),
  about: (state, action) =>
    AboutScreensNavigator.router.getStateForAction(action, state),
  battle: (state, action) =>
    BattleScreensNavigator.router.getStateForAction(action, state),
});
