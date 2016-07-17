/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { translateEvent as translateEventApi } from '../api/dancedeets';

export function translateEvent(eventId: string, language: string): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const translations = await translateEventApi(eventId, language);
    await dispatch(eventTranslated(eventId, translations));
  }
}

export function eventTranslated(eventId: string, translations: Object): Action {
  return {
    type: 'TRANSLATE_EVENT_DONE',
    eventId,
    translations,
  };
}

