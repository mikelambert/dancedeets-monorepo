/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type {Action} from '../actions/types';
import type { SearchQuery, SearchResults } from '../events/search';

export type State = {
  searchQuery: SearchQuery;
  results: ?SearchResults;
};

const initialState = {
  searchQuery: {
    location: '',
    keywords: '',
    timePeriod: 'UPCOMING',
  },
  loading: false,
  results: null,
};

export function search(state: State = initialState, action: Action): State {
  if (action.type === 'UPDATE_LOCATION' ||
      // Only set location from GPS if user hasn't entered any location
      (action.type === 'DETECTED_LOCATION' && state.searchQuery.location == "")) {
    var searchQuery = {
      ...state.searchQuery,
      location: action.location,
    };
    return {
      ...state,
      searchQuery,
    };
  }
  if (action.type === 'UPDATE_KEYWORDS') {
    var searchQuery = {
      ...state.searchQuery,
      keywords: action.keywords,
    };
    return {
      ...state,
      searchQuery,
    };
  }
  if (action.type === 'START_SEARCH') {
    return {
      ...state,
      loading: true,
      results: null,
    };
  }
  if (action.type === 'SEARCH_COMPLETE') {
    return {
      ...state,
      loading: false,
      results: action.results,
    };
  }
  if (action.type === 'SEARCH_FAILED') {
    return {
      ...state,
      loading: false,
      results: null,
    };
  }
  return state;
}
