/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  Image,
  Linking,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import querystring from 'querystring';
import { ProportionalImage } from '../ui';
import { Event } from './models';
import MapView from 'react-native-maps';
import { ShareButton } from 'react-native-fbsdk';
import moment from 'moment';

const {
  Globalize,
} = require('react-native-globalize');

var en = new Globalize('en');

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
    var dateFormatter = en.getDateFormatter({skeleton: 'yMMMdhm'});
    var start = moment(this.props.start, moment.ISO_8601);
    var formattedStart = dateFormatter(start.toDate());

    if (this.props.start) {
      return <Text style={eventStyles.rowDateTime}>{formattedStart}</Text>;
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
      components.push(<Text key="line1" style={eventStyles.rowLink}>{this.props.venue.name}</Text>);
    }
    if (this.props.venue.address) {
      components.push(<Text key="line2" style={eventStyles.rowLink}>{this.props.venue.address.city + ', ' + this.props.venue.address.country}</Text>);
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
  textRender() {
    if (this.props.source) {
      return (
        <View style={{flexDirection: 'row'}}>
          <Text style={eventStyles.rowText}>Source: </Text>
          <TouchableOpacity onPress={this.onPress} activeOpacity={0.5}>
            <Text style={eventStyles.rowLink}>{this.props.source.name}</Text>
          </TouchableOpacity>
        </View>
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
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
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

  constructor(props: Object) {
    super(props);
    (this: any).onLocationClicked = this.onLocationClicked.bind(this);
    (this: any).onFlyerClicked = this.onFlyerClicked.bind(this);
  }

  async onLocationClicked() {
/*
            if UIApplication.sharedApplication().canOpenURL(NSURL(string: "comgooglemaps://")!) {
                var encodedVenue:String
                if event.venue?.name != nil {
                    encodedVenue = event.venue!.name!.stringByAddingPercentEncodingWithAllowedCharacters(NSCharacterSet.URLQueryAllowedCharacterSet())!
                } else {
                    encodedVenue = "\(coordinate.latitude),\(coordinate.longitude)"
                }

                let url = "comgooglemaps://?q=\(encodedVenue)&center=\(coordinate.latitude),\(coordinate.longitude)&zoom=15"
                UIApplication.sharedApplication().openURL(NSURL(string:url)!)
            }

            let placemark = MKPlacemark(coordinate: coordinate, addressDictionary: event.venue?.fullAddressDictionary)
            let mapItem:MKMapItem = MKMapItem(placemark: placemark)
            mapItem.openInMapsWithLaunchOptions(nil)
            addr = [NSString stringWithFormat: @"maps://saddr=%f,%f&daddr=%f,%f", newLocation.coordinate.latitude, newLocation.coordinate.longitude, oldLatitude, oldLongitude];
            NSURL *url = [NSURL URLWithString:addr];
            [[UIApplication sharedApplication] openURL:url];
        }

    public Uri getOpenMapUrl() {
        Uri mapUrl;
        if (latLong != null) {
            mapUrl = Uri.parse("geo:0,0?q=" + latLong.getLatitude() + "," + latLong.getLongitude() + "(" + Uri.encode(getVenue().getName()) + ")");
        } else {
            mapUrl = Uri.parse("geo:0,0?q=" + Uri.encode(getVenue().getName()));
        }
        return mapUrl;
    }
}*/
    const venue = this.props.event.venue;
    const latLong = venue.geocode.latitude + ',' + venue.geocode.longitude;
    const venueName = venue.name || '(' + latLong + ')';

    var url: string = '';
    if (Platform.OS === 'ios') {
      if (await Linking.canOpenURL('comgooglemaps://')) {
        const qs = querystring.stringify({
          q: venueName,
          center: latLong,
          zoom: 15,
        });
        url = 'comgooglemaps://?' + qs;
      } else {
        const qs = querystring.stringify({
          q: venueName,
          ll: latLong,
          z: 5,
        });
        url = 'http://maps.apple.com/?' + qs;
      }
    } else if (Platform.OS === 'android') {
        // "geo:lat,lng?q=query
        // "geo:0,0?q=lat,lng(label)"
        // "geo:0,0?q=my+street+address"
        /*
         * We must support a few use cases:
         * 1) Venue Name: Each One Teach One
         * Street/City/State/Zip/Country: Lehman College 250 Bedford Prk Blvd Speech & Theatre Bldg the SET Room B20, Bronx, NY, 10468, United States
         * Lat, Long: 40.8713753364, -73.8879763323
         * 2) Venue Name: Queens Theatre in the Park
         * Street/City/State/Zip/Country: New York, NY, 11368, United States
         * Lat, Long: 40.7441611111, -73.8444222222
         * 3) Venue Name: "Hamburg"
         * Street/City/State/Zip/Country: null
         * Lat, Long: null
         * 4) More normal scenarios, like a good venue and street address
         *
         * Given this, our most reliable source is lat/long.
         * We don't want to do a search around it because of #1 and #2 will search for the wrong things.
         * So instead, the best we can do is to label the lat/long point
         */
      const q = latLong ? (latLong + '(' + venueName + ')') : venueName;
      const qs = querystring.stringify({q: q});
      url = 'geo:0,0?' + qs;
    } else {
      console.error('Unknown platform: ', Platform.OS);
    }

    Linking.openURL(url).catch(err => console.error('Error opening map URL:', url, ', with Error:', err));
  }

  onFlyerClicked() {
    this.props.onFlyerSelected(this.props.event);
  }

  render() {
    var imageProps = this.props.event.getImageProps();
    return (
      <ScrollView style={eventStyles.container}>
        <View style={eventStyles.row}>
          <TouchableOpacity onPress={this.onFlyerClicked} activeOpacity={0.5}>
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
            <EventCategories categories={this.props.event.annotations.categories} />
            <EventSource source={this.props.event.source} />
            <View style={{flex: 1, flexDirection: 'row'}}>
              <View style={{flex: 1, flexDirection: 'column'}}>
                <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
                <EventRsvp rsvp={this.props.event.rsvp} />
              </View>
              <EventShare event={this.props.event} />
            </View>
            <TouchableOpacity onPress={this.onLocationClicked} activeOpacity={0.5}>
              <EventVenue venue={this.props.event.venue} />
            </TouchableOpacity>
          </View>
          <EventDescription description={this.props.event.description} />
          <TouchableOpacity onPress={this.onLocationClicked} activeOpacity={0.5}>
            <EventMap venue={this.props.event.venue} />
          </TouchableOpacity>
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
    color: 'white',
  },
  rowDateTime: {
    color: '#C0FFC0',
  },
  rowLink: {
    color: '#70C0FF',
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
    marginTop: 2,
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
