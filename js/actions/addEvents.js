/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { Action, ThunkAction, Dispatch } from './types';
import type {
  AddEventList,
  SortOrder,
} from '../addEventsModels';

import { getAddEvents, addEvent as reallyAddEvent } from '../api/dancedeets';

export function reloadAddEvents(): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    await dispatch(reloadStart());
    try {
      const responseData = await getAddEvents();
      await dispatch(reloadComplete(responseData.events));
    } catch (e) {
      console.log('error fetching events', e, e.stack);
      await dispatch(reloadFailed());
    }
  };
}

export function reloadStart(): Action {
  return {
    type: 'ADD_EVENTS_RELOAD',
  };
}

export function reloadComplete(results: AddEventList): Action {
  return {
    type: 'ADD_EVENTS_RELOAD_COMPLETE',
    results,
  };
}

export function reloadFailed(): Action {
  return {
    type: 'ADD_EVENTS_RELOAD_FAILED',
  };
}

function markAsPending(eventId): Action {
  return {
    type: 'ADD_EVENTS_UPDATE_LOADED',
    status: 'PENDING',
    eventId: eventId,
  };
}

function markAsLoaded(eventId): Action {
  return {
    type: 'ADD_EVENTS_UPDATE_LOADED',
    status: 'LOADED',
    eventId: eventId,
  };
}

function markAsUnLoaded(eventId): Action {
  return {
    type: 'ADD_EVENTS_UPDATE_LOADED',
    status: 'UNLOADED',
    eventId: eventId,
  };
}

function alreadyProcessing(getState, eventId: string) {
  const results = getState().addEvents.results;
  if (!results) {
    return;
  }
  results.forEach((x) => {
    if (x.id === eventId) {
      if (x.loaded !== false) {
        return true;
      }
    }
  });
}

export function clickEvent(eventId: string) {
  return {
    type: 'ADD_EVENTS_UPDATE_LOADED',
    status: 'CLICKED',
    eventId: eventId,
  };
}

export function addEvent(eventId: string): ThunkAction {
  return async (dispatch, getState) => {
    try {
      // Ensure we don't double-post
      if (alreadyProcessing(getState, eventId)) {
        return;
      }
      await dispatch(markAsPending(eventId));
      await reallyAddEvent(eventId);
      await dispatch(markAsLoaded(eventId));
    } catch (e) {
      await dispatch(markAsUnLoaded(eventId));
    }
  };
}

export function setOnlyUnadded(value: boolean): Action {
  return {
    type: 'ADD_EVENTS_SET_ONLY_UNADDED',
    value,
  };
}

export function setSortOrder(value: SortOrder): Action {
  return {
    type: 'ADD_EVENTS_SET_SORT_ORDER',
    value,
  };
}
