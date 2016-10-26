/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { translateEvent as translateEventApi } from '../api/dancedeets';
import type { Action, Dispatch, ThunkAction } from './types';
import { canGetValidLoginFor } from './loginComplex';
import {
  defineMessages,
  intlShape,
} from 'react-intl';

const messages = defineMessages({
  featureTranslation: {
    id: 'feature.translation',
    defaultMessage: 'Translation',
    description: 'The name of the Translation feature when requesting permissions',
  },
});

export function toggleEventTranslation(eventId: string, language: string, intl: intlShape): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const state = getState();
    if (!state.translate.events[eventId]) {
      // Lookup translation
      if (!state.user.userData && !await canGetValidLoginFor(intl.formatMessage(messages.featureTranslation), intl, dispatch)) {
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
