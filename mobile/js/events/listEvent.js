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
import {
  formatStartEnd,
  formatStartDateOnly,
} from 'dancedeets-common/js/dates';
import { Event, Venue } from 'dancedeets-common/js/events/models';
import {
  BlurredImage,
  HorizontalView,
  normalize,
  semiNormalize,
  Text,
} from '../ui';

export const RowHeight = 130;

class EventVenueShort extends React.Component {
  props: {
    venue: Venue,
    style?: ViewPropTypes.style,
  };

  render() {
    if (!this.props.venue.address) {
      return null;
    }
    return (
      <Text style={[eventStyles.detailText, this.props.style]}>
        {this.props.venue.cityState()}
      </Text>
    );
  }
}

class _EventRow extends React.Component {
  props: {
    onEventSelected: (x: Event) => void,
    event: Event,
  };

  render() {
    const imageProps = this.props.event.getResponsiveFlyers();
    return (
      <View>
        <TouchableOpacity
          onPress={() => this.props.onEventSelected(this.props.event)}
          activeOpacity={0.5}
        >
          <HorizontalView>
            <BlurredImage
              source={imageProps}
              style={{ height: RowHeight, flex: 1 }}
            >
              <View style={{ flex: 1, margin: 5 }}>
                <Text
                  numberOfLines={2}
                  style={[
                    eventStyles.rowTitle,
                    { fontWeight: 'bold', flexShrink: 1 },
                  ]}
                >
                  {this.props.event.name}
                </Text>
                <EventVenueShort venue={this.props.event.venue} />
                <Text
                  style={
                    (eventStyles.detailText, {
                      position: 'absolute',
                      bottom: 0,
                    })
                  }
                >
                  {this.props.event.annotations.categories
                    .slice(0, 8)
                    .join(', ')}
                </Text>
              </View>
            </BlurredImage>
            <Image
              source={imageProps}
              style={{ height: RowHeight, width: RowHeight }}
            />
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
  },
  detailText: {
    fontSize: semiNormalize(detailHeight),
    lineHeight: semiNormalize(detailHeight + 2),
  },
});
