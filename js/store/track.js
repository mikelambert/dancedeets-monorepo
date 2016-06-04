/**
 * Copyright 2016 Facebook, Inc.
 *
 * You are hereby granted a non-exclusive, worldwide, royalty-free license to
 * use, copy, modify, and distribute this software in source code or binary
 * form for use in connection with the web services and APIs provided by
 * Facebook.
 *
 * As with any software that integrates with the Facebook platform, your use
 * of this software is subject to the Facebook Developer Principles and
 * Policies [http://developers.facebook.com/policy/]. This copyright notice
 * shall be included in all copies or substantial portions of the software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE
 *
 * @flow
 */

'use strict';

import Mixpanel from 'react-native-mixpanel';
import {AppEventsLogger} from 'react-native-fbsdk';
import { AccessToken } from 'react-native-fbsdk';
import { performRequest } from '../api/fb';

import type {Action} from '../actions/types';
import type {Event} from '../events/models';

// TODO: Implement GA: https://github.com/lwansbrough/react-native-google-analytics ?
// TODO: Implement Firebase Analytics

function initMixpanel() {
  let mixpanelApiKey = null;
  if (__DEV__) {
    mixpanelApiKey = '668941ad91e251d2ae9408b1ea80f67b';
  } else {
    mixpanelApiKey = 'f5d9d18ed1bbe3b190f9c7c7388df243';
  }

  return Mixpanel.sharedInstanceWithToken(mixpanelApiKey);
}

initMixpanel();

type Params = {[key: string]: string | number};

function track(eventName: string, params: ?Params) {
  if (params) {
    AppEventsLogger.logEvent(eventName, 1, params);
    Mixpanel.trackWithProperties(eventName, params);
  } else {
    AppEventsLogger.logEvent(eventName, 1);
    Mixpanel.track(eventName);
  }
}

function trackWithEvent(eventName: string, event: Event) {
  const venue = event.venue || null;
  const extraParams: Params = {
    'Event ID': event.id,
    'Event City': venue ? venue.cityStateCountry() : '',
    'Event Country': venue.address ? venue.address.country : '',
  };
  track(eventName, extraParams);
}

async function setupPersonProperties(token: AccessToken) {
  Mixpanel.identify(token.userID);

  const user = await performRequest('GET', 'me', {fields: 'id,name,first_name,last_name,gender,locale,timezone,email,link'});
  Mixpanel.set('$first_name', user.first_name);
  Mixpanel.set('$last_name', user.last_name);
  Mixpanel.set('FB Gender', user.gender);
  Mixpanel.set('FB Locale', user.locale);
  Mixpanel.set('FB Timezone', user.timezone);
  Mixpanel.set('$email', user.email);

  const now = new Date().toISOString().slice(0,19); // Trim off the fractional seconds from our ISO?UTC time
  Mixpanel.set('Last Login', now);
  Mixpanel.setOnce('$created', now);
}

export default function trackDispatches(action: Action): void {
  switch (action.type) {
    case 'LOGIN_LOGGED_IN':
      // We must call identify *first*, before calling setDeviceToken() or login().
      // This ensures the latter functions operate against the correct user.
      // TODO: Retrieve push token
      //Mixpanel.addPushDeviceToken(...);
      setupPersonProperties(action.token);
      track('Login');
      break;

    case 'LOGIN_LOGGED_OUT':
      track('Logout');
      Mixpanel.removePushToken();
      Mixpanel.reset();
      break;

    case 'VIEW_EVENT':
      trackWithEvent('View Event', action.event);
      break;

    case 'START_SEARCH':
      track('Search Events', {
        'Location': action.searchQuery.location,
        'Keywords': action.searchQuery.keywords,
      });
      break;
  }
}
