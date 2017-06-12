/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { Event } from 'dancedeets-common/js/events/models';
import type { ThunkAction, Dispatch } from './types';
import WebsiteUrl from '../websiteUrl';
import { event } from '../api/dancedeets';
import { performSearch, updateKeywords, updateLocation } from './search';

export function processUrl(url: string) {
  console.log(url);
  return async (dispatch: Dispatch) => {
    const processedUrl = url ? new WebsiteUrl(url) : null;
    if (processedUrl && processedUrl.isEventUrl()) {
      const eventId = processedUrl.eventId();
      const eventData = await event(eventId);
      dispatch(appNavigateToEvent(eventData));
    } else if (processedUrl && processedUrl.isSearchUrl()) {
      /*
      TODO(navigation): navigate to Events tab, then go to top-level, then do a serach
      await dispatch(selectTab('events'));
      await dispatch(navigatePop(navName));
      await dispatch(navigatePop(navName));
      */
      await dispatch(updateLocation(processedUrl.location()));
      await dispatch(updateKeywords(processedUrl.keywords()));
      dispatch(performSearch());
    }
  };
}

export function appNavigateToEvent(navigateEvent: Event): ThunkAction {
  return async (dispatch: Dispatch) => {
    const navName = 'EVENT_NAV';
    const destState = {
      key: 'EventView',
      title: navigateEvent.name,
      event: navigateEvent,
    };
    /*
    TODO(navigation): navigate to Events tab, then go to top-level, then open an event
    await dispatch(selectTab('events'));
    await dispatch(navigatePop(navName));
    await dispatch(navigatePop(navName));
    await dispatch(navigatePush(navName, destState));
    */
  };
}
