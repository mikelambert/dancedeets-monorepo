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
		//TODO: Abstract out this hardcoded initial state value!
		{ key: 'EventList', title: 'DanceDeets' }
	]
};

type AllNavigationStates = {
	states: { [key: string]: NavigationState };
};

const initialNavStates: AllNavigationStates = {
	states: {},
};

export function getNamedState(allStates: AllNavigationStates, navigator: string) {
	return allStates[navigator] || initialNavState;
}

export function navigationState(allStates: AllNavigationStates = initialNavStates, action: Action) {
	if (action.type === 'LOGIN_LOGGED_OUT') {
		return {};
	}
	let state = null;
	switch (action.type) {
	case NAV_PUSH:
		state = getNamedState(allStates, action.navigator);
		if (state.routes[state.index].key === (action.state && action.state.key)) {
			return state;
		}
		return {
			...allStates,
			[action.navigator]: NavigationStateUtils.push(state, action.state),
		};

	case NAV_POP:
		state = getNamedState(allStates, action.navigator);
		if (state.index === 0 || state.routes.length === 1) {
			return state;
		}
		return {
			...allStates,
			[action.navigator]: NavigationStateUtils.pop(state),
		};

	case NAV_JUMP_TO_KEY:
		state = getNamedState(allStates, action.navigator);
		return {
			...allStates,
			[action.navigator]: NavigationStateUtils.jumpTo(state, action.key),
		};

	case NAV_JUMP_TO_INDEX:
		state = getNamedState(allStates, action.navigator);
		return {
			...allStates,
			[action.navigator]: NavigationStateUtils.jumpToIndex(state, action.index),
		};

	case NAV_SWAP:
		state = getNamedState(allStates, action.navigator);
		return {
			...allStates,
			[action.navigator]: NavigationStateUtils.replaceAt(state, action.key, action.newState),
		};

	case NAV_RESET:
		state = getNamedState(allStates, action.navigator);
		return {
			...allStates,
			[action.navigator]: {
				...state,
				index: action.index,
				routes: action.children,
			}
		};

	default:
		return allStates;
	}
}
