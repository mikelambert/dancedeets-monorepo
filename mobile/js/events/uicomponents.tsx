/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import {
  ActivityIndicator,
  AlertIOS,
  Dimensions,
  Image,
  ImageBackground,
  Linking,
  Platform,
  ScrollView,
  StyleSheet,
  StyleProp,
  ViewStyle,
  TouchableOpacity,
  View,
} from 'react-native';
import { injectIntl, IntlShape, defineMessages } from 'react-intl';
import Locale from 'react-native-locale';
import { connect } from 'react-redux';
import moment from 'moment';
import geolib from 'geolib';
import querystring from 'querystring';
import { formatStartEnd } from 'dancedeets-common/js/dates';
import { Event, Venue, SearchEvent } from 'dancedeets-common/js/events/models';
import messages from 'dancedeets-common/js/events/messages';
import { getHostname } from 'dancedeets-common/js/util/url';
import { formatAttending } from 'dancedeets-common/js/events/helpers';
import {
  Autolink,
  Button,
  Card,
  FBShareButton,
  HorizontalView,
  normalize,
  ProportionalImage,
  SegmentedControl,
  semiNormalize,
  Text,
} from '../ui';
import { User, ThunkAction, Dispatch } from '../actions/types';
import { linkColor, purpleColors } from '../Colors';
import { add as CalendarAdd } from '../api/calendar';
import { performRequest } from '../api/fb';
import RsvpOnFB from '../api/fb-event-rsvp';
import { trackWithEvent } from '../store/track';
import { TranslatedEvent } from '../reducers/translate';
import { LoadedEventState } from '../reducers/loadedEvents';
import {
  loadEvent,
  toggleEventTranslation,
  canGetValidLoginFor,
} from '../actions';
import { openUserId } from '../util/fb';

interface SubEventLineProps {
  icon: any;
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
}

class SubEventLine extends React.Component<SubEventLineProps> {
  render() {
    return (
      <HorizontalView style={[eventStyles.detailLine, this.props.style]}>
        <Image
          key="image"
          source={this.props.icon}
          style={eventStyles.detailIcon}
        />
        <View style={eventStyles.detailTextContainer}>
          {this.props.children}
        </View>
      </HorizontalView>
    );
  }
}

interface EventCategoriesProps {
  categories: Array<string>;
}

class EventCategories extends React.PureComponent<EventCategoriesProps> {
  render() {
    if (this.props.categories.length > 0) {
      return (
        <SubEventLine icon={require('./images/categories.png')}>
          <Text style={eventStyles.detailText}>
            {this.props.categories.slice(0, 8).join(', ')}
          </Text>
        </SubEventLine>
      );
    } else {
      return null;
    }
  }
}

interface AddToCalendarButtonProps {
  event: Event;
  style: StyleProp<ViewStyle>;

  // Self-managed props
  intl: IntlShape;
}

class _AddToCalendarButton extends React.PureComponent<AddToCalendarButtonProps> {
  render() {
    return (
      <Button
        style={this.props.style}
        icon={require('./images/calendar.png')}
        caption={this.props.intl.formatMessage(messages.addToCalendar)}
        size="small"
        onPress={async () => {
          trackWithEvent('Add to Calendar', this.props.event);
          const added = await CalendarAdd(this.props.event);
          if (added && Platform.OS === 'ios') {
            AlertIOS.alert(
              this.props.intl.formatMessage(messages.addedToCalendar)
            );
          }
        }}
      />
    );
  }
}

const AddToCalendarButton = injectIntl(_AddToCalendarButton);

interface EventDateTimeProps {
  start: moment.Moment;
  end: moment.Moment;

  // Self-managed props
  intl: IntlShape;
  children: React.ReactNode;
}

class _EventDateTime extends React.Component<EventDateTimeProps> {
  _interval: number | undefined;

  componentDidMount() {
    // refresh our 'relative start offset' every minute
    this._interval = window.setInterval(() => this.forceUpdate(), 60 * 1000);
  }

  componentWillUnmount() {
    if (this._interval) {
      clearInterval(this._interval);
    }
  }

