/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { Platform } from 'react-native';
import PushNotification from 'react-native-push-notification';
import type { TokenRegistration } from '../store/track';
import { setupToken } from '../store/track';
import { auth } from '../api/dancedeets';

async function registerToken(tokenRegistration: TokenRegistration) {
  setupToken(tokenRegistration);
  if (tokenRegistration.os === 'android') {
    auth({android_device_token: tokenRegistration.token});
  } else {
    //auth({android_device_token: tokenData.token});
  }
}

export function setup() {
  PushNotification.configure({
      // (optional) Called when Token is generated (iOS and Android)
      onRegister: registerToken,

      // (required) Called when a remote or local notification is opened or received
      onNotification: function(notification) {
          console.log( 'NOTIFICATION:', notification );
      },

      // ANDROID ONLY: GCM Sender ID (optional - not required for local notifications, but is need to receive remote push notifications)
      senderID: '911140565156',

      // IOS ONLY (optional): default: all - Permissions to register.
      permissions: {
          alert: true,
          badge: true,
          sound: true
      },

      // Should the initial notification be popped automatically
      // default: true
      popInitialNotification: false,

      /**
        * (optional) default: true
        * - Specified if permissions (ios) and token (android and ios) will requested or not,
        * - if not, you must call PushNotificationsHandler.requestPermissions() later
        */
      requestPermissions: Platform.OS === 'android',
  });
}
