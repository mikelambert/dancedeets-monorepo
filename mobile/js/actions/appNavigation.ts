/**
 * Copyright 2016 DanceDeets.
 *
 * Navigation actions for React Navigation v6.
 * Uses navigation ref for programmatic navigation.
 */

import { Event } from 'dancedeets-common/js/events/models';
import type { ThunkAction, Dispatch } from './types';
import WebsiteUrl from '../websiteUrl';
import { event } from '../api/dancedeets';
import { performSearch } from './search';
import { updateKeywords, updateLocation } from '../ducks/searchQuery';
import { navigationRef } from '../containers/TabApp';

export function processUrl(url: string): ThunkAction {
  console.log(url);
  return async (dispatch: Dispatch) => {
    const processedUrl = url ? new WebsiteUrl(url) : null;
    if (processedUrl && processedUrl.isEventUrl()) {
      const eventId = processedUrl.eventId();
      const eventData = await event(eventId);
      dispatch(appNavigateToEvent(eventData));
    } else if (processedUrl && processedUrl.isSearchUrl()) {
      // Navigate to Events tab and then to EventList screen
      navigationRef.current?.navigate('Events', {
        screen: 'EventList',
      });
      await dispatch(updateLocation(processedUrl.location() || ''));
      await dispatch(updateKeywords(processedUrl.keywords() || ''));
      dispatch(performSearch());
    }
  };
}

export function appNavigateToEvent(navigateEvent: Event): ThunkAction {
  return async (_dispatch: Dispatch) => {
    // Navigate to Events tab and then to EventView screen with event params
    navigationRef.current?.navigate('Events', {
      screen: 'EventView',
      params: { event: navigateEvent },
    });
  };
}
