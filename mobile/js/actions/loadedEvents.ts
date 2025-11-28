/**
 * Copyright 2016 DanceDeets.
 */

import { Event } from 'dancedeets-common/js/events/models';
import type { Action, Dispatch, ThunkAction, GetState } from './types';
import { event } from '../api/dancedeets';

export function loadEvent(eventId: string): ThunkAction {
  return async (dispatch: Dispatch, getState: GetState) => {
    const state = getState();
    const loadedEventState = state.loadedEvents[eventId];
    if (!loadedEventState) {
      await dispatch(loadEventInProgress(eventId));
      const realEvent = await event(eventId);
      await dispatch(loadEventFinished(eventId, realEvent));
    }
  };
}

function loadEventInProgress(eventId: string): Action {
  return {
    type: 'LOAD_EVENT_START',
    eventId,
  };
}

// We pass eventId and event, just to be sure we clear up the right state in case there are server bugs
function loadEventFinished(eventId: string, loadedEvent: Event): Action {
  return {
    type: 'LOAD_EVENT_DONE',
    eventId,
    event: loadedEvent,
  };
}
