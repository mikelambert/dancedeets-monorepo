/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';


const initialState = {
  events: {},
};

export function translate(state: State = initialState, action: Action): State {
  if (action.type === 'TRANSLATE_EVENT_DONE') {
    return {
      ...state,
      events: {
        ...state.events,
        [action.eventId]: action.translations,
      },
    }
    return initialState;
  }
  return state;
}