  render() {
    const formattedLines = formatStartEnd(
      this.props.start,
      this.props.end,
      this.props.intl
    );
    return (
      <SubEventLine icon={require('./images/datetime.png')}>
        <View
          style={{ flexGrow: 1, alignItems: 'flex-start', paddingRight: 10 }}
        >
          <Text style={eventStyles.detailText}>{formattedLines.first}</Text>
          <Text style={eventStyles.detailSubText}>{formattedLines.second}</Text>
          {this.props.children}
        </View>
      </SubEventLine>
    );
  }
}

const EventDateTime = injectIntl(_EventDateTime);

function formatDistance(intl: IntlShape, distanceKm: number) {
  const useKm = Locale.constants().usesMetricSystem;
  if (useKm) {
    const km = Math.round(distanceKm);
    return intl.formatMessage(messages.kmAway, { km });
  } else {
    const miles = Math.round(distanceKm * 0.621371);
    return intl.formatMessage(messages.milesAway, { miles });
  }
}

interface EventVenueProps {
  venue: Venue;
  style: StyleProp<ViewStyle>;

  currentPosition: any | null;

  // Self-managed props
  intl: IntlShape;
}

class _EventVenue extends React.PureComponent<EventVenueProps> {
  render() {
    const components: JSX.Element[] = [];
    if (this.props.venue.name) {
      components.push(
        <Autolink
          key="line1"
          style={[eventStyles.detailText, this.props.style]}
          text={this.props.venue.name}
        />
      );
    }
    if (this.props.venue.address) {
      components.push(
        <Text key="line2" style={[eventStyles.detailText, this.props.style]}>
          {this.props.venue.cityStateCountry()}
        </Text>
      );
    }
    let distanceComponent = null;
    if (this.props.venue.geocode && this.props.currentPosition) {
      const km =
        geolib.getDistance(
          this.props.currentPosition.coords,
          this.props.venue.geocode
        ) / 1000;
      distanceComponent = (
        <Text style={eventStyles.detailSubText}>
          {formatDistance(this.props.intl, km)}
        </Text>
      );
    }
    return (
      <SubEventLine icon={require('./images/location.png')}>
        <View>
          {components}
          {distanceComponent}
        </View>
      </SubEventLine>
    );
  }
}

const EventVenue = injectIntl(_EventVenue);

interface EventSourceProps {
  event: Event;

  // Self-managed props
  intl: IntlShape;
}

class _EventSource extends React.PureComponent<EventSourceProps> {
  constructor(props: EventSourceProps) {
    super(props);
    this.onPress = this.onPress.bind(this);
  }

  onPress() {
    trackWithEvent('Open Source', this.props.event);
    // Try opening the event in the facebook app
    if (this.props.event.source.name === 'Facebook Event') {
      if (Platform.OS === 'ios') {
        if (Linking.canOpenURL('fb://')) {
          // This URL format is supposedly current as of May 2016:
          // http://stackoverflow.com/questions/34875501/opening-facebook-event-pages-in-the-facebook-app-using-swift
          const sourceUrl = `fb://event?id=${this.props.event.id}`;
          try {
            Linking.openURL(sourceUrl);
          } catch (err) {
            console.error('Error opening:', sourceUrl, ', with Error:', err);
          }
        }
      }
    }
    // Otherwise just use the web browser
    const sourceUrl = this.props.event.source.url;
    try {
      Linking.openURL(sourceUrl);
    } catch (err) {
      console.error('Error opening:', sourceUrl, ', with Error:', err);
    }
  }

  render() {
    if (this.props.event.source) {
      return (
        <SubEventLine icon={require('./images/website.png')}>
          <HorizontalView>
            <Text style={eventStyles.detailText}>
              {this.props.intl.formatMessage(messages.source)}{' '}
            </Text>
            <TouchableOpacity onPress={this.onPress} activeOpacity={0.5}>
              <Text style={[eventStyles.detailText, eventStyles.rowLink]}>
                {this.props.event.source.name}
              </Text>
            </TouchableOpacity>
          </HorizontalView>
        </SubEventLine>
      );
    } else {
      return null;
    }
  }
}

const EventSource = injectIntl(_EventSource);

interface EventAddedByProps {
  event: Event;

  // Self-managed props
  intl: IntlShape;
}

interface EventAddedByState {
  addedBy: string | null;
}

