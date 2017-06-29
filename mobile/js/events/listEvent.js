/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Image,
  StyleSheet,
  TouchableOpacity,
  View,
  ViewPropTypes,
} from 'react-native';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import { connect } from 'react-redux';
import LinearGradient from 'react-native-linear-gradient';
import {
  formatStartEnd,
  formatStartDateOnly,
} from 'dancedeets-common/js/dates';
import { Event, Venue } from 'dancedeets-common/js/events/models';
import { HorizontalView, normalize, semiNormalize, Text } from '../ui';

export const RowHeight = 130;

class EventVenueShort extends React.PureComponent {
  props: {
    venue: Venue,
    style?: ViewPropTypes.style,
  };

  render() {
    if (!this.props.venue.address) {
      return null;
    }
    return (
      <Text style={[eventStyles.cityText, this.props.style]}>
        {this.props.venue.cityState()}
      </Text>
    );
  }
}

class _EventRow extends React.PureComponent {
  props: {
    onEventSelected: (x: Event) => void,
    event: Event,
  };

  render() {
    const imageProps = this.props.event.getSquareFlyer();

    return (
      <View>
        <TouchableOpacity
          onPress={() => this.props.onEventSelected(this.props.event)}
          activeOpacity={0.5}
        >
          <HorizontalView>
            <Image
              source={imageProps}
              style={{ height: RowHeight, width: RowHeight }}
            />
            <View style={{ flex: 1, margin: 5 }}>
              <Text numberOfLines={2} style={eventStyles.rowTitle}>
                {this.props.event.name}
              </Text>
              <EventVenueShort venue={this.props.event.venue} />
              <Text numberOfLines={2} style={eventStyles.styleList}>
                {this.props.event.annotations.categories.slice(0, 8).join(', ')}
              </Text>
            </View>
          </HorizontalView>
        </TouchableOpacity>
      </View>
    );
  }
}
export const EventRow = connect(state => ({}))(_EventRow);

const detailHeight = 15;

const eventStyles = StyleSheet.create({
  thumbnail: {
    flexGrow: 1,
    borderRadius: 5,
  },
  rowTitle: {
    fontSize: semiNormalize(18),
    lineHeight: semiNormalize(22),
    fontWeight: 'bold',
    flexShrink: 1,
  },
  cityText: {
    fontSize: semiNormalize(detailHeight),
    lineHeight: semiNormalize(detailHeight + 2),
  },
  styleList: {
    position: 'absolute',
    bottom: 0,
    fontSize: semiNormalize(detailHeight - 3),
    lineHeight: semiNormalize(detailHeight - 3 + 2),
  },
});
