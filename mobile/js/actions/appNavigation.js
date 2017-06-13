/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { NavigationActions } from 'react-navigation';
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
      await dispatch(
        NavigationActions.navigate({
          routeName: 'Events',
          params: {},
          action: NavigationActions.navigate({
            routeName: 'EventList',
          }),
        })
      );
      await dispatch(updateLocation(processedUrl.location()));
      await dispatch(updateKeywords(processedUrl.keywords()));
      dispatch(performSearch());
    }
  };
}

export function appNavigateToEvent(navigateEvent: Event): ThunkAction {
  return async (dispatch: Dispatch) => {
    await dispatch(
      NavigationActions.navigate({
        routeName: 'Events',
        params: {},
        action: NavigationActions.navigate({
          routeName: 'EventView',
          params: { event: navigateEvent },
        }),
      })
    );
  };
}