class _EventAddedBy extends React.PureComponent<
  EventAddedByProps,
  EventAddedByState
> {
  constructor(props: EventAddedByProps) {
    super(props);
    this.state = {
      addedBy: null,
    };
  }

  componentDidMount() {
    this.loadProfileName();
  }

  async loadProfileName() {
    const creation = this.props.event.annotations.creation;
    if (creation && creation.creator && creation.creator !== '701004') {
      let name = null;
      if (creation.creatorName) {
        name = creation.creatorName;
      } else {
        const result = await performRequest('GET', creation.creator, {
          fields: 'name',
        });
        name = result.name;
      }
      this.setState({ addedBy: name });
    }
  }

  render() {
    if (this.state.addedBy) {
      // TODO: When we add Profiles, let's link to the Profile view itself: eventStyles.rowLink
      return (
        <SubEventLine icon={require('./images/user-add.png')}>
          <HorizontalView>
            <Text style={eventStyles.detailText}>
              {this.props.intl.formatMessage(messages.addedBy, {
                name: this.state.addedBy,
              })}
            </Text>
          </HorizontalView>
        </SubEventLine>
      );
    } else {
      return null;
    }
  }
}

const EventAddedBy = injectIntl(_EventAddedBy);

interface EventOrganizersProps {
  event: Event;

  // Self-managed props
  intl: IntlShape;
}

interface EventOrganizersState {
  opened: boolean;
}

class _EventOrganizers extends React.PureComponent<
  EventOrganizersProps,
  EventOrganizersState
> {
  constructor(props: EventOrganizersProps) {
    super(props);
    this.state = {
      opened: false,
    };
  }

  renderAdminLink(admin: { id: string; name: string }) {
    return (
      <TouchableOpacity key={admin.id} onPress={() => openUserId(admin.id)}>
        <Text
          style={[
            eventStyles.detailText,
            eventStyles.detailListText,
            eventStyles.rowLink,
          ]}
        >
          {admin.name}
        </Text>
      </TouchableOpacity>
    );
  }

  renderText() {
    if (this.props.event.admins.length === 1) {
      return (
        <HorizontalView>
          <Text style={eventStyles.detailText}>
            {this.props.intl.formatMessage(messages.organizer)}{' '}
          </Text>
          {this.renderAdminLink(this.props.event.admins[0])}
        </HorizontalView>
      );
    } else {
      // TODO: fetch the types of each admin, and sort them with the page first (or show only the page?)
      const organizers = this.props.event.admins.map(admin => (
        <HorizontalView key={admin.id}>
          <Text style={[eventStyles.detailText, eventStyles.detailListText]}>
            {' '}
            –{' '}
          </Text>
          {this.renderAdminLink(admin)}
        </HorizontalView>
      ));
      let text = '';
      if (this.state.opened) {
        text = this.props.intl.formatMessage(messages.hideOrganizers);
      } else {
        text = this.props.intl.formatMessage(messages.showOrganizers, {
          count: this.props.event.admins.length,
        });
      }
      return (
        <View>
          <TouchableOpacity
            onPress={() => {
              this.setState({ opened: !this.state.opened });
            }}
          >
            <Text
              style={[
                eventStyles.detailText,
                eventStyles.rowLink,
                { marginBottom: 5 },
              ]}
            >
              {text}
            </Text>
          </TouchableOpacity>
          {this.state.opened ? organizers : null}
        </View>
      );
    }
  }

  render() {
    if (this.props.event.admins.length) {
      return (
        <SubEventLine icon={require('./images/organizer.png')}>
          {this.renderText()}
        </SubEventLine>
      );
    } else {
      return null;
    }
  }
}

const EventOrganizers = injectIntl(_EventOrganizers);

interface EventRsvpControlProps {
  event: Event;
  style?: any;

  // Self-managed props
  intl: IntlShape;
  user: User | null;
  canGetValidLoginFor: (
    feature: string,
    props: { intl: IntlShape; user: User | null }
  ) => Promise<void>;
}

interface EventRsvpControlState {
  loading: boolean;
  defaultRsvp: number;
}

class _EventRsvpControl extends React.PureComponent<
  EventRsvpControlProps,
  EventRsvpControlState
