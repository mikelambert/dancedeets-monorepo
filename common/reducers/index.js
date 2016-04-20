/**
 * Copyright DanceDeets.
 * @flow
 */

'use strict';

import {combineReducers} from 'redux';
import {user} from './user';
import {navigationState} from './navigation';
import {onboarding} from './onboarding';

export default combineReducers({
	navigationState,
	user,
    onboarding,
});
