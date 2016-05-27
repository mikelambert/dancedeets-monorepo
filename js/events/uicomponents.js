/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Image,
  Linking,
  Platform,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';

import querystring from 'querystring';
import {
  Autolink,
  Button,
  FBShareButton,
  HorizontalView,
  ProportionalImage,
  SegmentedControl,
  Text,
} from '../ui';
import { connect } from 'react-redux';
import { Event, Venue } from './models';
import type { ThunkAction } from '../actions/types';
import MapView from 'react-native-maps';
import moment from 'moment';
import { linkColor, purpleColors } from '../Colors';
import { add as CalendarAdd } from '../api/calendar';
import RsvpOnFB from '../api/fb-event-rsvp';

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
      <HorizontalView style={eventStyles.detailLine}>
        <Image key="image" source={this.icon()} style={eventStyles.detailIcon} />
        <View style={eventStyles.detailTextContainer}>
        {this.textRender()}
        </View>
      </HorizontalView>
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
        style={eventStyles.detailText}
        >({this.props.categories.slice(0,8).join(', ')})</Text>;
    } else {
      return null;
    }
  }
}

class AddToCalendarButton extends React.Component {
  render() {
    return <Button
      icon={require('./images/add_calendar.png')}
      caption="Add to Calendar"
      type="primary"
      size="small"
      onPress={()=> CalendarAdd(this.props.event)}
    />;
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
      return <View style={{alignItems: 'flex-start'}}>
        <Text style={[eventStyles.detailText, eventStyles.rowDateTime]}>{formattedStart}</Text>
        {this.props.children}
      </View>;
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
      components.push(<Autolink
        key="line1"
        style={[eventStyles.detailText, this.props.style]}
        text={this.props.venue.name}
        />);
    }
    if (this.props.venue.address) {
      components.push(<Text
        key="line2"
        style={[eventStyles.detailText, this.props.style]}
      >{this.props.venue.cityStateCountry()}</Text>);
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
    return require('./images/website.png');
  }
  onPress() {
    Linking.openURL(this.props.source.url).catch(err => console.error('Error opening event source:', err));
  }
  textRender() {
    if (this.props.source) {
      return (
        <HorizontalView>
          <Text style={eventStyles.detailText}>Source: </Text>
          <TouchableOpacity onPress={this.onPress} activeOpacity={0.5}>
            <Text style={[eventStyles.detailText, eventStyles.rowLink]}>{this.props.source.name}</Text>
          </TouchableOpacity>
        </HorizontalView>
      );
    } else {
      return null;
    }
  }
}

class EventRsvpControl extends React.Component {
  state: {
    loading: boolean,
    defaultRsvp: number,
  };

  constructor(props: Object) {
    super(props);
    this.state = {
      loading: true,
      defaultRsvp: -1,
    };
    (this: any).onRsvpChange = this.onRsvpChange.bind(this);
  }

  componentDidMount() {
    this.loadRsvp();
  }

  async loadRsvp() {
    const rsvpIndex = await new RsvpOnFB().getRsvpIndex(this.props.event.id);
    this.setState({defaultRsvp: rsvpIndex, loading: false});
  }

  async onRsvpChange(index: number, oldIndex: number) {
    // Android's SegmentedControl doesn't upport enabled=,
    // so it's possible onRsvpChange will be called while we are loading.
    // Setting an RSVP while an RSVP is in-progress breaks the underlying FB API.
    // So let's skip sending any RSVPs while we are setting-and-reloading the value.
    // We enforce this by throwing an exception,
    // which guarantees the SegmentedControl 'undoes' the selection.
    if (this.state.loading) {
      throw 'Already loading values, do not allow any changes!';
    }
    const rsvp = RsvpOnFB.RSVPs[index].apiValue;
    // We await on this, so exceptions are propagated up (and segmentedControl can undo actions)
    this.setState({...this.state, loading: true});
    await new RsvpOnFB().send(this.props.event.id, rsvp);
    console.log('Successfully RSVPed as ' + rsvp + ' to event ' + this.props.event.id);
    // Now while the state is still 'loading', let's reload the latest RSVP from the server.
    // And when we receive it, we'll unset state.loading, re-render this component.
    await this.loadRsvp();
  }

  render() {
    return <SegmentedControl
      // When loading, we construct a "different" SegmentedControl here (forcing it via key=),
      // so that when we flip to having a defaultRsvp, we construct a *new* SegmentedControl.
      // This ensures that the SegmentedControl's constructor runs (and pulls in the new defaultRsvp).
      key={ this.state.loading ? 'loading' : 'segmentedControl' }
      enabled={ !this.state.loading } // only works on iOS
      values={RsvpOnFB.RSVPs.map((x)=>x.text)}
      defaultIndex={this.state.defaultRsvp}
      tintColor={purpleColors[0]}
      style={{marginTop: 5}}
      tryOnChange={this.onRsvpChange}
      />;
  }
}