> {
  constructor(props: EventRsvpControlProps) {
    super(props);
    this.state = {
      loading: false,
      defaultRsvp: -1,
    };
    this.onRsvpChange = this.onRsvpChange.bind(this);
  }

  componentDidMount() {
    if (this.props.user) {
      this.loadRsvp();
    }
  }

  async onRsvpChange(index: number, oldIndex: number): Promise<void> {
    if (!this.props.user) {
      if (
        !(await this.props.canGetValidLoginFor(
          this.props.intl.formatMessage(messages.featureRSVP),
          this.props
        ))
      ) {
        throw new Error('Not logged in, do not allow changes!');
      }
      // Have user, let's load!
    }
    // Android's SegmentedControl doesn't upport enabled=,
    // so it's possible onRsvpChange will be called while we are loading.
    // Setting an RSVP while an RSVP is in-progress breaks the underlying FB API.
    // So let's skip sending any RSVPs while we are setting-and-reloading the value.
    // We enforce this by throwing an exception,
    // which guarantees the SegmentedControl 'undoes' the selection.
    if (this.state.loading) {
      throw new Error('Already loading values, do not allow any changes!');
    }
    const rsvp = RsvpOnFB.RSVPs[index];
    trackWithEvent('RSVP', this.props.event, { 'RSVP Value': rsvp });
    // We await on this, so exceptions are propagated up (and segmentedControl can undo actions)
    this.setState({ ...this.state, loading: true });
    try {
      await RsvpOnFB.send(this.props.event.id, rsvp);
      console.log(
        `Successfully RSVPed as ${rsvp} to event ${this.props.event.id}`
      );
      // Now while the state is still 'loading', let's reload the latest RSVP from the server.
      // And when we receive it, we'll unset state.loading, re-render this component.
      await this.loadRsvp();
    } catch (e) {
      this.setState({ loading: false });
      throw new Error(
        `Error sending rsvp ${rsvp} for event ${this.props.event.id}: ${e}`
      );
    }
  }

  async loadRsvp() {
    // We don't check this.props.user here, since there may be a delay before it gets set,
    // relative to the code flow that calls this from onRsvpChange.
    this.setState({ loading: true });
    const rsvpIndex = await RsvpOnFB.getRsvpIndex(this.props.event.id);
    this.setState({ defaultRsvp: rsvpIndex, loading: false });
  }

  render() {
    return (
      <SegmentedControl
        // When loading, we construct a "different" SegmentedControl here (forcing it via key=),
        // so that when we flip to having a defaultRsvp, we construct a *new* SegmentedControl.
        // This ensures that the SegmentedControl's constructor runs (and pulls in the new defaultRsvp).
        key={this.state.loading ? 'loading' : 'segmentedControl'}
        enabled={!this.state.loading}
        values={RsvpOnFB.RSVPs.map(x =>
          this.props.intl.formatMessage(messages[x])
        )}
        defaultIndex={this.state.defaultRsvp}
        tintColor={purpleColors[0]}
        style={[{ marginTop: 5, flexGrow: 1 }, this.props.style]}
        tryOnChange={this.onRsvpChange}
      />
    );
  }
}

const EventRsvpControl = connect(
  (state: any) => ({
    isLoggedIn: state.user.isLoggedIn,
  }),
  (dispatch: any) => ({
    canGetValidLoginFor: async (feature: string, props: any) => {
      if (
        !props.isLoggedIn &&
        !(await canGetValidLoginFor(feature, props.intl, dispatch))
      ) {
        return false;
      }
      return true;
    },
  })
)(injectIntl(_EventRsvpControl));

interface EventRsvpProps {
  event: Event;

  // Self-managed props
  intl: IntlShape;
}

class _EventRsvp extends React.Component<EventRsvpProps> {
  render() {
    if (this.props.event.rsvp) {
      const counts = formatAttending(this.props.intl, this.props.event.rsvp);
      // TODO: Maybe make a pop-out to show the list-of-users-attending prepended by DD users
      const countsText = <Text style={eventStyles.detailText}>{counts}</Text>;
      const rsvpControl =
        this.props.event.source.name === 'Facebook Event' ? (
          <EventRsvpControl
            event={this.props.event}
            style={{ marginRight: 20 }}
          />
        ) : null;
      return (
        <SubEventLine icon={require('./images/attending.png')}>
          {countsText}
          {rsvpControl}
        </SubEventLine>
      );
    } else {
      return null;
    }
  }
}

