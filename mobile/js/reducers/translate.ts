/**
 * Copyright 2016 DanceDeets.
 */

import type { Action } from '../actions/types';

export interface TranslatedEvent {
  visible: boolean;
  translation: {
    name: string;
    description: string;
  };
}

interface State {
  events: { [key: string]: TranslatedEvent };
}

const initialState: State = {
  events: {},
};

export function translate(state: State = initialState, action: Action): State {
  if (action.type === 'TRANSLATE_EVENT_DONE') {
    return {
      ...state,
      events: {
        ...state.events,
        [action.eventId]: {
          visible: true,
          translation: action.translations,
        },
      },
    };
  }
  if (action.type === 'TRANSLATE_EVENT_TOGGLE') {
    return {
      ...state,
      events: {
        ...state.events,
        [action.eventId]: {
          ...state.events[action.eventId],
          visible: !state.events[action.eventId].visible,
        },
      },
    };
  }
  return state;
}
