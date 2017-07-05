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
import type { TokenRegistration } from '../store/track';
import { timeout, retryWithBackoff } from './timeouts';

const DEV_SERVER = false;

let writesDisabled = false;

export function disableWrites() {
  writesDisabled = true;
}

function getUrl(path: string, args: Object) {
  const version = '1.4';
  const baseUrl = DEV_SERVER
    ? `http://dev.dancedeets.com:8080/api/v${version}/`
    : `https://www.dancedeets.com/api/v${version}/`;
  const formattedArgs = querystring.stringify(args);
  let fullPath = baseUrl + path;
  if (formattedArgs) {
    fullPath += `?${formattedArgs}`;
  }
  return fullPath;
}

async function performRequest(
  path: string,
  args: Object,
  postArgs: ?Object | null
): Promise<Object> {
  try {
    // Standardize our API args with additional data
    const client = `react-${Platform.OS}`;
    const locale = Locale.constants()
      .localeIdentifier.split('_')[0]
      .split('-')[0];
    const fullArgs = Object.assign({}, args, {
      client,
      locale,
    });
    const token = await AccessToken.getCurrentAccessToken();
    const fullPostData = Object.assign({}, postArgs, {
      client,
      locale,
      access_token: token ? token.accessToken : null,
    });

    console.log('JSON API:', getUrl(path, fullArgs));
    const result = await fetch(getUrl(path, fullArgs), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(fullPostData),
    });
    // This setTimeout kicks the eventloop so it doesn't fall asleep.
    // Workaround for https://github.com/facebook/react-native/issues/14391
    setTimeout(() => null, 0);
    const json = await result.json();
    // 'undefined' means success, 'false' means error
    if (json.success === false) {
      throw new Error(`${json.errors}`);
    } else {
      return json;
    }
  } catch (e) {
    console.warn(
      'Error on API call:',
      path,
      'withArgs:',
      args,
      '. Error:',
      e.message,
      e
    );
    throw e;
  }
}

function createRequest(
  path: string,
  args: Object,
  postArgs: ?Object | null
): () => Promise<Object> {
  return () => performRequest(path, args, postArgs);
}

function idempotentRetry(
  timeoutMs: number,
  promiseGenerator: () => Promise<() => Promise<Object>>
) {
  return retryWithBackoff(timeoutMs, 2, 5, promiseGenerator);
}

export async function isAuthenticated() {
  return await AccessToken.getCurrentAccessToken();
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

  return idempotentRetry(2000, createRequest('auth', {}, finalData));
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
  response.results = sortString(response.results, resultEvent =>
    moment(resultEvent.start_time).toISOString()
  );
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

export async function getAddEvents(): Promise<> {
  await verifyAuthenticated('getAddEvents');
  return await timeout(10000, performRequest('events_list_to_add', {}));
}

export async function userInfo() {
  await verifyAuthenticated('userInfo');
  return await retryWithBackoff(2000, 2, 5, createRequest('user/info', {}));
}

export async function addEvent(eventId: string) {
  if (writesDisabled) {
    return null;
  }
  await verifyAuthenticated('addEvent');
  return await retryWithBackoff(
    2000,
    2,
    3,
    createRequest('events_add', { event_id: eventId }, { event_id: eventId })
  );
}

export async function translateEvent(eventId: string) {
  await verifyAuthenticated('translateEvent');
  const params = { event_id: eventId };
  return await timeout(
    10000,
    performRequest('events_translate', params, params)
  );
}

export async function eventRegister(
  eventId: string,
  categoryId: string,
  values: Object
) {
  await verifyAuthenticated('eventRegister');
  const params = { event_id: eventId, category_id: categoryId, ...values };
  return await performRequest('event_signups/register', params, params);
}

export async function eventUnregister(
  eventId: string,
  categoryId: string,
  signupId: string
) {
  await verifyAuthenticated('eventUnregister');
  const params = {
    event_id: eventId,
    category_id: categoryId,
    signup_id: signupId,
  };
  return await performRequest('event_signups/unregister', params, params);
}
