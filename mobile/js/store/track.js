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

import Mixpanel from 'react-native-mixpanel';
import firebase from 'react-native-firebase';
import { AccessToken, AppEventsLogger } from 'react-native-fbsdk';
import { Crashlytics } from 'react-native-fabric';
import DeviceInfo from 'react-native-device-info';
import type { Event } from 'dancedeets-common/js/events/models';
import { performRequest } from '../api/fb';
import type { Action } from '../actions/types';

let trackingEnabled = DeviceInfo.getModel() !== 'Calypso AppCrawler';

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

  Mixpanel.sharedInstanceWithToken(mixpanelApiKey);
  if (DeviceInfo.getModel() === 'Calypso AppCrawler') {
    Mixpanel.registerSuperProperties({ $ignore: true });
  }
  // Don't use global track(), since this is a Mixpanel-only event:
  Mixpanel.track('$app_open');
}

initMixpanel();

type Params = { [key: string]: string | number };

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
  console.log('Tracking', eventName, params);
  if (params != null) {
    const firebaseSafeParams = {};
    for (const key of Object.keys(params)) {
      firebaseSafeParams[firebaseSafe(key)] = params[key];
    }
    AppEventsLogger.logEvent(eventName, 1, params);
    Mixpanel.trackWithProperties(eventName, params);
    firebase.analytics().logEvent(firebaseSafe(eventName), firebaseSafeParams);
  } else {
    AppEventsLogger.logEvent(eventName, 1);
    Mixpanel.track(eventName);
    firebase.analytics().logEvent(firebaseSafe(eventName));
  }
}

export function trackWithEvent(
  eventName: string,
  event: Event,
  params: ?Params
) {
  if (!trackingEnabled) {
    return;
  }
  const venue = event.venue || null;
  let city = venue.address ? venue.cityStateCountry() : '';
  if (!city) {
    city = '';
  }
  const extraParams: Params = Object.assign({}, params, {
    'Event ID': event.id,
    'Event City': city,
    'Event Country': venue.address ? venue.address.country : '',
  });
  track(eventName, extraParams);
}

export type TokenRegistration = {
  os: 'android' | 'os',
  token: string,
};

export function setupMixpanelToken(tokenData: TokenRegistration) {
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
  Crashlytics.setUserIdentifier(token.userID);
  Mixpanel.identify(token.userID);
  firebase.analytics().setUserId(token.userID);

  const user = await performRequest('GET', 'me', {
    fields: 'id,name,first_name,last_name,gender,locale,timezone,email,link',
  });
  const now = new Date().toISOString().slice(0, 19); // Trim off the fractional seconds from our ISO?UTC time

  Crashlytics.setUserName(user.name);
  Crashlytics.setUserEmail(user.email);
  Mixpanel.set({
    $first_name: user.first_name,
    $last_name: user.last_name,
    'FB Gender': user.gender,
    'FB Locale': user.locale,
    'FB Timezone': user.timezone,
    $email: user.email,
    'Last Login': now,
  });
  Mixpanel.setOnce({ $created: now });

  firebase.analytics().setUserProperty('FBFirstName', user.first_name);
  firebase.analytics().setUserProperty('FBLastName', user.last_name);
  firebase.analytics().setUserProperty('FBGender', user.gender);
  firebase.analytics().setUserProperty('FBLocale', user.locale);
  firebase.analytics().setUserProperty('FBTimezone', user.timezone.toString());
  firebase.analytics().setUserProperty('FBEmail', user.email);
  firebase.analytics().setUserProperty('LastLogin', now);
}

export async function trackLogin() {
  if (!trackingEnabled) {
    return;
  }
  // We must call identify *first*, before calling setDeviceToken() or login().
  // This ensures the latter functions operate against the correct user.
  // TODO: Retrieve push token
  await setupPersonProperties();
  // Mixpanel.addPushDeviceToken(...);
}

export function trackLogout() {
  if (!trackingEnabled) {
    return;
  }
  track('Logout');
  // Mixpanel.removePushToken();
  Mixpanel.reset();
  firebase.analytics().setUserId(null);
}

export function trackDispatches(action: Action): void {}

export function trackStart(eventName: string) {
  Mixpanel.timeEvent(eventName);
}

export function trackEnd(eventName: string) {
  // We don't use track.track(), because we only want to log these to MixPanel
  // (Since Google/Facebook don't support start/end in the same way)
  Mixpanel.track(eventName);
}
