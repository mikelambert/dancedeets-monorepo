/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {combineReducers} from 'redux';
import {user} from './user';
import {navigationState} from './navigation';
import {search} from './search';

export default combineReducers({
  navigationState,
  user,
  search,
});