const EventRsvp = injectIntl(_EventRsvp);

interface EventDescriptionProps {
  event: Event;

  // Self-managed props
  translatedEvent: TranslatedEvent | null;
}

class _EventDescription extends React.PureComponent<EventDescriptionProps> {
  render() {
    let description = this.props.event.description;
    const translatedEvent = this.props.translatedEvent;
    if (translatedEvent && translatedEvent.visible) {
      description = translatedEvent.translation.description;
    }

    return (
      <View style={{ margin: 5 }}>
        <Autolink
          linkStyle={eventStyles.rowLink}
          style={eventStyles.description}
          text={description}
          // Currently only works on Android with my recent change:
          // https://github.com/mikelambert/react-native/commit/90a79cc11ee493f0dd6a8a2a5fa2a01cb2d12cad
          selectable
          hashtag="instagram"
          twitter
        />
      </View>
    );
  }
}

const EventDescription = connect((state: any, props: any) => ({
  translatedEvent: state.translate.events[props.event.id],
}))(_EventDescription);

interface TranslateButtonProps {
  event: Event;

  // Self-managed props
  intl: IntlShape;
}

class _TranslateButton extends React.PureComponent<TranslateButtonProps> {
  render() {
    if (this.props.event.language !== this.props.intl.locale) {
      return <EventTranslate event={this.props.event} />;
    } else {
      return null;
    }
  }
}

const TranslateButton = injectIntl(_TranslateButton);

