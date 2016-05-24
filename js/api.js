/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import querystring from 'querystring';
import { Platform } from 'react-native';
import { AccessToken } from 'react-native-fbsdk';
import type { TimePeriod } from './events/search';

const DEV_SERVER = false;

function getUrl(path: string, args: Object) {
  const baseUrl = DEV_SERVER ? 'http://dev.dancedeets.com:8080/api/v1.2/' : 'http://www.dancedeets.com/api/v1.2/';
  const fullArgs = Object.assign({}, args, {client: Platform.OS});
  const formattedArgs = querystring.stringify(fullArgs);
  var fullPath = baseUrl + path;
  if (formattedArgs) {
    fullPath += '?' + formattedArgs;
  }
  return fullPath;
}

async function performRequest(path: string, args: Object, postArgs: ?Object | null) {
  try {
    console.log('JSON API:', getUrl(path, args));
    const result = await fetch(getUrl(path, args), {
      method: postArgs ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      body: postArgs ? JSON.stringify(postArgs) : null,
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

export async function auth(token: ?AccessToken, data: ?Object) {
  if (!token) {
    token = await AccessToken.getCurrentAccessToken();
  }
  if (!token) {
    return;
  }
  if (data == null) {
    data = {};
  }
  const postData = Object.assign({}, {
    client: Platform.OS,
    access_token: token.accessToken,
  }, data);
  return performRequest('auth', {}, postData);
}

export async function search(location: string, keywords: string, time_period: TimePeriod) {
  return performRequest('search', {
    location,
    keywords,
    time_period,
  });
}

