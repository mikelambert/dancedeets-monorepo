/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Image,
  Platform,
} from 'react-native';
import { Event } from '../events/models';
import Share from 'react-native-share';

export function shareEvent(event: Event) {
  Share.open({
    share_text: event.name,
    share_URL: event.getUrl(),
    title: event.name,
  }, (e) => {
    console.warn(e);
  });
}

export const shareIcon = (Platform.OS === 'ios'
  ? <Image style={{height: 28, width: 28}} source={require('./share-icons/share-ios.png')} />
  : <Image style={{height: 28, width: 28}} source={require('./share-icons/share-android.png')} />
);
