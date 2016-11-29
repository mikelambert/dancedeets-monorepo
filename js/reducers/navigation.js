/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as NavigationStateUtils from 'NavigationStateUtils';

import { NAV_PUSH, NAV_POP, NAV_JUMP_TO_KEY, NAV_JUMP_TO_INDEX, NAV_RESET, NAV_SWAP } from '../actions';

import type { Action } from '../actions/types';
import type { NavigationState, NavigationRoute } from 'NavigationTypeDefinition';

// This is used to track the 'default' route for each possible navigator,
// that can be configured from outside of this module
const defaultNavigatorRoutes: {[navigator: string]: NavigationRoute} = {};

type AllNavigationStates = { [key: string]: NavigationState };

const initialNavStates: AllNavigationStates = {};

export function setDefaultState(navigator: string, route: NavigationRoute) {
	defaultNavigatorRoutes[navigator] = route;
}

export function getNamedState(allStates: AllNavigationStates, navigator: string): NavigationState {
	return allStates[navigator] || {
		index: 0,
		routes: [defaultNavigatorRoutes[navigator]],
	};
}

export function navigationState(allStates: AllNavigationStates = initialNavStates, action: Action): AllNavigationStates {
	if (action.type === 'LOGIN_LOGGED_OUT') {
		return {};
	}
	let state = null;
	switch (action.type) {
	case NAV_PUSH:
		state = getNamedState(allStates, action.navigator);
		if (state.routes[state.index].key === (action.state && action.state.key)) {
			return {
				...allStates,
				[action.navigator]: state,
			};
		}
		return {
			...allStates,
			[action.navigator]: NavigationStateUtils.push(state, action.state),
		};

	case NAV_POP:
		state = getNamedState(allStates, action.navigator);
		if (state.index === 0 || state.routes.length === 1) {
			return {
				...allStates,
				[action.navigator]: state,
			};
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
			[action.navigator]: NavigationStateUtils.replaceAt(state, action.key, action.newRoute),
		};

	case NAV_RESET:
		state = getNamedState(allStates, action.navigator);
		return {
			...allStates,
			[action.navigator]: {
				...state,
				index: action.index,
				routes: action.routes,
			}
		};

	default:
		return allStates;
	}
}
