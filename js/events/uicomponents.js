/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Dimensions,
  Image,
  Linking,
  ListView,
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
  Card,
  FBShareButton,
  HorizontalView,
  ProgressiveLayout,
  ProportionalImage,
  SegmentedControl,
  Text,
} from '../ui';
import { connect } from 'react-redux';
import { Event, Venue } from './models';
import type { ThunkAction } from '../actions/types';
import MapView from 'react-native-maps';
import moment from 'moment';
import { linkColor, yellowColors, purpleColors } from '../Colors';
import { add as CalendarAdd } from '../api/calendar';
import { performRequest } from '../api/fb';
import RsvpOnFB from '../api/fb-event-rsvp';
import { trackWithEvent } from '../store/track';
import LinearGradient from 'react-native-linear-gradient';

const {
  Globalize,
} = require('react-native-globalize');

const en = new Globalize('en');

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
        style={eventStyles.detailText}
        >{this.props.categories.slice(0,8).join(', ')}</Text>;
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
      size="small"
      onPress={() => {
        trackWithEvent('Add to Calendar', this.props.event);
        CalendarAdd(this.props.event);
      }}
    />;
  }
}

class EventDateTime extends SubEventLine {
  icon() {
    return require('./images/datetime.png');
  }
  textRender() {
    const dateFormatter = en.getDateFormatter({skeleton: 'yMMMdhm'});
    const start = moment(this.props.start, moment.ISO_8601);
    const formattedStart = dateFormatter(start.toDate());

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
      >{this.props.venue.cityState()}</Text>);
      components.push(<Text
        key="line3"
        style={[eventStyles.detailText, this.props.style]}
      >{this.props.venue.address.country}</Text>);
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
    trackWithEvent('Open Source', this.props.event);
    const url = this.props.event.source.url;
    try {
      Linking.openURL(url);
    } catch (err) {
      console.error('Error opening:', url, ', with Error:', err);
    }
  }
  textRender() {
    if (this.props.event.source) {
      return (
        <HorizontalView>
          <Text style={eventStyles.detailText}>Source: </Text>
          <TouchableOpacity onPress={this.onPress} activeOpacity={0.5}>
            <Text style={[eventStyles.detailText, eventStyles.rowLink]}>{this.props.event.source.name}</Text>
          </TouchableOpacity>
        </HorizontalView>
      );
    } else {
      return null;
    }
  }
}

class EventAddedBy extends SubEventLine {
  state: {
    addedBy: ?string,
  };

  constructor(props) {
    super(props);
    this.state = {
      addedBy: null,
    };
  }

  icon() {
    //TODO: Fix image
    return require('./images/user-add.png');
  }

  async loadProfileName() {
    const creation = this.props.event.annotations.creation;
    if (creation && creation.creator && creation.creator != '701004') {
      const result = await performRequest('GET', creation.creator, {fields: 'name'});
      this.setState({...this.state, addedBy: result.name});
    }
  }

  componentDidMount() {
    this.loadProfileName();
  }

  render() {
    if (this.state.addedBy) {
      return super.render();
    } else {
      return null;
    }
  }

  textRender() {
    if (this.state.addedBy) {
      //TODO: When we add Profiles, let's link to the Profile view itself: eventStyles.rowLink
      return (
        <HorizontalView>
          <Text style={eventStyles.detailText}>Added By: </Text>
          <Text style={[eventStyles.detailText]}>{this.state.addedBy}</Text>
        </HorizontalView>
      );
    } else {
      return null;
    }
  }
}


class EventOrganizers extends SubEventLine {
  state: {
    opened: boolean,
  };

  constructor(props) {
    super(props);
    this.state = {
      opened: false,
    };
  }

  icon() {
    //TODO: Fix image
    return require('./images/website.png');
  }

