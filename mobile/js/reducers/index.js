/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { combineReducers } from 'redux';
import { addEvents } from './addEvents';
import { firebase } from './firebase';
import { mainTabs } from './mainTabs';
import { search } from './search';
import { translate } from './translate';
import { tutorials } from './tutorials';
import { user } from './user';
import screens from './screens';
import searchHeader from '../ducks/searchHeader';

export default combineReducers({
  addEvents,
  firebase,
  mainTabs,
  screens,
  search,
  searchHeader,
  translate,
  tutorials,
  user,
});
