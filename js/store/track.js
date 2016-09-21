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
// TODO(lambert): Eventually migrate this to react-native-firestack
import { Analytics } from 'react-native-firebase3';
import { AccessToken, AppEventsLogger } from 'react-native-fbsdk';
import { performRequest } from '../api/fb';

import type {Action} from '../actions/types';
import type {Event} from '../events/models';

let trackingEnabled = true;

export function disableTracking() {
  trackingEnabled = false;
}

function initMixpanel() {
  if (!trackingEnabled) {
    return;
  }
  let mixpanelApiKey = null;
  if (__DEV__) {
    mixpanelApiKey = '668941ad91e251d2ae9408b1ea80f67b';
  } else {
    mixpanelApiKey = 'f5d9d18ed1bbe3b190f9c7c7388df243';
  }

  const mixpanel = Mixpanel.sharedInstanceWithToken(mixpanelApiKey);
  // Don't use global track(), since this is a Mixpanel-only event:
  Mixpanel.track('$app_open');
  return mixpanel;
}

initMixpanel();

type Params = {[key: string]: string | number};

function firebaseSafe(str) {
  if (str != null) {
    return str.toString().replace(/\W/g, '');
  } else {
    return '';
  }
}

export function track(eventName: string, params: ?Params) {
  if (!trackingEnabled) {
    return;
  }
  if (params != null) {
    const firebaseSafeParams = {};
    for (let key of Object.keys(params)) {
      firebaseSafeParams[firebaseSafe(key)] = params[key];
    }
    AppEventsLogger.logEvent(eventName, 1, params);
    Mixpanel.trackWithProperties(eventName, params);
    Analytics.logEvent(firebaseSafe(eventName), firebaseSafeParams);
  } else {
    AppEventsLogger.logEvent(eventName, 1);
    Mixpanel.track(eventName);
    Analytics.logEvent(firebaseSafe(eventName));
  }
}

export function trackWithEvent(eventName: string, event: Event, params: ?Params) {
  if (!trackingEnabled) {
    return;
  }
  const venue = event.venue || null;
  const extraParams: Params = Object.assign({}, params, {
    'Event ID': event.id,
    'Event City': venue.address ? venue.cityStateCountry() : '',
    'Event Country': venue.address ? venue.address.country : '',
  });
  track(eventName, extraParams);
}

export type TokenRegistration = {
  os: 'android' | 'os';
  token: string;
};

export function setupToken(tokenData: TokenRegistration) {
  if (tokenData.os === 'android') {
    Mixpanel.setPushRegistrationId(tokenData.token);
  } else if (tokenData.os === 'ios') {
    Mixpanel.addPushDeviceToken(tokenData.token);
  }
}

async function setupPersonProperties() {
  const token = await AccessToken.getCurrentAccessToken();
  if (!token) {
    return;
  }
  Mixpanel.identify(token.userID);
  Analytics.setUserId(token.userID);

  const user = await performRequest('GET', 'me', {fields: 'id,name,first_name,last_name,gender,locale,timezone,email,link'});
  const now = new Date().toISOString().slice(0,19); // Trim off the fractional seconds from our ISO?UTC time

  Mixpanel.set({
    '$first_name': user.first_name,
    '$last_name': user.last_name,
    'FB Gender': user.gender,
    'FB Locale': user.locale,
    'FB Timezone': user.timezone,
    '$email': user.email,
    'Last Login': now,
  });
  Mixpanel.setOnce({'$created': now});

  Analytics.setUserProperties({
    'FBFirstName': user.first_name,
    'FBLastName': user.last_name,
    'FBGender': user.gender,
    'FBLocale': user.locale,
    'FBTimezone': user.timezone.toString(),
    'FBEmail': user.email,
    'LastLogin': now,
  });

}

export async function trackLogin() {
  if (!trackingEnabled) {
    return;
  }
  // We must call identify *first*, before calling setDeviceToken() or login().
  // This ensures the latter functions operate against the correct user.
  // TODO: Retrieve push token
  await setupPersonProperties();
  //Mixpanel.addPushDeviceToken(...);
}

export function trackLogout() {
  if (!trackingEnabled) {
    return;
  }
  track('Logout');
  //Mixpanel.removePushToken();
  Mixpanel.reset();
  Analytics.setUserId(null);
}

export function trackDispatches(action: Action): void {
  if (!trackingEnabled) {
    return;
  }
}
