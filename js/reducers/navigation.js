/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as NavigationStateUtils from 'NavigationStateUtils';

import { NAV_PUSH, NAV_POP, NAV_JUMP_TO_KEY, NAV_JUMP_TO_INDEX, NAV_RESET, NAV_SWAP } from '../actions';

import type { Action } from '../actions/types';
import type { NavigationState } from 'NavigationTypeDefinition';

const initialNavState: NavigationState = {
	key: 'MainNavigation',
	index: 0,
	routes: [
		{ key: 'EventList', title: 'DanceDeets' }
	]
};

export function navigationState(state: NavigationState = initialNavState, action: Action) {
  if (action.type === 'LOGIN_LOGGED_OUT') {
    return initialNavState;
  }
	switch (action.type) {
	case NAV_PUSH:
		if (state.routes[state.index].key === (action.state && action.state.key)) {
			return state;
		}
		return NavigationStateUtils.push(state, action.state);

	case NAV_POP:
		if (state.index === 0 || state.routes.length === 1) {
			return state;
		}
		return NavigationStateUtils.pop(state);

	case NAV_JUMP_TO_KEY:
		return NavigationStateUtils.jumpTo(state, action.key);

	case NAV_JUMP_TO_INDEX:
		return NavigationStateUtils.jumpToIndex(state, action.index);

	case NAV_SWAP:
		return NavigationStateUtils.replaceAt(state, action.key, action.newState);

	case NAV_RESET:
		return {
			...state,
			index: action.index,
			routes: action.routes,
		};

	default:
		return state;
	}
}
