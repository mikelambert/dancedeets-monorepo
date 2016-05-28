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
    const fullArgs = Object.assign({}, args, {
      client,
    });
    const token = await AccessToken.getCurrentAccessToken();
    const fullPostData = Object.assign({}, postArgs, {
      client,
      'access_token': token ? token.accessToken : null,
    });

    console.log('JSON API:', getUrl(path, fullArgs));
    const result = await fetch(getUrl(path, args), {
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

async function verifyAuthenticated() {
  const token = await AccessToken.getCurrentAccessToken();
  if (!token) {
    throw 'Not authenticated!';
  }
}

export async function auth(data: ?Object) {
  await verifyAuthenticated();
  return performRequest('auth', {}, data);
}

export async function search(location: string, keywords: string, time_period: TimePeriod) {
  return performRequest('search', {
    location,
    keywords,
    time_period,
  });
}

export async function getAddEvents() {
  await verifyAuthenticated();
  return performRequest('events_list_to_add', {});
}

