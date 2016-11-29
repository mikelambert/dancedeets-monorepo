/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {combineReducers} from 'redux';
import {addEvents} from './addEvents';
import {firebase} from './firebase';
import {mainTabs} from './mainTabs';
import {navigationState} from './navigation';
import {search} from './search';
import {translate} from './translate';
import {tutorials} from './tutorials';
import {user} from './user';

export default combineReducers({
  addEvents,
  firebase,
  mainTabs,
  navigationState,
  search,
  translate,
  tutorials,
  user,
});
