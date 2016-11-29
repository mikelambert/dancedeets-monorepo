/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

export type State = {
  selectedTab: string;
};

const initialState = {
  selectedTab: 'events',
};

export function mainTabs(state: State = initialState, action: Action): State {
  if (action.type === 'TAB_SELECT') {
    return {...state, selectedTab: action.tab};
  }
  return state;
}