  async _openAdmin(adminId) {
    let url = null;
    // On Android, just send them to the URL and let the native URL intecerpetor send it to FB.
    if (Platform.OS === 'ios' && await Linking.canOpenURL('fb://')) {
      // We don't really need to pass fields=, but the FB SDK complains if we don't
      const metadata = await performRequest('GET', adminId, {metadata: '1', fields: ''});
      const idType = metadata.metadata.type;
      if (idType === 'user') {
        // This should work, but doesn't...
        // url = 'fb://profile/' + adminId;
        // So let's send them to the URL directly:
        url = 'https://www.facebook.com/' + adminId;
      } else if (idType === 'page') {
        url = 'fb://page/?id=' + adminId;
      }
      // Every event lists all members of the event who created it
      // Group events only list members (not the group, which is in a different field)
      // Page events list the members and the page id, too
    } else {
      url = 'https://www.facebook.com/' + adminId;
    }
    try {
      Linking.openURL(url);
    } catch (err) {
      console.error('Error opening FB admin page:', url, ', with Error:', err);
    }
  }

  adminLink(admin) {
    return <TouchableOpacity
      key={admin.id}
      onPress={() => {
        this._openAdmin(admin.id);
      }}
    ><Text style={[eventStyles.detailListText, eventStyles.rowLink]}>{admin.name}</Text></TouchableOpacity>;
  }

