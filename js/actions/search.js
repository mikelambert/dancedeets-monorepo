/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { Action } from './types';
import type { SearchQuery, SearchResults } from '../events/search';
import type { Dispatch } from '../actions/types';

import { search } from '../api';

export function performSearch(searchQuery: SearchQuery) {
  return async function(dispatch: Dispatch) {
    try {
      const responseData = await search(searchQuery.location, searchQuery.keywords, searchQuery.timePeriod);
      dispatch(searchComplete(responseData));
    } catch (e) {
      // TODO: error fetching events.
      console.log('error fetching events', e);
      dispatch(searchFailed());
    }
  };
}
export function updateLocation(location: string): Action {
  return {
    type: 'UPDATE_LOCATION',
    location,
  };
}

export function updateKeywords(keywords: string): Action {
  return {
    type: 'UPDATE_KEYWORDS',
    keywords,
  };
}

function searchComplete(results: SearchResults): Action {
  return {
    type: 'SEARCH_COMPLETE',
    results,
  };
}

function searchFailed(): Action {
  return {
    type: 'SEARCH_FAILED',
  };
}
