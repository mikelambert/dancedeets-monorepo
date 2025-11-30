/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Image, Platform, TouchableOpacity } from 'react-native';
import Share from 'react-native-share';
import { Event } from 'dancedeets-common/js/events/models';
import { trackWithEvent } from '../store/track';

interface ShareEventIconProps {
  event: Event;
}

export default class ShareEventIcon extends React.Component<ShareEventIconProps> {
  render() {
    return (
      <TouchableOpacity
        onPress={() => {
          trackWithEvent('Share Event', this.props.event);
          Share.open({
            message: this.props.event.name,
            url: this.props.event.getUrl(),
            title: 'Share Event',
          }).catch(e => {
            console.warn(e);
          });
        }}
      >
        <Image
          style={{
            height: 28,
            width: 28,
            marginLeft: 10,
            marginRight: 10,
          }}
          source={
            Platform.OS === 'ios' ? (
              require('./share-icons/share-ios.png')
            ) : (
              require('./share-icons/share-android.png')
            )
          }
        />
      </TouchableOpacity>
    );
  }
}
