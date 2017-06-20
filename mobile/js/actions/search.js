/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import type { SearchResponse } from 'dancedeets-common/js/events/search';
import type { Action, ThunkAction, Dispatch } from './types';

import { search } from '../api/dancedeets';
import { track } from '../store/track';
import { storeSavedAddress } from '../events/savedAddress';
import { hideSearchForm } from '../ducks/searchHeader';

export function performSearch(): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const searchQuery = getState().searchQuery;
    track('Search Events', {
      Location: searchQuery.location,
      Keywords: searchQuery.keywords,
    });
    await storeSavedAddress(searchQuery.location);
    await dispatch(searchStart());
    await dispatch(hideSearchForm());
    try {
      const responseData = await search(
        searchQuery.location,
        searchQuery.keywords,
        searchQuery.timePeriod
      );
      track('Searched Results', {
        Location: searchQuery.location,
        Keywords: searchQuery.keywords,
        Tab: searchQuery.timePeriod,
        'Result Count': responseData.results.length,
        'Onebox Count': responseData.onebox_links.length,
      });
      await dispatch(searchComplete(responseData));
    } catch (e) {
      // TODO: error fetching events.
      console.log('Error fetching events', e.message, e, e.stack);
      await dispatch(searchFailed(e.message));
    }
  };
}

export function setWaitingForLocationPermission(waiting: boolean): Action {
  return {
    type: 'WAITING_FOR_LOCATION',
    waiting,
  };
}

function searchStart(): Action {
  return {
    type: 'START_SEARCH',
  };
}

function searchComplete(response: SearchResponse): Action {
  return {
    type: 'SEARCH_COMPLETE',
    response,
  };
}

function searchFailed(errorString: string): Action {
  return {
    type: 'SEARCH_FAILED',
    errorString,
  };
}
