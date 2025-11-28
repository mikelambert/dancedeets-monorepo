/**
 * Copyright 2016 DanceDeets.
 */

import { Event } from 'dancedeets-common/js/events/models';
import type { Action } from '../actions/types';

export interface LoadedEventState {
  loading: boolean;
  event?: Event;
}

type State = { [key: string]: LoadedEventState };

const initialState: State = {};

export function loadedEvents(
  state: State = initialState,
  action: Action
): State {
  if (action.type === 'LOAD_EVENT_START') {
    return {
      ...state,
      [action.eventId]: {
        loading: true,
      },
    };
  }
  if (action.type === 'LOAD_EVENT_DONE') {
    return {
      ...state,
      [action.eventId]: {
        loading: false,
        event: action.event,
      },
    };
  }
  return state;
}
