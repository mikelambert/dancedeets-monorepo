/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Image,
  Platform,
  TouchableOpacity,
} from 'react-native';
import Share from 'react-native-share';
import { trackWithEvent } from '../store/track';
import { Event } from 'dancedeets-common/js/events/models';

export default class ShareEventIcon extends React.Component {
  props: {
    event: Event;
  }
  render() {
    return (<TouchableOpacity
      onPress={() => {
        trackWithEvent('Share Event', this.props.event);
        Share.open({
          message: this.props.event.name,
          url: this.props.event.getUrl(),
          title: 'Share Event',
        }, (e) => {
          console.warn(e);
        });
      }}
    >
      <Image style={{ height: 28, width: 28 }} source={Platform.OS === 'ios' ? require('./share-icons/share-ios.png') : require('./share-icons/share-android.png')} />
    </TouchableOpacity>);
  }
}
