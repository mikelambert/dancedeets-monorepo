/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  Image,
  Linking,
  //MapView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import { ProportionalImage } from '../ui';
import { Event } from './models';
import MapView from 'react-native-maps';
import { ShareButton } from 'react-native-fbsdk';

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

class EventSource extends SubEventLine {
  constructor(props: Object) {
    super(props);
    (this: any).onPress = this.onPress.bind(this);
  }
  icon() {
    return require('./images/location.png');
  }
  onPress() {
    Linking.openURL(this.props.source.url).catch(err => console.error('Error opening event source:', err));
  }
  render() {
    return (
      <TouchableOpacity onPress={this.onPress} activeOpacity={0.5}>
        {super.render()}
      </TouchableOpacity>
    );
  }
  textRender() {
    if (this.props.source) {
      return (
        <Text style={eventStyles.rowText}>Source: {this.props.source.name}</Text>
      );
    } else {
      return null;
    }
  }
}

class EventRsvp extends SubEventLine {
  constructor(props: Object) {
    super(props);
  }
  icon() {
    return require('./images/attending.png');
  }
  textRender() {
    if (this.props.rsvp) {
      var components = [];
      if (this.props.rsvp.attending_count) {
        components.push(this.props.rsvp.attending_count + ' attending');
      }
      if (this.props.rsvp.maybe_count) {
        components.push(this.props.rsvp.maybe_count + ' maybe');
      }
      const counts = components.join(', ');
      return (
        <Text style={eventStyles.rowText}>{counts}</Text>
      );
    } else {
      return null;
    }
  }
}

class EventDescription extends React.Component {
  render() {
    return <Text style={eventStyles.description}>{this.props.description}</Text>;
  }
}

class EventMap extends React.Component {
  render() {
    return <MapView
        style={eventStyles.eventMap}
        region={{
          latitude: this.props.venue.geocode.latitude,
          longitude: this.props.venue.geocode.longitude,
          latitudeDelta: 0.02,
          longitudeDelta: 0.02,
        }}
        zoomEnabled={false}
        rotateEnabled={false}
        scrollEnabled={false}
        pitchEnabled={false}
      >
        <MapView.Marker
          coordinate={{
            latitude: this.props.venue.geocode.latitude,
            longitude: this.props.venue.geocode.longitude,
          }}
        />
      </MapView>;
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

class EventShare extends React.Component {
  render() {
    var shareContent = {
      contentType: 'link',
      contentUrl: this.props.event.getUrl(),
    };
    return <View style={eventStyles.shareIndent}>
      <ShareButton shareContent={shareContent} />
    </View>;
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
      <ScrollView style={eventStyles.container}>
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
            <EventSource source={this.props.event.source} />
            <EventCategories categories={this.props.event.annotations.categories} />
            <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
            <EventShare event={this.props.event} />
            <EventRsvp rsvp={this.props.event.rsvp} />
            <EventVenue venue={this.props.event.venue} />
          </View>
          <EventDescription description={this.props.event.description} />
          <EventMap venue={this.props.event.venue} />
        </View>
      </ScrollView>
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
  shareIndent: {
    marginLeft: 37,
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
  },
  eventIndent: {
    marginBottom: 20,
  },
  description: {
    color: 'white',
    marginBottom: 20,
  },
  eventMap: {
    left: 0,
    height: 200,
    right: 0,
  },
});
