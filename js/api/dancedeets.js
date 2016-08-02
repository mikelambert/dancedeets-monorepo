/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import querystring from 'querystring';
import { Platform } from 'react-native';
import { AccessToken } from 'react-native-fbsdk';
import type { TimePeriod } from '../events/search';
import { Event } from '../events/models';
import { timeout, retryWithBackoff } from './timeouts';
import Locale from 'react-native-locale';

const DEV_SERVER = false;

function getUrl(path: string, args: Object) {
  const baseUrl = DEV_SERVER ? 'http://dev.dancedeets.com:8080/api/v1.2/' : 'http://www.dancedeets.com/api/v1.2/';
  const formattedArgs = querystring.stringify(args);
  var fullPath = baseUrl + path;
  if (formattedArgs) {
    fullPath += '?' + formattedArgs;
  }
  return fullPath;
}

async function performRequest(path: string, args: Object, postArgs: ?Object | null) {
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
      throw json['errors'];
    } else {
      return json;
    }
  } catch (e) {
    console.warn('Error on API call:', path, 'withArgs:', args, '. Error:', e);
    throw e;
  }
}

function createRequest(path: string, args: Object, postArgs: ?Object | null) {
  return () => performRequest(path, args, postArgs);
}

function idempotentRetry(timeoutMs: number, promiseGenerator: () => Promise) {
  return retryWithBackoff(timeoutMs, 2, 5, promiseGenerator);
}

async function verifyAuthenticated() {
  const token = await AccessToken.getCurrentAccessToken();
  if (!token) {
    throw 'Not authenticated!';
  }
}

export async function auth(data: ?Object) {
  await verifyAuthenticated();
  return idempotentRetry(2000, createRequest('auth', {}, data));
}

export async function search(location: string, keywords: string, time_period: TimePeriod) {
  let results = await timeout(10000, performRequest('search', {
    location,
    keywords,
    time_period,
  }));
  results.results = results.results.map((x) => new Event(x));
  return results;
}

export async function event(id: string) {
  const eventData = await timeout(5000, performRequest('events/' + id, {}));
  return new Event(eventData);
}

export async function getAddEvents() {
  await verifyAuthenticated();
  return await timeout(10000, performRequest('events_list_to_add', {}));
}

export async function userInfo() {
  await verifyAuthenticated();
  return await retryWithBackoff(2000, 2, 5, createRequest('user/info', {}));
}

export async function addEvent(eventId: string) {
  await verifyAuthenticated();
  return await retryWithBackoff(2000, 2, 3, createRequest('events_add', {event_id: eventId}, {event_id: eventId}));
}

export async function translateEvent(eventId: string) {
  await verifyAuthenticated();
  const params = {event_id: eventId};
  return await timeout(10000, performRequest('events_translate', params, params));
}

