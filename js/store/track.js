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

function track(eventName: string) {
  AppEventsLogger.logEvent(eventName, 1);
  Mixpanel.track(eventName);
}

function trackWithEvent(eventName: string, event: Event) {
  const extraParams = {
    'Event ID': event.id,
    'Event City': event.city,
    'Event Country': event.country,
  };
  AppEventsLogger.logEvent('View Event', extraParams);
  Mixpanel.trackWithProperties('View Event', extraParams);
}

export default function track(action: Action): void {
  switch (action.type) {
    case 'LOGGED_IN':
      track('Login');
      break;

    case 'LOGGED_OUT':
      track('Logout');
      break;

    case 'VIEW_EVENT':
      trackWithEvent('View Event', action.event);
      break;
  }
}
