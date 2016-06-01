/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';

import type { AddEventData, AddEventList, SortOrder } from '../addEventsModels';

export type RsvpFilter = 'attending' | 'maybe' | 'declined' | 'unsure' | null;

export type DisplayOptions = {
  onlyUnadded: boolean;
  sortOrder: SortOrder;
  //rsvpFilter: RsvpFilter;
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
    //rsvpFilter: null,
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
  if (action.type === 'ADD_EVENTS_SET_ONLY_UNADDED') {
    return {
      ...state,
      displayOptions: {
        ...state.displayOptions,
        onlyUnadded: action.value,
      },
    };
  }
  if (action.type === 'ADD_EVENTS_SET_SORT_ORDER') {
    return {
      ...state,
      displayOptions: {
        ...state.displayOptions,
        sortOrder: action.value,
      },
    };
  }
  if (action.type === 'ADD_EVENTS_UPDATE_LOADED') {
    if (!state.results) {
      // Ignore any callbacks that don't correspond to a valid search results
      return state;
    }
    const constAction = action; // Because flow doesn't trust this to stay inside the map()
    const newResults = state.results.map((x: AddEventData) => {
      if (x.id === constAction.eventId) {
        if (constAction.status === 'UNLOADED') {
          return {
            ...x,
            loaded: false,
            clickedConfirming: false,
            pending: false,
          };
        } else if (constAction.status === 'CLICKED') {
          console.log('hey, clicked', x);
          return {
            ...x,
            loaded: false,
            clickedConfirming: !x.clickedConfirming,
            pending: false,
          };
        } else if (constAction.status === 'PENDING') {
          return {
            ...x,
            loaded: false,
            clickedConfirming: false,
            pending: true,
          };
        } else if (constAction.status === 'LOADED') {
          return {
            ...x,
            loaded: true,
            clickedConfirming: false,
            pending: false,
          };
        }
      }
      return x;
    });
    return {
      ...state,
      results: newResults,
    };
  }
  return state;
}
