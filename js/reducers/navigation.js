/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as NavigationStateUtils from 'NavigationStateUtils';

import { NAV_PUSH, NAV_POP, NAV_JUMP_TO_KEY, NAV_JUMP_TO_INDEX, NAV_RESET } from '../actions';

import type { Action } from '../actions/types';
import type { NavigationParentState } from 'NavigationTypeDefinition';

const initialNavState: NavigationParentState = {
	key: 'MainNavigation',
	index: 0,
	children: [
		{ key: 'EventList', title: 'DanceDeets' }
	]
};

export function navigationState(state: NavigationParentState = initialNavState, action: Action) {
  if (action.type === 'LOGIN_LOGGED_OUT') {
    return initialNavState;
  }
	switch (action.type) {
	case NAV_PUSH:
		if (state.children[state.index].key === (action.state && action.state.key)) {
			return state;
		}
		return NavigationStateUtils.push(state, action.state);

	case NAV_POP:
		if (state.index === 0 || state.children.length === 1) {
			return state;
		}
		return NavigationStateUtils.pop(state);

	case NAV_JUMP_TO_KEY:
		return NavigationStateUtils.jumpTo(state, action.key);

	case NAV_JUMP_TO_INDEX:
		return NavigationStateUtils.jumpToIndex(state, action.index);

	case NAV_RESET:
		return {
			...state,
			index: action.index,
			children: action.children
		};

	default:
		return state;
	}
}
