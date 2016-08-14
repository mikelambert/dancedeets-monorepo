/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import type { Action } from './types';
import type { NavigationRoute } from 'NavigationTypeDefinition';

// *** Action Types ***
export const NAVIGATE = 'NAVIGATE';
export const NAV_PUSH = 'NAV_PUSH';
export const NAV_POP = 'NAV_POP';
export const NAV_JUMP_TO_KEY = 'NAV_JUMP_TO_KEY';
export const NAV_JUMP_TO_INDEX = 'NAV_JUMP_TO_INDEX';
export const NAV_RESET = 'NAV_RESET';
export const NAV_SWAP = 'NAV_SWAP';

// *** Action Creators ***
// The following action creators were derived from NavigationStackReducer
export function navigatePush(navigator: string, state: string | NavigationRoute): Action {
	state = typeof state === 'string' ? { key: state } : state;
	return {
		type: NAV_PUSH,
		navigator,
		state,
	};
}

export function navigatePop(navigator: string): Action {
	return {
		type: NAV_POP,
		navigator,
	};
}

export function navigateJumpToKey(navigator: string, key: string): Action {
	return {
		type: NAV_JUMP_TO_KEY,
		navigator,
		key,
	};
}

export function navigateJumpToIndex(navigator: string, index: number): Action {
	return {
		type: NAV_JUMP_TO_INDEX,
		navigator,
		index,
	};
}

export function navigateSwap(navigator: string, key: string, newState: NavigationRoute): Action {
	return {
		type: NAV_SWAP,
		navigator,
		key,
		newState,
	};
}

export function navigateReset(navigator: string, routes: Array<NavigationRoute>, index: number): Action {
	return {
		type: NAV_RESET,
		navigator,
		index,
		routes,
	};
}
