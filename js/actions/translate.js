/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { translateEvent as translateEventApi } from '../api/dancedeets';
import type { Action, Dispatch, ThunkAction } from './types';

export function toggleEventTranslation(eventId: string, language: string): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    if (!getState().translate.events[eventId]) {
      // Lookup translation
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

