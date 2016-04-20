/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {combineReducers} from 'redux';
import {user} from './user';
import {navigationState} from './navigation';

export default combineReducers({
	navigationState,
	user,
});