class EventRsvp extends SubEventLine {

  icon() {
    return require('./images/attending.png');
  }

  textRender() {
    if (this.props.event.rsvp) {
      var components = [];
      if (this.props.event.rsvp.attending_count) {
        components.push(this.props.event.rsvp.attending_count + ' attending');
      }
      if (this.props.event.rsvp.maybe_count) {
        components.push(this.props.event.rsvp.maybe_count + ' maybe');
      }
      const counts = components.join(', ');
      const countsText = <Text style={eventStyles.detailText}>{counts}</Text>;
      return <View style={{width: 300}}>
        {countsText}
        <EventRsvpControl event={this.props.event} />
      </View>;
    } else {
      return null;
    }
  }
}

class EventDescription extends React.Component {
  render() {
    return <Autolink
      linkStyle={eventStyles.rowLink}
      style={eventStyles.description}
      text={this.props.description}
      hashtag="instagram"
      twitter
    />;
  }
}

class EventMap extends React.Component {
  render() {
    // TODO: Disabled while we wait for:
    // https://github.com/lelandrichardson/react-native-maps/issues/249
    if (Platform.OS === 'android') {
      return null;
    }
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

async function openVenueWithApp(venue: Venue) {
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

class _EventRow extends React.Component {
  props: {
    onEventSelected: (x: Event) => void,
    event: Event,
    listLayout: boolean,
  };

  render() {
    if (this.props.listLayout) {
      var imageProps = this.props.event.getImageProps();
      return (
        <View style={eventStyles.row}>
          <TouchableOpacity onPress={() => this.props.onEventSelected(this.props.event)} activeOpacity={0.5}>
            <Text
              numberOfLines={2}
              style={[eventStyles.rowTitle, eventStyles.rowLink]}>{this.props.event.name}</Text>
            <HorizontalView>
              <View style={{width: 100}}>
                <Image
                  source={{uri: imageProps.url}}
                  originalWidth={imageProps.width}
                  originalHeight={imageProps.height}
                  style={eventStyles.thumbnail}
                />
              </View>
              <View style={eventStyles.eventIndent}>
                <EventCategories categories={this.props.event.annotations.categories} />
                <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
                <EventVenue venue={this.props.event.venue} />
              </View>
            </HorizontalView>
          </TouchableOpacity>
        </View>
      );
    } else {
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
              style={[eventStyles.rowTitle, eventStyles.rowLink]}>{this.props.event.name}</Text>
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
}
const mapStateToProps = (state) => {
  return {
    listLayout: state.search.listLayout,
  };
};
export const EventRow = connect(mapStateToProps)(_EventRow);

class EventShare extends React.Component {
  render() {
    var shareContent = {
      contentType: 'link',
      contentUrl: this.props.event.getUrl(),
    };
    return <View style={eventStyles.shareIndent}>
      <FBShareButton shareContent={shareContent} />
    </View>;
  }
}

export class FullEventView extends React.Component {
  props: {
    onFlyerSelected: (x: Event) => ThunkAction,
    event: Event,
  };

  constructor(props: Object) {
    super(props);
    (this: any).onLocationClicked = this.onLocationClicked.bind(this);
    (this: any).onFlyerClicked = this.onFlyerClicked.bind(this);
  }

  async onLocationClicked() {
    openVenueWithApp(this.props.event.venue);
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
            <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
            <EventRsvp event={this.props.event} />
            <TouchableOpacity onPress={this.onLocationClicked} activeOpacity={0.5}>
              <EventVenue style={eventStyles.rowLink} venue={this.props.event.venue} />
            </TouchableOpacity>
            <EventSource source={this.props.event.source} />
            <HorizontalView style={{justifyContent: 'space-between'}}>
              <AddToCalendarButton event={this.props.event} />
              <EventShare event={this.props.event} />
            </HorizontalView>
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

const detailHeight = 16;

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
    fontSize: 18,
    marginBottom: 10,
  },
  rowDateTime: {
    color: '#C0FFC0',
  },
  rowLink: {
    color: linkColor,
  },
  detailTextContainer: {
    flex: 1,
  },
  detailText: {
    fontSize: detailHeight,
  },
  shareIndent: {
  },
  detailLine: {
    marginLeft: 20,
    marginBottom: 10,
  },
  detailIcon: {
    marginTop: 2,
    marginRight: 5,
    height: detailHeight,
    width: detailHeight,
  },
  eventIndent: {
    marginBottom: 20,
  },
  description: {
    lineHeight: 20,
    marginBottom: 20,
  },
  eventMap: {
    left: 0,
    height: 200,
    right: 0,
  },
});
