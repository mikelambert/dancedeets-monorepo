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
  normalize,
  ProgressiveLayout,
  ProportionalImage,
  SegmentedControl,
  semiNormalize,
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
import { weekdayDateTime } from '../formats';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import geolib from 'geolib';

const messages = defineMessages({
  addToCalendar: {
    id: 'event.addToCalendar',
    defaultMessage: 'Add to Calendar',
    description: 'Button to add this event to the user\'s calendar',
  },
  addedBy: {
    id: 'event.addedBy',
    defaultMessage: 'Added By:',
    description: 'Describes who added this event to DanceDeets',
  },
  source: {
    id: 'event.source',
    defaultMessage: 'Source:',
    description: 'The original website from which we discovered this event',
  },
  hideOrganizers: {
    id: 'event.hideOrganizers',
    defaultMessage: 'Hide Organizers',
    description: 'Will hide the list of organizers for this event',
  },
  showOrganizers: {
    id: 'event.showOrganizers',
    defaultMessage: 'Show {count} Organizers', // Always 2-and-more, so don't need to deal with singular case
    description: 'Will show the list of organizers for this event',
  },
  organizer: {
    id: 'event.organizer',
    defaultMessage: 'Organizer:',
    description: 'Describes the one person who created this event',
  },
  attendingCount: {
    id: 'event.attendingCount',
    defaultMessage: '{attendingCount} attending',
    description: 'Count of people attending this event',
  },
  attendingMaybeCount: {
    id: 'event.attendingMaybeCount',
    defaultMessage: '{attendingCount} attending, {maybeCount} maybe',
    description: 'Count of people maybe-attending this event',
  },
  attending: {
    id: 'event.rsvp.attending',
    defaultMessage: 'I\'ll be there!',
    description: 'Clickable text for when a user wants to attend an event'
  },
  maybe: {
    id: 'event.rsvp.maybe',
    defaultMessage: 'I might flake…',
    description: 'Clickable text for when a user wants to attend an event'
  },
  declined: {
    id: 'event.rsvp.declined',
    defaultMessage: 'No thanks.',
    description: 'Clickable text for when a user wants to attend an event'
  },
  milesAway: {
    id: 'distance.miles',
    defaultMessage: '{miles} {miles, plural, one {mile} other {miles}} away',
    description: 'Distance of something from the user',
  },
  kmAway: {
    id: 'distance.km',
    defaultMessage: '{km} km away',
    description: 'Distance of something from the user',
  },
});

class SubEventLine extends React.Component {

  icon() {
    throw ('Not Implemented!');
  }

  textRender() {
    throw ('Not Implemented!');
  }

  shouldRender() {
    return true;
  }

