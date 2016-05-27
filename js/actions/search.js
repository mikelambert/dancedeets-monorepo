/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { Action, ThunkAction } from './types';
import type { SearchQuery, SearchResults } from '../events/search';
import type { Dispatch } from '../actions/types';

import { search } from '../api/dancedeets';

export function performSearch(searchQuery: SearchQuery) {
  return async function(dispatch: Dispatch) {
    await dispatch(searchStart());
    try {
      const responseData = await search(searchQuery.location, searchQuery.keywords, searchQuery.timePeriod);
      await dispatch(searchComplete(responseData));
    } catch (e) {
      // TODO: error fetching events.
      console.log('error fetching events', e, e.stack);
      await dispatch(searchFailed());
    }
  };
}

export function detectedLocation(location: string): ThunkAction {
  return async function(dispatch: Dispatch) {
    await dispatch({
      type: 'DETECTED_LOCATION',
      location,
    });
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

function searchStart(): Action {
  return {
    type: 'START_SEARCH',
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
