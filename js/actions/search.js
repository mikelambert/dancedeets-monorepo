/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { Action, ThunkAction, Dispatch } from './types';
import type { SearchQuery, SearchResults } from '../events/search';

import { search } from '../api/dancedeets';

export function performSearch(): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const searchQuery = getState().search.searchQuery;
    await dispatch(searchStart(searchQuery));
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

export function toggleLayout(): Action {
  return {
    type: 'TOGGLE_LAYOUT',
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

function searchStart(searchQuery: SearchQuery): Action {
  return {
    type: 'START_SEARCH',
    searchQuery,
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
