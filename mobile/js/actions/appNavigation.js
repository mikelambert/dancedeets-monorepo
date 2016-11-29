/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { Action, ThunkAction, Dispatch } from './types';

import { Event } from '../events/models';
import { selectTab } from './mainTabs';
import { navigatePop, navigatePush } from './navigation';
import WebsiteUrl from '../websiteUrl';
import {
  event,
} from '../api/dancedeets';
import {
  performSearch,
  updateKeywords,
  updateLocation,
} from './search';

export function processUrl(url: string) {
  console.log(url);
  return async (dispatch: Dispatch) => {
    const processedUrl = url ? new WebsiteUrl(url) : null;
    if (processedUrl && processedUrl.isEventUrl()) {
      const eventId = processedUrl.eventId();
      const eventData = await event(eventId);
      dispatch(appNavigateToEvent(eventData));
    } else if (processedUrl && processedUrl.isSearchUrl()) {
      const navName = 'EVENT_NAV';
      await dispatch(selectTab('events'));
      await dispatch(navigatePop(navName));
      await dispatch(navigatePop(navName));
      await dispatch(updateLocation(processedUrl.location()));
      await dispatch(updateKeywords(processedUrl.keywords()));
      dispatch(performSearch());
    }
  }
}

export function appNavigateToEvent(event: Event): ThunkAction {
  return async (dispatch: Dispatch, getState) => {
    const navName = 'EVENT_NAV';
    const destState = {key: 'EventView', title: event.name, event: event};
    await dispatch(selectTab('events'));
    await dispatch(navigatePop(navName));
    await dispatch(navigatePop(navName));
    await dispatch(navigatePush(navName, destState));
  }
}
