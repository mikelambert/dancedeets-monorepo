/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import type { Action } from './types';
import type { NavigationState } from 'NavigationTypeDefinition';

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
export function navigatePush(state: string | NavigationState): Action {
	state = typeof state === 'string' ? { key: state } : state;
	return {
		type: NAV_PUSH,
		state
	};
}

export function navigatePop(): Action {
	return {
		type: NAV_POP
	};
}

export function navigateJumpToKey(key: string): Action {
	return {
		type: NAV_JUMP_TO_KEY,
		key
	};
}

export function navigateJumpToIndex(index: number): Action {
	return {
		type: NAV_JUMP_TO_INDEX,
		index
	};
}

export function navigateSwap(key: string, newState: NavigationState): Action {
	return {
		type: NAV_SWAP,
		key,
		newState,
	};
}

export function navigateReset(children: Array<NavigationState>, index: number): Action {
	return {
		type: NAV_RESET,
		index,
		children
	};
}
