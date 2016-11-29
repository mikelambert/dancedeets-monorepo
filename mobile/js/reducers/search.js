/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { Dimensions } from 'react-native';

import type {Action} from '../actions/types';
import type { SearchQuery, SearchResults } from '../events/search';

export type State = {
  listLayout: boolean; // should show list view or expanded view
  loading: boolean; // loading indicator
  searchQuery: SearchQuery; // our current search query
  results: ?SearchResults; // our last-searched results
  error: boolean; // whether there was an error fetching the current results
};

// Use the smaller thumbnails by default on a larger screen
const widescreen = Dimensions.get('window').width >= 768;
const initialState = {
  listLayout: widescreen,
  loading: false,
  searchQuery: {
    location: '',
    keywords: '',
    timePeriod: 'UPCOMING',
  },
  results: null,
  error: false,
};

export function search(state: State = initialState, action: Action): State {
  if (action.type === 'LOGIN_LOGGED_OUT') {
    return initialState;
  }
  if (action.type === 'UPDATE_LOCATION' ||
      // Only set location from GPS if user hasn't entered any location
      (action.type === 'DETECTED_LOCATION' && state.searchQuery.location === '')) {
    var searchQuery = {
      ...state.searchQuery,
      location: action.location,
    };
    return {
      ...state,
      searchQuery,
    };
  }
  if (action.type === 'TOGGLE_LAYOUT') {
    return {
      ...state,
      listLayout: !state.listLayout,
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
      error: false,
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
      error: true,
    };
  }
  return state;
}