  render() {
    if (this.shouldRender()) {
      return (
        <HorizontalView style={eventStyles.detailLine}>
          <Image key="image" source={this.icon()} style={eventStyles.detailIcon} />
          <View style={eventStyles.detailTextContainer}>
          {this.textRender()}
          </View>
        </HorizontalView>
      );
    } else {
      return null;
    }
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

class _AddToCalendarButton extends React.Component {
  render() {
    return <Button
      icon={require('./images/calendar.png')}
      caption={this.props.intl.formatMessage(messages.addToCalendar)}
      size="small"
      onPress={() => {
        trackWithEvent('Add to Calendar', this.props.event);
        CalendarAdd(this.props.event);
      }}
    />;
  }
}
const AddToCalendarButton = injectIntl(_AddToCalendarButton);

class _EventDateTime extends SubEventLine {
  icon() {
    return require('./images/datetime.png');
  }
  textRender() {
    const textFields = [];
    const now = moment();
    const start = moment(this.props.start, moment.ISO_8601);
    const formattedStart = this.props.intl.formatDate(start.toDate(), weekdayDateTime);
    if (this.props.end) {
      const end = moment(this.props.end, moment.ISO_8601);
      const duration = end.diff(start);
      if (duration > moment.duration(1, 'days')) {
        const formattedEnd = this.props.intl.formatDate(end, weekdayDateTime);
        textFields.push(formattedStart + ' - \n' + formattedEnd);
      } else {
        const formattedEndTime = this.props.intl.formatTime(end);
        textFields.push(formattedStart + ' - ' + formattedEndTime);
      }
      const relativeDuration = moment.duration(duration).humanize();
      textFields.push(` (${relativeDuration})`);
    } else {
      const formattedDate = this.props.intl.formatDate(start.toDate(), weekdayDateTime);
      textFields.push(formattedStart);
    }
    // Ensure we do some sort of timer refresh update on this
    const relativeStart = start.diff(now);
    if (relativeStart < moment.duration(2, 'weeks')) {
      const relativeStartOffset = moment.duration(relativeStart).humanize(true);
      textFields.push('\n');
      textFields.push(relativeStartOffset);
    }
    return <View style={{alignItems: 'flex-start'}}>
      <Text style={[eventStyles.detailText, eventStyles.rowDateTime]}>{textFields.join('')}</Text>
      {this.props.children}
    </View>;
  }
  componentDidMount() {
    // refresh our 'relative start offset' every minute
    this.interval = setInterval(() => this.forceUpdate(), 60*1000);
  }
  componentWillUnmount() {
    clearInterval(this.interval);
  }
}
const EventDateTime = injectIntl(_EventDateTime);

function formatDistance(intl, distanceKm) {
  const useKm = (intl.locale !== 'en');
  if (useKm) {
    const km = Math.round(distanceKm);
    return intl.formatMessage(messages.kmAway, {km});
  } else {
    const miles = distanceKm * 0.621371;
    return intl.formatMessage(messages.milesAway, {miles});
  }
}

class _EventVenue extends SubEventLine {
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
    let distanceComponent = null;
    if (this.props.venue.geocode && this.props.currentPosition) {
      const km = geolib.getDistance(this.props.currentPosition.coords, this.props.venue.geocode) / 1000;
      distanceComponent = <Text>{formatDistance(this.props.intl, km)}</Text>;
    }
    return <View>{distanceComponent}{components}</View>;
  }
}
const EventVenue = injectIntl(_EventVenue);

class _EventSource extends SubEventLine {
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
          <Text style={eventStyles.detailText}>{this.props.intl.formatMessage(messages.source)}{' '}</Text>
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
const EventSource = injectIntl(_EventSource);

class _EventAddedBy extends SubEventLine {
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

  shouldRender() {
    return this.state.addedBy;
  }

  textRender() {
    if (this.state.addedBy) {
      //TODO: When we add Profiles, let's link to the Profile view itself: eventStyles.rowLink
      return (
        <HorizontalView>
          <Text style={eventStyles.detailText}>{this.props.intl.formatMessage(messages.addedBy, {name: this.state.addedBy})}</Text>
        </HorizontalView>
      );
    } else {
      return null;
    }
  }
}
const EventAddedBy = injectIntl(_EventAddedBy);

class _EventOrganizers extends SubEventLine {
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
    return require('./images/organizer.png');
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
    ><Text style={[eventStyles.detailText, eventStyles.detailListText, eventStyles.rowLink]}>{admin.name}</Text></TouchableOpacity>;
  }

  shouldRender() {
    return this.props.event.admins.length;
  }

  textRender() {
    if (this.props.event.admins.length === 1) {
      return (
        <HorizontalView>
          <Text style={eventStyles.detailText}>{this.props.intl.formatMessage(messages.organizer)}{' '}</Text>
          {this.adminLink(this.props.event.admins[0])}
        </HorizontalView>
      );
    } else {
      // TODO: fetch the types of each admin, and sort them with the page first (or show only the page?)
      let organizers = this.props.event.admins.map((admin) => {
        return <HorizontalView>
          <Text style={[eventStyles.detailText, eventStyles.detailListText]}> – </Text>
          {this.adminLink(admin)}
        </HorizontalView>;
      });
      let text = '';
      if (this.state.opened) {
        text = this.props.intl.formatMessage(messages.hideOrganizers);
      } else {
        text = this.props.intl.formatMessage(messages.showOrganizers, {count: this.props.event.admins.length});
      }
      return (
        <View>
          <TouchableOpacity
          onPress={()=>{this.setState({opened: !this.state.opened});}}
          >
            <Text style={[eventStyles.detailText, eventStyles.rowLink, {marginBottom: 5}]}>
              {text}
            </Text>
          </TouchableOpacity>
          {this.state.opened ? organizers : null}
        </View>
      );
    }
  }
}
const EventOrganizers = injectIntl(_EventOrganizers);


class _EventRsvpControl extends React.Component {
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
    const rsvp = RsvpOnFB.RSVPs[index];
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
      values={RsvpOnFB.RSVPs.map((x)=>this.props.intl.formatMessage(messages[x]))}
      defaultIndex={this.state.defaultRsvp}
      tintColor={yellowColors[0]}
      style={{marginTop: 5, flex: 1}}
      tryOnChange={this.onRsvpChange}
      />;
  }
}
const EventRsvpControl = injectIntl(_EventRsvpControl);