async function openVenueWithApp(venue: Venue) {
  const latLong = `${venue.geocode.latitude},${venue.geocode.longitude}`;
  const venueName = venue.name || `(${latLong})`;

  let venueUrl: string = '';
  if (Platform.OS === 'ios') {
    if (await Linking.canOpenURL('comgooglemaps://')) {
      const qs = querystring.stringify({
        q: venueName,
        center: latLong,
        zoom: 15,
      });
      venueUrl = `comgooglemaps://?${qs}`;
    } else {
      const qs = querystring.stringify({
        q: venueName,
        ll: latLong,
        z: 5,
      });
      venueUrl = `http://maps.apple.com/?${qs}`;
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
    const q = latLong ? `${latLong}(${venueName})` : venueName;
    const qs = querystring.stringify({ q });
    venueUrl = `geo:0,0?${qs}`;
  } else {
    console.error('Unknown platform: ', Platform.OS);
  }

  try {
    Linking.openURL(venueUrl);
  } catch (err) {
    console.error('Error opening map URL:', venueUrl, ', with Error:', err);
  }
}

interface EventShareProps {
  event: Event;
}

class EventShare extends React.PureComponent<EventShareProps> {
  render() {
    const shareContent = {
      contentType: 'link',
      contentUrl: this.props.event.getUrl(),
    };
    return (
      <View style={eventStyles.shareIndent}>
        <FBShareButton shareContent={shareContent} event={this.props.event} />
      </View>
    );
  }
}

interface EventTranslateProps {
  event: Event;

  // Self-managed props
  intl: IntlShape;
  translatedEvent: TranslatedEvent | null;
  toggleEventTranslation: (
    eventId: string,
    language: string,
    intl: IntlShape
  ) => void;
}

class _EventTranslate extends React.PureComponent<EventTranslateProps> {
  render() {
    const translatedText =
      this.props.translatedEvent && this.props.translatedEvent.visible
        ? this.props.intl.formatMessage(messages.untranslate)
        : this.props.intl.formatMessage(messages.translate);
    return (
      <Button
        icon={require('./images/translate.png')}
        caption={translatedText}
        size="small"
        onPress={() => {
          trackWithEvent('Translate', this.props.event);
          this.props.toggleEventTranslation(
            this.props.event.id,
            this.props.intl.locale,
            this.props.intl
          );
        }}
      />
    );
  }
}

const EventTranslate = connect(
  (state: any, props: any) => ({
    translatedEvent: state.translate.events[props.event.id],
  }),
  (dispatch: Dispatch) => ({
    toggleEventTranslation: (eventId: string, language: string, intl: IntlShape) =>
      dispatch(toggleEventTranslation(eventId, language, intl)),
  })
)(injectIntl(_EventTranslate));

interface EventTicketsProps {
  event: Event;

  // Self-managed props
  intl: IntlShape;
}

class _EventTickets extends React.PureComponent<EventTicketsProps> {
  constructor(props: EventTicketsProps) {
    super(props);
    this.onTicketClicked = this.onTicketClicked.bind(this);
  }

  onTicketClicked() {
    trackWithEvent('Tickets Link', this.props.event);
    try {
      Linking.openURL(this.props.event.ticket_uri);
    } catch (err) {
      console.error(
        'Error opening:',
        this.props.event.ticket_uri,
        ', with Error:',
        err
      );
    }
  }

  render() {
    if (this.props.event.ticket_uri) {
      const hostname = getHostname(this.props.event.ticket_uri);
      return (
        <SubEventLine icon={require('./images/ticket.png')}>
          <HorizontalView>
            <Text style={[eventStyles.detailText]}>
              {this.props.intl.formatMessage(messages.ticketsLink)}{' '}
            </Text>
            <TouchableOpacity
              onPress={this.onTicketClicked}
              activeOpacity={0.5}
            >
              <Text style={[eventStyles.detailText, eventStyles.rowLink]}>
                {hostname}
              </Text>
            </TouchableOpacity>
          </HorizontalView>
        </SubEventLine>
      );
    } else {
      return null;
    }
  }
}

const EventTickets = injectIntl(_EventTickets);

interface FullEventViewProps {
  onFlyerSelected: (x: SearchEvent) => ThunkAction;
  event: SearchEvent;
  currentPosition: any;
  translatedEvent: TranslatedEvent | null;
  loadedEvent: LoadedEventState | null;
  loadEvent: (eventId: string) => Promise<void>;
}

class _FullEventView extends React.Component<FullEventViewProps> {
  constructor(props: FullEventViewProps) {
    super(props);
    this.onLocationClicked = this.onLocationClicked.bind(this);
    this.onFlyerClicked = this.onFlyerClicked.bind(this);
  }

  componentWillMount() {
    if (!this.props.loadedEvent) {
      this.props.loadEvent(this.props.event.id);
    }
  }

  async onLocationClicked() {
    trackWithEvent('View on Map', this.props.event);
    openVenueWithApp(this.props.event.venue);
  }

  onFlyerClicked() {
    this.props.onFlyerSelected(this.props.event);
  }

  renderFullEvent(event: Event, width: number, flyer: JSX.Element | null) {
    let name = event.name;
    const translatedEvent = this.props.translatedEvent;
    if (translatedEvent && translatedEvent.visible) {
      name = translatedEvent.translation.name;
    }
    return (
      <ScrollView style={[eventStyles.container, { width }]}>
        {flyer}
        <Text
          numberOfLines={2}
          style={[eventStyles.rowTitle, eventStyles.rowTitlePadding]}
        >
          {name}
        </Text>
        <EventDateTime
          start={event.getStartMoment({ timezone: false })}
          end={event.getEndMoment({ timezone: false })}
        >
          <AddToCalendarButton
            event={event}
            style={eventStyles.addToCalendarButton}
          />
        </EventDateTime>
        <TouchableOpacity onPress={this.onLocationClicked} activeOpacity={0.5}>
          <EventVenue
            style={eventStyles.rowLink}
            venue={event.venue}
            currentPosition={this.props.currentPosition}
          />
        </TouchableOpacity>
        <EventCategories categories={event.annotations.categories} />
        <EventTickets event={event} />

        <EventRsvp event={event} />
        <EventSource event={event} />
        <EventAddedBy event={event} />
        <EventOrganizers event={event} />

        <HorizontalView style={eventStyles.splitButtons}>
          <EventShare event={event} />
          <TranslateButton event={event} />
        </HorizontalView>
        <EventDescription event={event} />
      </ScrollView>
    );
  }

  renderLoadingEvent(searchEvent: SearchEvent, width: number, flyer: JSX.Element | null) {
    const name = searchEvent.name;
    return (
      <ScrollView style={[eventStyles.container, { width }]}>
        {flyer}
        <Text
          numberOfLines={2}
          style={[eventStyles.rowTitle, eventStyles.rowTitlePadding]}
        >
          {name}
        </Text>
        <EventDateTime
          start={searchEvent.getStartMoment({ timezone: false })}
          end={searchEvent.getEndMoment({ timezone: false })}
        />
        <ActivityIndicator style={{ margin: 50 }} size="large" />
      </ScrollView>
    );
  }

  render() {
    const width = Dimensions.get('window').width;
    let flyer = null;
    const squareImageProps = this.props.event.getSquareFlyer();
    const imageProps = this.props.event.getResponsiveFlyers();
    if (imageProps.length && imageProps[0]) {
      const flyerImage = (
        <ProportionalImage
          source={imageProps}
          originalWidth={imageProps[0].width}
          originalHeight={imageProps[0].height}
          style={eventStyles.thumbnail}
          initialDimensions={{
            width,
            height: 0,
          }}
        />
      );

      flyer = (
        <TouchableOpacity onPress={this.onFlyerClicked} activeOpacity={0.5}>
          {flyerImage}
        </TouchableOpacity>
      );
    }

    let eventView = null;
    if (this.props.loadedEvent && this.props.loadedEvent.event) {
      eventView = this.renderFullEvent(
        this.props.loadedEvent.event,
        width,
        flyer
      );
    } else {
      eventView = this.renderLoadingEvent(this.props.event, width, flyer);
    }

    if (squareImageProps) {
      // Android and iOS blurRadius act differently, as noticed here:
      // https://github.com/facebook/react-native/commit/fc09c54324ff7fcec41e4f55edcca3854c9fa76b
      // TODO: At some point this will be remedied, and we'll need to adjust here.
      const blurRadius =
        3 *
        (Platform.OS === 'android'
          ? 1
          : (2 * Dimensions.get('window').width) / squareImageProps.width);
      return (
        <ImageBackground
          source={squareImageProps}
          style={eventStyles.blurredImage}
          blurRadius={blurRadius}
        >
          {eventView}
        </ImageBackground>
      );
    } else {
      return eventView;
    }
  }
}

export const FullEventView = connect(
  (state: any, props: any) => ({
    translatedEvent: state.translate.events[props.event.id],
    loadedEvent: state.loadedEvents[props.event.id],
  }),
  (dispatch: any) => ({
    loadEvent: async (eventId: string) => {
      await dispatch(loadEvent(eventId));
    },
  })
)(_FullEventView);

const detailHeight = 15;

const eventStyles = StyleSheet.create({
  thumbnail: {
    flexGrow: 1,
  },
  container: {
    backgroundColor: 'rgba(0, 0, 0, .6)',
  },
  splitButtons: {
    justifyContent: 'space-between',
    marginTop: 20,
    marginHorizontal: 10,
  },
  row: {
    justifyContent: 'flex-start',
    alignItems: 'stretch',
    // http://stackoverflow.com/questions/36605906/what-is-the-row-container-for-a-listview-component
    overflow: 'hidden',
  },
  rowTitle: {
    fontSize: semiNormalize(18),
    lineHeight: semiNormalize(22),
    fontWeight: 'bold',
    marginBottom: 20,
  },
  rowTitlePadding: {
    margin: 5,
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
    lineHeight: semiNormalize(detailHeight + 4),
  },
  detailSubText: {
    fontSize: semiNormalize(detailHeight - 2),
    lineHeight: semiNormalize(detailHeight - 2 + 4),
    color: '#bbbbbb',
  },
  shareIndent: {},
  detailLine: {
    marginLeft: 10,
    marginRight: 10,
    marginBottom: 5,
    paddingBottom: 5,
    borderBottomColor: 'rgba(255, 255, 255, 0.3)',
    borderBottomWidth: StyleSheet.hairlineWidth,
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
    flexGrow: 1,
    marginLeft: 10,
    height: normalize(150),
  },
  addToCalendarButton: {
    marginTop: 5,
  },
  blurredImage: {
    // Ignore the built-in image size props, so it can fully flex
    width: undefined,
    height: undefined,
  },
});
