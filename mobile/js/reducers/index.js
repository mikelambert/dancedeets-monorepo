/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { combineReducers } from 'redux';
import { addEvents } from './addEvents';
import { firebase } from './firebase';
import { loadedEvents } from './loadedEvents';
import { search } from './search';
import { translate } from './translate';
import { tutorials } from './tutorials';
import { user } from './user';
import searchHeader from '../ducks/searchHeader';
import searchQuery from '../ducks/searchQuery';
import TabNavigator from '../containers/TabNavigator';

function screens(state, action) {
  // Reverse ordering: (state, action) => (action, state)
  const nextState = TabNavigator.router.getStateForAction(action, state);

  // If nextState is null, it means no-action. So let's return the existing state.
  // https://github.com/react-community/react-navigation/issues/271#issuecomment-309482910
  // https://reactnavigation.org/docs/guides/redux#Redux-Integration
  return nextState || state;
}

export default combineReducers({
  addEvents,
  firebase,
  loadedEvents,
  screens,
  search,
  searchHeader,
  searchQuery,
  translate,
  tutorials,
  user,
});
