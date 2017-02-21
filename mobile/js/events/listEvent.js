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
} from 'react-native';
import {
  injectIntl,
  intlShape,
  defineMessages,
} from 'react-intl';
import { connect } from 'react-redux';
import {
  formatStartEnd,
  formatStartDateOnly,
} from 'dancedeets-common/js/dates';
import {
  Event,
  Venue,
} from 'dancedeets-common/js/events/models';
import {
  BlurredImage,
  HorizontalView,
  normalize,
  semiNormalize,
  Text,
} from '../ui';

class _EventVenueShort extends React.Component {
  props: {
    venue: Venue;
    style: View.propTypes.style;

    currentPosition: ?Object;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    if (!this.props.venue.address) {
      return null;
    }
    return (<Text
        style={[eventStyles.detailText, this.props.style]}
      >{this.props.venue.cityState()}</Text>);
  }
}
const EventVenueShort = injectIntl(_EventVenueShort);

class _EventRow extends React.Component {
  props: {
    onEventSelected: (x: Event) => void,
    event: Event,
    listLayout: boolean,
    currentPosition: ?Object,
  };

  render() {
    const imageProps = this.props.event.getResponsiveFlyers();
    return (
      <View>
        <TouchableOpacity onPress={() => this.props.onEventSelected(this.props.event)} activeOpacity={0.5}>
          <HorizontalView>
            <BlurredImage source={imageProps}
              style={{height: 130, flex: 1}}
            >
              <View style={{flex: 1, margin: 5}}>
                <Text
                  numberOfLines={2}
                  style={[eventStyles.rowTitle, {fontWeight: 'bold', flexShrink: 1}]}
                >{this.props.event.name}</Text>
                <EventVenueShort venue={this.props.event.venue} currentPosition={this.props.currentPosition} />
                <Text
                  style={eventStyles.detailText, {position: 'absolute', bottom: 0}}
                >{this.props.event.annotations.categories.slice(0, 8).join(', ')}</Text>
              </View>
            </BlurredImage>
            <Image
              source={imageProps}
              style={{height: 130, width: 130}}
            />
          </HorizontalView>
        </TouchableOpacity>
      </View>
    );
  }
}
export const EventRow = connect(
  state => ({
    listLayout: state.search.listLayout,
  }),
)(_EventRow);

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
