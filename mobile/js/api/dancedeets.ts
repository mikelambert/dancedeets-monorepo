/**
 * Copyright 2016 DanceDeets.
 */

import { Platform } from 'react-native';
import { AccessToken } from 'react-native-fbsdk';
import Locale from 'react-native-locale';
import { Event, SearchEvent } from 'dancedeets-common/js/events/models';
import { TimePeriod } from 'dancedeets-common/js/events/search';
import {
  idempotentRetry,
  performRequest as realPerformRequest,
} from 'dancedeets-common/js/api/dancedeets';
import { timeout, retryWithBackoff } from 'dancedeets-common/js/api/timeouts';
import { TokenRegistration } from '../store/track';

let writesDisabled = false;

export function disableWrites(): void {
  writesDisabled = true;
}

async function performRequest(
  path: string,
  args: Record<string, any>,
  postArgs: Record<string, any> | null = null
): Promise<any> {
  // Standardize our API args with additional data
  const client = `react-${Platform.OS}`;
  const locale = Locale.constants()
    .localeIdentifier.split('_')[0]
    .split('-')[0];
  const newArgs = Object.assign({}, args, {
    client,
    locale,
  });
  const token = await AccessToken.getCurrentAccessToken();
  const newPostArgs = Object.assign({}, postArgs, {
    client,
    locale,
    access_token: token ? token.accessToken : null,
  });
  return await realPerformRequest(fetch, path, newArgs, newPostArgs, '2.0');
}

export async function isAuthenticated(): Promise<any> {
  return await AccessToken.getCurrentAccessToken();
}

async function verifyAuthenticated(location: string): Promise<void> {
  if (!await isAuthenticated()) {
    throw new Error(`Not authenticated in ${location}`);
  }
}

export async function saveToken(tokenRegistration: TokenRegistration): Promise<void> {
  const fbToken = await AccessToken.getCurrentAccessToken();
  // Make sure we are logged-in before we call auth(), otherwise save it for later
  const eventuallySaveToken = fbToken ? auth : saveForLaterAuth;
  if (tokenRegistration.os === 'android') {
    eventuallySaveToken({ android_device_token: tokenRegistration.token });
  } else {
    // eventuallySaveToken({ios_device_token: tokenData.token});
  }
}

// Where we store off any android/ios tokens, for later passing to auth() when we authorize properly
let saveForAuth: Record<string, any> = {};

export function saveForLaterAuth(data?: Record<string, any>): void {
  saveForAuth = data || {};
}

export async function auth(data?: Record<string, any>): Promise<any> {
  if (writesDisabled) {
    return null;
  }
  await verifyAuthenticated('auth');

  // Grab any saveForAuth data and pass it in to the auth() call
  const finalData = { ...saveForAuth, ...data };
  saveForAuth = {};

  return await idempotentRetry(2000, () =>
    performRequest('auth', {}, finalData)
  );
}

export async function feed(url: string): Promise<any> {
  const response = await timeout(
    10000,
    performRequest(
      'feed',
      {
        url,
      },
      {
        url,
      }
    )
  );
  return response;
}

interface FeaturedInfo {
  event: Event;
  [key: string]: any;
}

interface MobileSearchResponse {
  featuredInfos: FeaturedInfo[];
  results: SearchEvent[];
  people?: any;
  onebox_links?: any[];
  query?: any;
  [key: string]: any;
}

export async function search(
  location: string,
  keywords: string,
  timePeriod: TimePeriod
): Promise<MobileSearchResponse> {
  const response: any = await timeout(
    10000,
    performRequest('search', {
      location,
      keywords,
      time_period: timePeriod,
    })
  );
  response.featuredInfos = response.featuredInfos.map((x: any) => ({
    ...x,
    event: new Event(x.event),
  }));
  response.results = response.results.map((x: any) => new SearchEvent(x));
  return response;
}

export async function people(location: string): Promise<any> {
  const response = await timeout(
    10000,
    performRequest('people', {
      location,
    })
  );
  return response;
}

export async function event(id: string): Promise<Event> {
  const eventData = await timeout(5000, performRequest(`events/${id}`, {}));
  return new Event(eventData);
}

export async function getAddEvents(): Promise<any> {
  await verifyAuthenticated('getAddEvents');
  return await timeout(10000, performRequest('events_list_to_add', {}));
}

export async function userInfo(): Promise<any> {
  await verifyAuthenticated('userInfo');
  return await retryWithBackoff(2000, 2, 5, () =>
    performRequest('user/info', {})
  );
}

export async function addEvent(eventId: string): Promise<any> {
  if (writesDisabled) {
    return new Promise(() => null);
  }
  await verifyAuthenticated('addEvent');
  return await retryWithBackoff(2000, 2, 3, () =>
    performRequest('events_add', { event_id: eventId }, { event_id: eventId })
  );
}

export async function translateEvent(
  eventId: string,
  language: string
): Promise<any> {
  await verifyAuthenticated('translateEvent');
  const params = { event_id: eventId, language };
  return await timeout(
    10000,
    performRequest('events_translate', params, params)
  );
}

export async function eventRegister(
  eventId: string,
  categoryId: string,
  values: Record<string, any>
): Promise<any> {
  await verifyAuthenticated('eventRegister');
  const params = { event_id: eventId, category_id: categoryId, ...values };
  return await performRequest('event_signups/register', params, params);
}

export async function eventUnregister(
  eventId: string,
  categoryId: string,
  signupId: string
): Promise<any> {
  await verifyAuthenticated('eventUnregister');
  const params = {
    event_id: eventId,
    category_id: categoryId,
    signup_id: signupId,
  };
  return await performRequest('event_signups/unregister', params, params);
}
