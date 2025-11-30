/**
 * Copyright 2016 DanceDeets.
 */

import { defineMessages, IntlShape } from 'react-intl';
import { translateEvent as translateEventApi } from '../api/dancedeets';
import type { Action, Dispatch, ThunkAction, GetState } from './types';
import { canGetValidLoginFor } from './loginComplex';

const messages = defineMessages({
  featureTranslation: {
    id: 'feature.translation',
    defaultMessage: 'Translation',
    description:
      'The name of the Translation feature when requesting permissions',
  },
});

interface TranslateState {
  translate: {
    events: Record<string, { translations: Record<string, unknown>; expanded: boolean }>;
  };
  user: {
    userData: unknown;
  };
}

export function toggleEventTranslation(
  eventId: string,
  language: string,
  intl: IntlShape
): ThunkAction {
  return async (dispatch: Dispatch, getState: GetState) => {
    const state = getState() as unknown as TranslateState;
    if (!state.translate.events[eventId]) {
      // Lookup translation
      if (
        !state.user.userData &&
        !(await canGetValidLoginFor(
          intl.formatMessage(messages.featureTranslation),
          intl,
          dispatch
        ))
      ) {
        return;
      }
      const translations = await translateEventApi(eventId, language) as { name: string; description: string };
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

function eventTranslated(eventId: string, translations: { name: string; description: string }): Action {
  return {
    type: 'TRANSLATE_EVENT_DONE',
    eventId,
    translations,
  };
}
