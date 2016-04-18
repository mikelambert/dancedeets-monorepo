// *** Action Types ***
export const NAVIGATE = 'NAVIGATE'
export const NAV_PUSH = 'NAV_PUSH'
export const NAV_POP = 'NAV_POP'
export const NAV_JUMP_TO_KEY = 'NAV_JUMP_TO_KEY'
export const NAV_JUMP_TO_INDEX = 'NAV_JUMP_TO_INDEX'
export const NAV_RESET = 'NAV_RESET'


// *** Action Creators ***
// The following action creators were derived from NavigationStackReducer
export function navigatePush(state) {
	state = typeof state === 'string' ? { key: state } : state
	return {
		type: NAV_PUSH,
		state
	}
}

export function navigatePop() {
	return {
		type: NAV_POP
	}
}

export function navigateJumpToKey(key) {
	return {
		type: NAV_JUMP_TO_KEY,
		key
	}
}

export function navigateJumpToIndex(index) {
	return {
		type: NAV_JUMP_TO_INDEX,
		index
	}
}

export function navigateReset(children, index) {
	return {
		type: NAV_RESET,
		index,
		children
	}
}