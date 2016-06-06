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
  TouchableOpacity,
} from 'react-native';
import { trackWithEvent } from '../store/track';
import Share from 'react-native-share';

export default class ShareEventIcon extends React.Component {
  render() {
    return <TouchableOpacity onPress={() => {
      trackWithEvent('Share Event', this.props.event);
      Share.open({
        share_text: this.props.event.name,
        share_URL: this.props.event.getUrl(),
        title: 'Share Event',
      }, (e) => {
        console.warn(e);
      });
    }}>
      <Image style={{height: 28, width: 28}} source={Platform.OS === 'ios' ? require('./share-icons/share-ios.png') : require('./share-icons/share-android.png')} />
    </TouchableOpacity>;
  }
}
