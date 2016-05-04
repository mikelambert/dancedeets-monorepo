/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import querystring from 'querystring';
import { Platform } from 'react-native';

function getUrl(path: string, args: Object) {
  var baseUrl = 'http://www.dancedeets.com/api/v1.2/';
  var fullArgs = Object.assign({}, args, {client: Platform.OS});
  var formattedArgs = querystring.stringify(fullArgs);
  var fullPath = baseUrl + path;
  if (formattedArgs) {
    fullPath += '?' + formattedArgs;
  }
  return fullPath;
}

function performRequest(path: string, args: Object, postArgs: ?Object | null) {
  console.log(getUrl(path, args));
  return fetch(getUrl(path, args), {
    method: postArgs ? 'POST' : 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    body: postArgs ? JSON.stringify(postArgs) : null,
  });
}

export function auth(token: Object) {
  return performRequest('auth', {}, {
    client: Platform.OS,
    access_token: token.tokenString,
    access_token_expires: new Date(token.expirationDate).toISOString(),
  });
}

export type TimePeriod = 'UPCOMING' | 'ONGOING' | 'PAST' | 'ALL_FUTURE';

export function search(location: string, keywords: string, time_period: TimePeriod) {
  return performRequest('search', {
    location,
    keywords,
    time_period,
  });
}

