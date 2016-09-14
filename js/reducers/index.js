/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {combineReducers} from 'redux';
import {addEvents} from './addEvents';
import {user} from './user';
import {mainTabs} from './mainTabs';
import {navigationState} from './navigation';
import {search} from './search';
import {translate} from './translate';

export default combineReducers({
  addEvents,
  mainTabs,
  navigationState,
  user,
  search,
  translate,
});
