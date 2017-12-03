/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { defineMessages, intlShape } from 'react-intl';
import { Event } from 'dancedeets-common/js/events/models';
import type { Action, Dispatch, ThunkAction } from './types';
import { event } from '../api/dancedeets';

export function loadEvent(eventId: string): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const state = getState();
    const loadedEventState = state.loadedEvents[eventId];
    console.log('c2', eventId, loadedEventState);
    if (!loadedEventState) {
      console.log('d');
      await dispatch(loadEventInProgress(eventId));
      console.log('e');
      console.log('e2', event(eventId));
      console.log('e3', await event(eventId));
      const realEvent = await event(eventId);
      console.log('f');
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
function loadEventFinished(eventId: string, event: Event): Action {
  return {
    type: 'LOAD_EVENT_DONE',
    eventId,
    event,
  };
}
