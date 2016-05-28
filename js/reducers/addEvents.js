/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

import type { AddEventList } from '../addEventsModels';

export type SortOrder = 'ByDate' | 'ByName';

export type DisplayOptions = {
  onlyUnadded: boolean;
  sortOrder: SortOrder;
};

export type State = {
  displayOptions: DisplayOptions;
  loading: boolean;
  results: ?AddEventList;
};

const initialState = {
  displayOptions: {
    onlyUnadded: false,
    sortOrder: 'ByDate',
  },
  loading: false,
  results: null,
};

export function addEvents(state: State = initialState, action: Action): State {
  if (action.type === 'ADD_EVENTS_RELOAD') {
    return {
      ...state,
      results: null,
      loading: true,
    };
  }
  if (action.type === 'ADD_EVENTS_RELOAD_COMPLETE') {
    return {
      ...state,
      results: action.results,
      loading: false,
    };
  }
  if (action.type === 'ADD_EVENTS_TOGGLE_ONLY_UNADDED') {
    return {
      ...state,
      displayOptions: {
        ...state.displayOptions,
        onlyUnadded: !state.displayOptions.onlyUnadded,
      },
    };
  }
  if (action.type === 'ADD_EVENTS_TOGGLE_SORT_ORDER') {
    return {
      ...state,
      displayOptions: {
        ...state.displayOptions,
        sortOrder: (state.displayOptions.sortOrder === 'ByDate' ? 'ByName' : 'ByDate'),
      },
    };
  }
  return state;
}