class _EventRsvp extends SubEventLine {

  icon() {
    return require('./images/attending.png');
  }

  shouldRender() {
    return this.props.event.rsvp;
  }

  textRender() {
    if (this.props.event.rsvp) {
      let counts = '';
      if (this.props.event.rsvp.attending_count) {
        if (this.props.event.rsvp.maybe_count) {
          counts = this.props.intl.formatMessage(messages.attendingMaybeCount, {
            attendingCount: this.props.event.rsvp.maybe_count,
            maybeCount: this.props.event.rsvp.maybe_count,
          });
        } else {
          counts = this.props.intl.formatMessage(messages.attendingCount, {attendingCount: this.props.event.rsvp.maybe_count});
        }
      }
      //TODO: Maybe make a pop-out to show the list-of-users-attending prepended by DD users
      const countsText = <Text style={eventStyles.detailText}>{counts}</Text>;
      const rsvpControl = (this.props.event.source.name === 'Facebook Event') ? <EventRsvpControl event={this.props.event} /> : null;
      return <View>
        {countsText}
        {rsvpControl}
      </View>;
    } else {
      return null;
    }
  }
}
const EventRsvp = injectIntl(_EventRsvp);

class EventDescription extends React.Component {
  render() {
    return <Card><Autolink
      linkStyle={eventStyles.rowLink}
      style={eventStyles.description}
      text={this.props.description}
      // Currently only works on Android with my recent change:
      // https://github.com/mikelambert/react-native/commit/90a79cc11ee493f0dd6a8a2a5fa2a01cb2d12cad
      textProps={{selectable: true}}
      hashtag="instagram"
      twitter
    /></Card>;
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
    currentPosition: any,
  };

  render() {
    if (!this.props.event.venue.geocode) {
      console.log(this.props.event);
    }
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
                <EventVenue venue={this.props.event.venue} currentPosition={this.props.currentPosition} />
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
            <EventVenue venue={this.props.event.venue} currentPosition={this.props.currentPosition} />
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
    currentPosition: any,
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

    const map = this.props.event.venue.geocode
      ? <TouchableOpacity onPress={this.onLocationClicked} activeOpacity={0.5}>
          <EventMap venue={this.props.event.venue} />
        </TouchableOpacity>
      : null;

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
          <EventDateTime start={this.props.event.start_time} end={this.props.event.end_time} >
            <AddToCalendarButton event={this.props.event} />
          </EventDateTime>
          <TouchableOpacity onPress={this.onLocationClicked} activeOpacity={0.5}>
            <EventVenue style={eventStyles.rowLink} venue={this.props.event.venue} currentPosition={this.props.currentPosition} />
          </TouchableOpacity>
          <EventRsvp event={this.props.event} />
          <EventSource event={this.props.event} />
          <EventAddedBy event={this.props.event} />
          <EventOrganizers event={this.props.event} />
          <EventShare event={this.props.event} />
        </Card>
        <EventDescription description={this.props.event.description} />
        {map}
      </ProgressiveLayout>
    );
  }
}

const detailHeight = 15;

const eventStyles = StyleSheet.create({
  thumbnail: {
    flex: 1,
    borderRadius: 5,
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
    fontSize: semiNormalize(18),
    lineHeight: semiNormalize(22),
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
    marginBottom: 5,
  },
  detailText: {
    fontSize: semiNormalize(detailHeight),
    lineHeight: semiNormalize(detailHeight+2),
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
    height: semiNormalize(detailHeight),
    width: semiNormalize(detailHeight),
  },
  description: {
    fontSize: semiNormalize(detailHeight),
    lineHeight: semiNormalize(20),
    marginBottom: 20,
    marginLeft: 5,
    marginRight: 5,
  },
  eventMap: {
    left: 0,
    height: normalize(200),
    right: 0,
  },
});
