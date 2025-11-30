/**
 * Copyright 2016 DanceDeets.
 *
 * Note: Navigation state is no longer stored in Redux.
 * React Navigation v6 manages its own state internally.
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

export default combineReducers({
  addEvents,
  firebase,
  loadedEvents,
  search,
  searchHeader,
  searchQuery,
  translate,
  tutorials,
  user,
});
