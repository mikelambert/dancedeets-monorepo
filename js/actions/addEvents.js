/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { Action, ThunkAction, Dispatch } from './types';
import type { AddEventList } from '../addEventsModels';

import { getAddEvents } from '../api/dancedeets';


export function performSearch(): ThunkAction {
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
