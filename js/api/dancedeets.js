/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { TimePeriod } from '../events/search';
import type { TokenRegistration } from '../store/track';
import querystring from 'querystring';
import { Platform } from 'react-native';
import { AccessToken } from 'react-native-fbsdk';
import { Event } from '../events/models';
import { timeout, retryWithBackoff } from './timeouts';
import Locale from 'react-native-locale';
import sort from '../util/sort';
import moment from 'moment';

const DEV_SERVER = false;

let writesDisabled = false;

export function disableWrites() {
  writesDisabled = true;
}

function getUrl(path: string, args: Object) {
  const baseUrl = DEV_SERVER ? 'http://dev.dancedeets.com:8080/api/v1.2/' : 'http://www.dancedeets.com/api/v1.2/';
  const formattedArgs = querystring.stringify(args);
  var fullPath = baseUrl + path;
  if (formattedArgs) {
    fullPath += '?' + formattedArgs;
  }
  return fullPath;
}

async function performRequest(path: string, args: Object, postArgs: ?Object | null): Promise<Object> {
  try {
    // Standardize our API args with additional data
    const client = 'react-' + Platform.OS;
    const locale = Locale.constants().localeIdentifier.split('_')[0].split('-')[0];
    const fullArgs = Object.assign({}, args, {
      client,
      locale,
    });
    const token = await AccessToken.getCurrentAccessToken();
    const fullPostData = Object.assign({}, postArgs, {
      client,
      locale,
      'access_token': token ? token.accessToken : null,
    });

    console.log('JSON API:', getUrl(path, fullArgs));
    const result = await fetch(getUrl(path, fullArgs), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(fullPostData),
    });
    const json = await result.json();
    // 'undefined' means success, 'false' means error
    if (json['success'] === false) {
      throw new Error('Server Error: ' + json['errors']);
    } else {
      return json;
    }
  } catch (e) {
    console.warn('Error on API call:', path, 'withArgs:', args, '. Error:', e);
    throw e;
  }
}

function createRequest(path: string, args: Object, postArgs: ?Object | null): () => Promise<Object> {
  return () => performRequest(path, args, postArgs);
}

function idempotentRetry(timeoutMs: number, promiseGenerator: () => Promise<() => Promise<Object>>) {
  return retryWithBackoff(timeoutMs, 2, 5, promiseGenerator);
}

export async function isAuthenticated() {
  return await AccessToken.getCurrentAccessToken();
}

async function verifyAuthenticated() {
  if (!await isAuthenticated()) {
    throw new Error('Not authenticated!');
  }
}

export async function saveToken(tokenRegistration: TokenRegistration) {
  const fbToken = await AccessToken.getCurrentAccessToken();
  // Make sure we are logged-in before we call auth(), otherwise save it for later
  let eventuallySaveToken = fbToken ? auth : saveForLaterAuth;
  if (tokenRegistration.os === 'android') {
    eventuallySaveToken({android_device_token: tokenRegistration.token});
  } else {
    //eventuallySaveToken({ios_device_token: tokenData.token});
  }
}

// Where we store off any android/ios tokens, for later passing to auth() when we authorize properly
let saveForAuth = {};

export function saveForLaterAuth(data: ?Object) {
  saveForAuth = data;
}

export async function auth(data: ?Object) {
  if (writesDisabled) {
    return;
  }
  await verifyAuthenticated();

  // Grab any saveForAuth data and pass it in to the auth() call
  const finalData = {...saveForAuth, ...data};
  saveForAuth = {};

  return idempotentRetry(2000, createRequest('auth', {}, finalData));
}

export async function feed(url: string) {
  let results = await timeout(10000, performRequest('feed', {
    url,
  }, {
    url,
  }));
  return results;
}

export async function search(location: string, keywords: string, time_period: TimePeriod) {
  let results = await timeout(10000, performRequest('search', {
    location,
    keywords,
    time_period,
  }));
  results.results = results.results.map((x) => new Event(x));
  results.results = sort(results.results, (resultEvent) => moment(resultEvent.start_time).toISOString());
  return results;
}

export async function event(id: string) {
  const eventData = await timeout(5000, performRequest('events/' + id, {}));
  return new Event(eventData);
}

export async function getAddEvents(): Promise<> {
  await verifyAuthenticated();
  return await timeout(10000, performRequest('events_list_to_add', {}));
}

export async function userInfo() {
  await verifyAuthenticated();
  return await retryWithBackoff(2000, 2, 5, createRequest('user/info', {}));
}

export async function addEvent(eventId: string) {
  if (writesDisabled) {
    return;
  }
  await verifyAuthenticated();
  return await retryWithBackoff(2000, 2, 3, createRequest('events_add', {event_id: eventId}, {event_id: eventId}));
}

export async function translateEvent(eventId: string) {
  await verifyAuthenticated();
  const params = {event_id: eventId};
  return await timeout(10000, performRequest('events_translate', params, params));
}

export async function eventRegister(eventId: string, categoryId: string, values: Object) {
  await verifyAuthenticated();
  const params = {event_id: eventId, category_id: categoryId, ...values};
  return await performRequest('event_signups/register', params, params);
}

export async function eventUnregister(eventId: string, categoryId: string, signupId: string) {
  await verifyAuthenticated();
  const params = {event_id: eventId, category_id: categoryId, signup_id: signupId};
  return await performRequest('event_signups/unregister', params, params);
}