  textRender() {
    if (this.props.event.admins.length === 1) {
      return (
        <HorizontalView>
          <Text style={eventStyles.detailText}>Organizer: </Text>
          {this.adminLink(this.props.event.admins[0])}
        </HorizontalView>
      );
    } else {
      // TODO: fetch the types of each admin, and sort them with the page first (or show only the page?)
      let organizers = this.props.event.admins.map((admin) => {
        return <HorizontalView>
          <Text style={eventStyles.detailListText}> – </Text>
          {this.adminLink(admin)}
        </HorizontalView>;
      });
      return (
        <View>
          <TouchableOpacity
          onPress={()=>{this.setState({opened: !this.state.opened});}}
          >
            <Text style={[eventStyles.detailText, {marginBottom: 5}]}>
              {this.state.opened ? 'Hide Organizers' : 'Show ' + this.props.event.admins.length + ' Organizers'}
            </Text>
          </TouchableOpacity>
          {this.state.opened ? organizers : null}
        </View>
      );
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
    trackWithEvent('RSVP', this.props.event, {'RSVP Value': rsvp});
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
      enabled={ !this.state.loading }
      values={RsvpOnFB.RSVPs.map((x)=>x.text)}
      defaultIndex={this.state.defaultRsvp}
      tintColor={yellowColors[0]}
      style={{marginTop: 5, flex: 1}}
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
      //TODO: Maybe make a pop-out to show the list-of-users-attending prepended by DD users
      const counts = components.join(', ');
      const countsText = <Text style={eventStyles.detailText}>{counts}</Text>;
      return <View>
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
      // Currently only works on Android with my recent change:
      // https://github.com/mikelambert/react-native/commit/90a79cc11ee493f0dd6a8a2a5fa2a01cb2d12cad
      textProps={{selectable: true}}
      hashtag="instagram"
      twitter
    />;
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

  try {
    Linking.openURL(url);
  } catch (err) {
    console.error('Error opening map URL:', url, ', with Error:', err);
  }
}


class _EventRow extends React.Component {
  props: {
    onEventSelected: (x: Event) => void,
    event: Event,
    listLayout: boolean,
  };

  render() {
    if (this.props.listLayout) {
      const width = 100;
      const imageProps = this.props.event.getImagePropsForWidth(width);
      return (
        <Card style={eventStyles.row}>
          <TouchableOpacity onPress={() => this.props.onEventSelected(this.props.event)} activeOpacity={0.5}>
            <Text
              numberOfLines={2}
              style={[eventStyles.rowTitle, eventStyles.rowLink]}>{this.props.event.name}</Text>
            <HorizontalView>
              <View style={{width: width}}>
                <Image
                  source={{uri: imageProps.source}}
                  originalWidth={imageProps.width}
                  originalHeight={imageProps.height}
                  style={eventStyles.thumbnail}
                />
              </View>
              <View style={{flex: 1}}>
                <EventCategories categories={this.props.event.annotations.categories} />
                <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
                <EventVenue venue={this.props.event.venue} />
              </View>
            </HorizontalView>
          </TouchableOpacity>
        </Card>
      );
    } else {
      const width = Dimensions.get('window').width;
      const imageProps = this.props.event.getImagePropsForWidth(width);
      return (
        <Card style={eventStyles.row}>
          <TouchableOpacity onPress={() => this.props.onEventSelected(this.props.event)} activeOpacity={0.5}>
            <ProportionalImage
              source={{uri: imageProps.source}}
              originalWidth={imageProps.width}
              originalHeight={imageProps.height}
              style={eventStyles.thumbnail}
            />
            <Text
              numberOfLines={2}
              style={[eventStyles.rowTitle, eventStyles.rowLink]}>{this.props.event.name}</Text>
            <EventCategories categories={this.props.event.annotations.categories} />
            <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
            <EventVenue venue={this.props.event.venue} />
          </TouchableOpacity>
        </Card>
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
    trackWithEvent('View on Map', this.props.event);
    openVenueWithApp(this.props.event.venue);
  }

  onFlyerClicked() {
    this.props.onFlyerSelected(this.props.event);
  }

  render() {
    const width = Dimensions.get('window').width;
    const imageProps = this.props.event.getImagePropsForWidth(width);
    const flyerImage =
      <ProportionalImage
        source={{uri: imageProps.source}}
        originalWidth={imageProps.width}
        originalHeight={imageProps.height}
        style={eventStyles.thumbnail}
      />;

    const clickableFlyer =
      <TouchableOpacity onPress={this.onFlyerClicked} activeOpacity={0.5}>
        {flyerImage}
      </TouchableOpacity>;
    return (
      <ProgressiveLayout
        style={[eventStyles.container, {width: width}]}
      >
        {this.props.event.cover ? clickableFlyer : flyerImage}
        <Card
          style={eventStyles.eventIndent}>
          <Text
            numberOfLines={2}
            style={eventStyles.rowTitle}>{this.props.event.name}</Text>
          <EventCategories categories={this.props.event.annotations.categories} />
          <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} />
          <TouchableOpacity onPress={this.onLocationClicked} activeOpacity={0.5}>
            <EventVenue style={eventStyles.rowLink} venue={this.props.event.venue} />
          </TouchableOpacity>
          <EventRsvp event={this.props.event} />
          <EventSource event={this.props.event} />
          <EventAddedBy event={this.props.event} />
          <EventOrganizers event={this.props.event} />
          <HorizontalView style={{marginHorizontal: 5, justifyContent: 'space-between'}}>
            <AddToCalendarButton event={this.props.event} />
            <EventShare event={this.props.event} />
          </HorizontalView>
        </Card>
        <EventDescription description={this.props.event.description} />
        <TouchableOpacity onPress={this.onLocationClicked} activeOpacity={0.5}>
          <EventMap venue={this.props.event.venue} />
        </TouchableOpacity>
      </ProgressiveLayout>
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
    justifyContent: 'flex-start',
    alignItems: 'stretch',
    // http://stackoverflow.com/questions/36605906/what-is-the-row-container-for-a-listview-component
    overflow: 'hidden',
  },
  rowTitle: {
    fontSize: 18,
    lineHeight: 22,
    marginBottom: 10,
    marginLeft: 5,
    marginRight: 5,
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
  detailListText: {
    fontSize: detailHeight,
    marginBottom: 5,
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
  description: {
    lineHeight: 20,
    marginBottom: 20,
    marginLeft: 5,
    marginRight: 5,
  },
  eventMap: {
    left: 0,
    height: 200,
    right: 0,
  },
});
