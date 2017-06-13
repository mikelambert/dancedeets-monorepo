/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { combineReducers } from 'redux';
import { addEvents } from './addEvents';
import { firebase } from './firebase';
import { search } from './search';
import { translate } from './translate';
import { tutorials } from './tutorials';
import { user } from './user';
import searchHeader from '../ducks/searchHeader';
import TabNavigator from '../containers/TabNavigator';

function screens(state, action) {
  // Reverse ordering: (state, action) => (action, state)
  return TabNavigator.router.getStateForAction(action, state);
}

export default combineReducers({
  addEvents,
  firebase,
  screens,
  search,
  searchHeader,
  translate,
  tutorials,
  user,
});
