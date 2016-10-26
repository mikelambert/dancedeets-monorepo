/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { translateEvent as translateEventApi } from '../api/dancedeets';
import type { Action, Dispatch, ThunkAction } from './types';
import { canGetValidLoginFor } from '../login/logic';

export function toggleEventTranslation(eventId: string, language: string): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const state = getState();
    if (!state.translate.events[eventId]) {
      // Lookup translation
      if (!state.user.userData && !await canGetValidLoginFor('Translation', dispatch)) {
        return;
      }
      const translations = await translateEventApi(eventId, language);
      await dispatch(eventTranslated(eventId, translations));
    } else {
      await dispatch(reallyToggleEventTranslation(eventId));
    }
  };
}

function reallyToggleEventTranslation(eventId: string): Action {
  return {
    type: 'TRANSLATE_EVENT_TOGGLE',
    eventId,
  };
}

function eventTranslated(eventId: string, translations: Object): Action {
  return {
    type: 'TRANSLATE_EVENT_DONE',
    eventId,
    translations,
  };
}

