/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import { ProportionalImage } from '../ui';
import { Event } from './models';

class SubEventLine extends React.Component {
  icon() {
    throw ('Not Implemented!');
  }

  textRender() {
    throw ('Not Implemented!');
  }

  render() {
    return (
      <View style={eventStyles.detailLine}>
        <Image key="image" source={this.icon()} style={eventStyles.detailIcon} />
        {this.textRender()}
      </View>
    );
  }
}

class EventCategories extends SubEventLine {
  icon() {
    return require('./images/categories.png');
  }
  textRender() {
    if (this.props.categories.length > 0) {
      return <Text
        numberOfLines={1}
        style={eventStyles.rowText}
        >({this.props.categories.slice(0,8).join(', ')})</Text>;
    } else {
      return null;
    }
  }
}

class EventDateTime extends SubEventLine {
  icon() {
    return require('./images/datetime.png');
  }
  textRender() {
    if (this.props.start) {
      return <Text style={eventStyles.rowDateTime}>{this.props.start}</Text>;
    } else {
      return null;
    }
  }
}

class EventVenue extends SubEventLine {
  icon() {
    return require('./images/location.png');
  }
  textRender() {
    var components = [];
    if (this.props.venue.name) {
      components.push(<Text key="line1" style={eventStyles.rowText}>{this.props.venue.name}</Text>);
    }
    if (this.props.venue.address) {
      components.push(<Text key="line2" style={eventStyles.rowText}>{this.props.venue.address.city + ', ' + this.props.venue.address.country}</Text>);
    }
    return <View>{components}</View>;
  }
}

export class EventRow extends React.Component {
  props: {
    onEventSelected: (x: Event) => void,
    event: Event,
  };

  render() {
    var imageProps = this.props.event.getImageProps();
    return (
      <View style={eventStyles.row}>
        <TouchableOpacity onPress={() => this.props.onEventSelected(this.props.event)} activeOpacity={0.5}>
          <ProportionalImage
            source={{uri: imageProps.url}}
            originalWidth={imageProps.width}
            originalHeight={imageProps.height}
            style={eventStyles.thumbnail}
          />
          <Text
            numberOfLines={2}
            style={eventStyles.rowTitle}>{this.props.event.name}</Text>
          <View style={eventStyles.eventIndent}>
            <EventCategories categories={this.props.event.annotations.categories} />
            <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
            <EventVenue venue={this.props.event.venue} />
          </View>
        </TouchableOpacity>
      </View>
    );
  }
}

export class FullEventView extends React.Component {
  props: {
    onFlyerSelected: (x: Event) => void,
    event: Event,
  };

  render() {
    var imageProps = this.props.event.getImageProps();
    return (
      <View style={eventStyles.container}>
        <View style={eventStyles.row}>
          <TouchableOpacity onPress={() => this.props.onFlyerSelected(this.props.event)} activeOpacity={0.5}>
            <ProportionalImage
              source={{uri: imageProps.url}}
              originalWidth={imageProps.width}
              originalHeight={imageProps.height}
              style={eventStyles.thumbnail}
            />
          </TouchableOpacity>
          <Text
            numberOfLines={2}
            style={eventStyles.rowTitle}>{this.props.event.name}</Text>
          <View style={eventStyles.eventIndent}>
            {/*<EventSource>*/}
            <EventCategories categories={this.props.event.annotations.categories} />
            <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
            {/*<EventRsvp>*/}
            <EventVenue venue={this.props.event.venue} />
            {/*<ShareView>*/}
          </View>
          {/*<EventDescription>*/}
          {/*<EventMap>*/}
        </View>
      </View>
    );
  }
}

const eventStyles = StyleSheet.create({
  thumbnail: {
    flex: 1,
  },
  container: {
    backgroundColor: '#000',
  },
  row: {
    flex: 1,
    marginLeft: 5,
    marginRight: 5,
    marginBottom: 20,
    justifyContent: 'flex-start',
    alignItems: 'stretch',
    // http://stackoverflow.com/questions/36605906/what-is-the-row-container-for-a-listview-component
    overflow: 'hidden',
  },
  rowTitle: {
    fontSize: 24,
    color: '#70C0FF',
  },
  rowDateTime: {
    color: '#C0FFC0',
  },
  rowText: {
    color: 'white',
  },
  detailLine: {
    marginLeft: 20,
    flexDirection: 'row',
  },
  detailIcon: {
    marginTop: 5,
    marginRight: 5,
    height: 12,
    width: 12,
  }
});
