/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import querystring from 'querystring';
import { Platform } from 'react-native';
import { AccessToken } from 'react-native-fbsdk';
import Locale from 'react-native-locale';
import moment from 'moment';
import { Event } from 'dancedeets-common/js/events/models';
import type { TimePeriod } from 'dancedeets-common/js/events/search';
import { sortString } from 'dancedeets-common/js/util/sort';
import {
  idempotentRetry,
  performRequest as realPerformRequest,
} from 'dancedeets-common/js/api/dancedeets';
import { timeout, retryWithBackoff } from 'dancedeets-common/js/api/timeouts';
import type { TokenRegistration } from '../store/track';

let writesDisabled = false;

export function disableWrites() {
  writesDisabled = true;
}

async function performRequest(
  path: string,
  args: Object,
  postArgs: ?Object | null
): Promise<Object> {
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
  return realPerformRequest(fetch, path, newArgs, newPostArgs, '1.4');
}

export async function isAuthenticated() {
  return AccessToken.getCurrentAccessToken();
}

async function verifyAuthenticated(location: string) {
  if (!await isAuthenticated()) {
    throw new Error(`Not authenticated in ${location}`);
  }
}

export async function saveToken(tokenRegistration: TokenRegistration) {
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
let saveForAuth = {};

export function saveForLaterAuth(data: ?Object) {
  saveForAuth = data;
}

export async function auth(data: ?Object) {
  if (writesDisabled) {
    return null;
  }
  await verifyAuthenticated('auth');

  // Grab any saveForAuth data and pass it in to the auth() call
  const finalData = { ...saveForAuth, ...data };
  saveForAuth = {};

  return idempotentRetry(2000, () => performRequest('auth', {}, finalData));
}

export async function feed(url: string) {
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

export async function search(
  location: string,
  keywords: string,
  timePeriod: TimePeriod
) {
  const response = await timeout(
    10000,
    performRequest('search', {
      location,
      keywords,
      time_period: timePeriod,
    })
  );
  response.featuredInfos = response.featuredInfos.map(x => ({
    ...x,
    event: new Event(x.event),
  }));
  response.results = response.results.map(x => new Event(x));
  return response;
}

export async function people(location: string) {
  const response = await timeout(
    10000,
    performRequest('people', {
      location,
    })
  );
  return response;
}

export async function event(id: string) {
  const eventData = await timeout(5000, performRequest(`events/${id}`, {}));
  return new Event(eventData);
}

export async function getAddEvents(): Promise<Object> {
  await verifyAuthenticated('getAddEvents');
  return timeout(10000, performRequest('events_list_to_add', {}));
}

export async function userInfo(): Promise<Object> {
  await verifyAuthenticated('userInfo');
  return retryWithBackoff(2000, 2, 5, () => performRequest('user/info', {}));
}

export async function addEvent(eventId: string): Promise<Object> {
  if (writesDisabled) {
    return new Promise(() => null);
  }
  await verifyAuthenticated('addEvent');
  return retryWithBackoff(2000, 2, 3, () =>
    performRequest('events_add', { event_id: eventId }, { event_id: eventId })
  );
}

export async function translateEvent(
  eventId: string,
  language: string
): Promise<Object> {
  await verifyAuthenticated('translateEvent');
  const params = { event_id: eventId, language };
  return timeout(10000, performRequest('events_translate', params, params));
}

export async function eventRegister(
  eventId: string,
  categoryId: string,
  values: Object
): Promise<Object> {
  await verifyAuthenticated('eventRegister');
  const params = { event_id: eventId, category_id: categoryId, ...values };
  return performRequest('event_signups/register', params, params);
}

export async function eventUnregister(
  eventId: string,
  categoryId: string,
  signupId: string
): Promise<Object> {
  await verifyAuthenticated('eventUnregister');
  const params = {
    event_id: eventId,
    category_id: categoryId,
    signup_id: signupId,
  };
  return performRequest('event_signups/unregister', params, params);
}
