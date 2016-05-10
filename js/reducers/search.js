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
  results: null,
};

export function search(state: State = initialState, action: Action): State {
  if (action.type === 'UPDATE_LOCATION') {
    var searchQuery = {
      ...state.searchQuery,
      location: action.location,
    };
    return {
      ...state,
      searchQuery,
      results: null,
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
      results: null,
    };
  }
  if (action.type === 'SEARCH_COMPLETE') {
    return {
      ...state,
      results: action.results,
    };
  }
  if (action.type === 'SEARCH_FAILED') {
    return {
      ...state,
      results: null,
    };
  }
  return state;
}
