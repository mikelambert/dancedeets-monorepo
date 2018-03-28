/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import moment from 'moment';
import FormatText from 'react-format-text';
import querystring from 'querystring';
import { injectIntl, intlShape } from 'react-intl';
import Helmet from 'react-helmet';
import { Share as TwitterShare } from 'react-twitter-widgets';
import { intlWeb } from 'dancedeets-common/js/intl';
import {
  formatDateTime,
  formatStartEnd,
  formatStartDateOnly,
} from 'dancedeets-common/js/dates';
import { BaseEvent, Event } from 'dancedeets-common/js/events/models';
import type {
  JSONObject,
  Admin,
  Post,
} from 'dancedeets-common/js/events/models';
import {
  expandResults,
  formatAttending,
} from 'dancedeets-common/js/events/helpers';
import messages from 'dancedeets-common/js/events/messages';
import { getHostname } from 'dancedeets-common/js/util/url';
import { RsvpComponent } from './eventRsvp';
import type { RsvpValue } from './eventRsvp';
import GoogleAd from './googleAd';
import { JsonSchema } from './schema';
import { getEventSchema } from './schema/event';
import { getBreadcrumbsForEvent } from './schema/breadcrumbs';
import { Message } from './intl';
import { AmpImage, Card, ImagePrefix } from './ui';
import FormatDescription from './formatDescription';
import { canonicalizeQuery, SearchBox } from './resultsCommon';

type Query = Object;

function getAdsenseStyle(amp) {
  return {
    display: 'inline-block',
    width: amp ? 300 : '100%',
    height: 100,
  };
}

function isEventAdsenseSafe(event) {
  const description = (event.name + event.description).toLowerCase();
  const sexyContent =
    description.includes('twerk') ||
    description.includes('queer') ||
    description.match(/\bcum\b/) ||
    event.annotations.categories.includes('Vogue');
  return !sexyContent;
}

class Title extends React.Component<{
  event: Event,
}> {
  render() {
    return <h2 className="event-page-header">{this.props.event.name}</h2>;
  }
}

class ImageWithLinks extends React.Component<
  {
    event: Event,
    amp: ?boolean,
  },
  {}
> {
  render() {
    // This is for the small percentage of browsers that don't support srcSet
    // We use 480 since they're likely old browsers, don't need high resolutions, etc
    const basicCoverImage = this.props.event.getFlyer({ width: 480 });
    if (!basicCoverImage || !this.props.event.picture) {
      return null;
    }
    const fullImageUrl = this.props.event.picture.source;

    const adsenseSafe = isEventAdsenseSafe(this.props.event);
    const adsenseStyle = getAdsenseStyle(this.props.amp);

    // Google Ad: event-inline
    const adInline = adsenseSafe ? (
      <GoogleAd
        style={adsenseStyle}
        data-ad-slot="6741973779"
        amp={this.props.amp}
      />
    ) : null;

    const flyers = this.props.event.getResponsiveFlyers();
    const srcSet = flyers.map(x => `${x.uri} ${x.width}w`).join(', ');
    // These were derived from looking at how the page renders at screen sizes,
    // and the size of the images with all the margins/padding intact.
    const sizes =
      '(max-width: 768px) 100vw, (max-width: 994px) 262px, (max-width: 1200px) 354px, 437px';

    const image = (
      <AmpImage
        picture={basicCoverImage}
        amp={this.props.amp}
        className="event-flyer"
        srcSet={srcSet}
        sizes={sizes}
      />
    );

    const link = (
      <a id="view-flyer" className="link-event-flyer" href={fullImageUrl}>
        {image}
      </a>
    );

    return (
      <div className="event-page-image-box">
        {link}
        {adInline}
      </div>
    );
  }
}

function googleCalendarStartEndFormat(event) {
  // If it's an all-day event
  const startNoTz = event.getStartMoment({ timezone: false });
  const endNoTz = event.getEndMoment({ timezone: false });
  if (
    startNoTz.format('HH:mm:SS') === '00:00:00' &&
    endNoTz &&
    endNoTz.format('HH:mm:SS') === '00:00:00'
  ) {
    const fmt = 'YYYYMMDD';
    const start = startNoTz.format(fmt);
    const end = endNoTz.format(fmt);
    return `${start}/${end}`;
  } else {
    const fmt = 'YYYYMMDDTHHmmss[Z]';
    const start = event
      .getStartMoment({ timezone: true })
      .utc()
      .format(fmt);
    const end = event
      .getEndMomentWithFallback({ timezone: true })
      .utc()
      .format(fmt);
    return `${start}/${end}`;
  }
}

function getAddToCalendarLink(event) {
  const address = event.venue.fullAddress();
  const args = {
    action: 'TEMPLATE',
    text: event.name,
    dates: googleCalendarStartEndFormat(event),
    details: `Event Details:\n${event.getUrl()}`,
    location: address ? address.replace('\n', ', ') : '',
    sf: true,
    output: 'xml',
  };
  const query = querystring.stringify(args);
  return `https://www.google.com/calendar/render?${query}`;
}

class _EventLinks extends React.Component<{
  event: Event,
  amp: boolean,
  userId: ?string,
  userRsvp: ?RsvpValue,

  // Self-managed props
  intl: intlShape,
}> {
  render() {
    const { event } = this.props;
    let rsvpElement = null;
    if (event.rsvp && (event.rsvp.attending_count || event.rsvp.maybe_count)) {
      let rsvpAction = null;
      if (this.props.userId != null && !this.props.amp) {
        rsvpAction = (
          <div>
            RSVP:{' '}
            <RsvpComponent
              event={this.props.event}
              userRsvp={this.props.userRsvp}
            />
          </div>
        );
      }
      rsvpElement = (
        <ImagePrefix iconName="users">
          {formatAttending(this.props.intl, event.rsvp)}
          {rsvpAction}
        </ImagePrefix>
      );
    }
    let organizerElement = null;
    if (event.admins.length) {
      const admins = event.admins.map(admin => (
        <li key={admin.id}>
          <a
            className="link-event-admin"
            href={`https://www.facebook.com/${admin.id}`}
            rel="noopener noreferrer"
            target="_blank"
          >
            {admin.name}
          </a>
        </li>
      ));
      organizerElement = (
        <ImagePrefix iconName="user">
          <Message message={messages.organizer} />
          <br />
          <ul id="view-event-admin">{admins}</ul>
        </ImagePrefix>
      );
    }
    let ticketElement = null;
    if (this.props.event.ticket_uri) {
      const hostname = getHostname(this.props.event.ticket_uri);
      ticketElement = (
        <ImagePrefix iconName="ticket">
          <Message message={messages.ticketsLink} />{' '}
          <a
            id="view-tickets"
            href={this.props.event.ticket_uri}
            rel="noopener noreferrer"
            target="_blank"
          >
            {hostname}
          </a>
        </ImagePrefix>
      );
    }

    let addedByElement = null;
    if (
      this.props.event.annotations.creation &&
      this.props.event.annotations.creation.creatorName
    ) {
      addedByElement = (
        <ImagePrefix iconName="user-plus">
          <Message
            message={messages.addedBy}
            values={{
              name: this.props.event.annotations.creation.creatorName,
            }}
          />
        </ImagePrefix>
      );
    }

    let shareLinks = null;
    if (!this.props.amp) {
      shareLinks = (
        <ImagePrefix iconName="share-square-o" className="product-social-links">
          <div className="inline-block">
            <TwitterShare url={event.getUrl()} />
          </div>
          <div
            className="link-event-share fb-share-button"
            data-href={event.getUrl()}
            data-layout="button"
            data-size="small"
            data-mobile-iframe="true"
          />
        </ImagePrefix>
      );
    }

    const formattedStartEndText = formatStartEnd(
      event.getStartMoment({ timezone: false }),
      event.getEndMoment({ timezone: false }),
      this.props.intl
    );
    const source = (
      <ImagePrefix
        iconName={
          event.source.name === 'Facebook Event' ? (
            'facebook-square'
          ) : (
            'external-link'
          )
        }
      >
        <Message message={messages.source} />{' '}
        <a // eslint-disable-line jsx-a11y/no-static-element-interactions
          className="link-event-source"
          id="view-source"
          // This may also help Google not discover the original FB event,
          // which may help our rankings on such events.
          rel="nofollow"
          href={event.source.url}
        >
          {event.source.name}
        </a>
      </ImagePrefix>
    );

    const adsenseSafe = isEventAdsenseSafe(this.props.event);
    const adsenseStyle = getAdsenseStyle(this.props.amp);
    // Google Ad: event-inline
    const adInline = adsenseSafe ? (
      <GoogleAd
        style={adsenseStyle}
        data-ad-slot="6741973779"
        amp={this.props.amp}
      />
    ) : null;

    let second = null;
    if (formattedStartEndText.second) {
      second = [
        <br key="formatted-date-time-has-second-element" />,
        <FormatText key="format-text">
          {formattedStartEndText.second}
        </FormatText>,
      ];
    }

    return (
      <Card newStyle>
        <div className="card-header">
          <span className="card-header-text">Details</span>
        </div>
        <div className="grey-top-border card-contents">
          {source}
          <ImagePrefix
            icon={require('../img/categories-black.png')} // eslint-disable-line global-require
            amp={this.props.amp}
          >
            {event.annotations.categories.join(', ')}
          </ImagePrefix>
          <ImagePrefix iconName="clock-o">
            <FormatText>{formattedStartEndText.first}</FormatText>
            {second}
          </ImagePrefix>
          <ImagePrefix iconName="calendar-plus-o">
            <a
              id="add-to-calendar"
              href={getAddToCalendarLink(event)}
              rel="noopener noreferrer"
              target="_blank"
              className="link-event-add-to-calendar"
            >
              <Message message={messages.addToCalendar} />
            </a>
          </ImagePrefix>
          {rsvpElement}
          {ticketElement}
          {addedByElement}
          {organizerElement}
          {shareLinks}
        </div>
        {adInline}
      </Card>
    );
  }
}
const EventLinks = injectIntl(_EventLinks);

class MapWithLinks extends React.Component<{
  event: Event,
  amp: ?boolean,
}> {
  mapUrl() {
    const { geocode } = this.props.event.venue;
    if (!geocode || !geocode.latitude) {
      return null;
    }
    let host = 'maps.google.com';
    if (
      this.props.event.venue.address &&
      this.props.event.venue.address.countryCode === 'CN'
    ) {
      host = 'maps.google.cn';
    }
    return `http://${host}/?daddr=${geocode.latitude},${geocode.longitude}`;
  }

  mapHeader() {
    const { geocode } = this.props.event.venue;
    if (!geocode || !geocode.latitude) {
      return null;
    }
    const venueName = this.props.event.venue.name;
    if (!venueName) {
      return null;
    }
    return (
      <div>
        <div>
          Open in{' '}
          <a
            className="link-event-map"
            id="view-map-link"
            href={this.mapUrl()}
            rel="noopener noreferrer"
            target="_blank"
          >
            Google Maps
          </a>
          .
        </div>
        {this.props.event.description ? (
          <div className="visible-xs italics">
            Event description is below the map.
          </div>
        ) : null}
      </div>
    );
  }

  map() {
    const { geocode } = this.props.event.venue;
    if (!geocode || !geocode.latitude) {
      return null;
    }

    const size = 450;
    const staticMapImageUrl: string =
      `//www.google.com/maps/api/staticmap?key=AIzaSyAvvrWfamjBD6LqCURkATAWEovAoBm1xNQ&size=${size}x${size}&scale=2&zoom=13&` +
      `center=${geocode.latitude},${geocode.longitude}&` +
      `markers=color:blue%7C${geocode.latitude},${geocode.longitude}`;

    return (
      <a
        className="link-event-map"
        id="view-map"
        href={this.mapUrl()}
        rel="noopener noreferrer"
        target="_blank"
      >
        <AmpImage
          amp={this.props.amp}
          picture={{
            uri: staticMapImageUrl,
            width: size,
            height: size,
          }}
          style={{ width: '100%' }} // Only used in non-amp pages
        />
      </a>
    );
  }

  render() {
    const { venue } = this.props.event;
    if (venue && venue.name) {
      let locationName = <FormatText>{venue.name}</FormatText>;
      if (venue.id) {
        locationName = (
          <a id="view-venue" href={`https://www.facebook.com/${venue.id}`}>
            {locationName}
          </a>
        );
      }
      return (
        <Card newStyle>
          <div className="card-contents">
            <ImagePrefix iconName="map-marker">
              <div>{locationName}</div>
              <FormatText>{venue.streetCityStateCountry('\n')}</FormatText>
            </ImagePrefix>
            {this.mapHeader()}
          </div>
          {this.map()}
        </Card>
      );
    }
    return null;
  }
}

class _WallPost extends React.Component<{
  post: Post,
  amp: boolean,

  // Self-managed props
  intl: intlShape,
}> {
  render() {
    let { message } = this.props.post;
    if (this.props.post.link && !message.includes(this.props.post.link)) {
      message += `\n${this.props.post.link}`;
    }
    // TODO: alternately, should we just process the link using the magical tools
    // and leave the wallpost message itself alone...
    return (
      <Card newStyle>
        <div className="card-header">
          <span className="card-header-text">
            {formatDateTime(
              moment(this.props.post.created_time),
              this.props.intl
            )}
          </span>
        </div>
        <div className="grey-top-border card-contents">
          <FormatDescription amp={this.props.amp}>{message}</FormatDescription>
        </div>
      </Card>
    );
  }
}
const WallPost = injectIntl(_WallPost);

class WallPosts extends React.Component<{
  posts: Array<Post>,
  admins: Array<Admin>,
  amp?: boolean,
}> {
  render() {
    const adminIds = this.props.admins.map(x => x.id);
    const adminPosts = this.props.posts.filter(
      x => x.from && adminIds.includes(x.from.id)
    );
    return (
      <div>
        {adminPosts.map((x, i) => (
          <WallPost key={x.created_time} post={x} amp={this.props.amp} />
        ))}
      </div>
    );
  }
}

class ExtraImages extends React.Component<{
  event: Event,
  amp?: boolean,
}> {
  render() {
    if (!this.props.event.extraImageCount || !this.props.event.picture) {
      return null;
    }
    const images = [];
    let i = 0;
    while (i < this.props.event.extraImageCount) {
      let source = null;
      if (i == 0) {
        // Ensure we get the magical 'height' calculated for us
        source = this.props.event.getFlyer({ width: 480 });
      } else {
        source = this.props.event.getCroppedCover(480, null, i);
      }
      if (source) {
        images.push(
          <AmpImage
            key={i}
            picture={source}
            amp={this.props.amp}
            className="event-flyer"
          />
        );
      }
      i += 1;
    }
    return images;
  }
}

class Description extends React.Component<{
  event: Event,
  amp?: boolean,
}> {
  render() {
    return (
      <Card newStyle>
        <div className="card-header">
          <span className="card-header-text">Description</span>
          <span className="google-translate" id="google_translate_element" />
        </div>
        <div className="grey-top-border card-contents">
          <FormatDescription amp={this.props.amp}>
            {this.props.event.description}
          </FormatDescription>
          <ExtraImages event={this.props.event} amp={this.props.amp} />
        </div>
      </Card>
    );
  }
}

class AdminButton extends React.Component<{
  path: string,
  children: React.Node,
}> {
  constructor(props) {
    super(props);
    (this: any).onClick = this.onClick.bind(this);
  }

  onClick() {
    console.log(this.props.path);
  }

  render() {
    return (
      <button className="btn btn-default" onClick={this.onClick}>
        {this.props.children}
      </button>
    );
  }
}

class AdminPanel extends React.Component<{
  forceAdmin: ?boolean,
  event: Event,
  userId: ?string,
}> {
  isAdmin() {
    const adminIds = this.props.event.admins.map(x => x.id);
    return this.props.userId && adminIds.includes(this.props.userId);
  }

  render() {
    // TODO: Temporarily disable for the event pages, while we build this out...
    if (!this.props.forceAdmin) {
      return null;
    }
    if (!this.props.forceAdmin && !this.isAdmin()) {
      return null;
    }
    const eventId = this.props.event.id;
    return (
      <div>
        <AdminButton path={`/promoters/events/${eventId}/refresh`}>
          Refresh from Facebook
        </AdminButton>{' '}
        |
        <AdminButton path={`/promoters/events/${eventId}/delete`}>
          Delete from DanceDeets
        </AdminButton>{' '}
        |
        <AdminButton path={`/promoters/events/${eventId}/feature`}>
          Pay to Promote
        </AdminButton>{' '}
        |
        <AdminButton path={`/promoters/events/${eventId}/categories`}>
          Edit Categories
        </AdminButton>
      </div>
    );
  }
}

class _EventRecommendation extends React.Component<{
  event: BaseEvent,
  intl: intlShape,
}> {
  render() {
    const start = this.props.event.getStartMoment({ timezone: false });
    return (
      <a href={this.props.event.getUrl()}>
        {formatStartDateOnly(start, this.props.intl)}
        {' - '}
        {this.props.event.name}
      </a>
    );
  }
}
const EventRecommendation = injectIntl(_EventRecommendation);

class BadEventWarning extends React.Component<{
  messages: Array<string>,
  // include future events from same admins
  initialQuery: Query,
  upcomingEvents: Array<BaseEvent>,
}> {
  render() {
    let upcomingEvents = null;
    if (this.props.upcomingEvents.length) {
      upcomingEvents = (
        <div>
          Or more upcoming events from the same organizers:
          <ul>
            {this.props.upcomingEvents.map(x => (
              <li key={x.id}>
                <EventRecommendation event={x} />
              </li>
            ))}
          </ul>
        </div>
      );
    }

    let nearbyEvents = null;
    const { location } = this.props.initialQuery;
    if (location) {
      const searchUrl = getSearchUrl(this.props.initialQuery);

      nearbyEvents = (
        <a href={searchUrl}>all upcoming events near {location}</a>
      );
    }

    let recommendations = null;
    if (upcomingEvents || nearbyEvents) {
      recommendations = (
        <div className="other-upcoming-events">
          But you may be interested in {nearbyEvents}.
          {upcomingEvents}
        </div>
      );
    }

    return (
      <div>
        <div className="red-card">
          <div className="card-contents">
            {this.props.messages.map(x => <div key={x}>{x}</div>)}
          </div>
        </div>
        {recommendations}
      </div>
    );
  }
}

function getSearchUrl(query: Query) {
  const newQuery = canonicalizeQuery(query);
  const newQueryString = querystring.stringify(newQuery);
  return `/?${newQueryString}`;
}

class HtmlHead extends React.Component<{
  event: Event,
}> {
  render() {
    return <Helmet title={this.props.event.name} />;
  }
}

export class EventPage extends React.Component<{
  event: JSONObject,
  forceAdmin?: boolean,
  amp?: boolean,
  userId?: string,
  userRsvp?: RsvpValue,
  // Past event, as defined by the server code
  pastEvent: boolean,
  canceledEvent: boolean,
  // List of events, if we need to display relevant upcoming events
  upcomingEvents: Array<BaseEvent>,
}> {
  performSearch(query: Query) {
    global.window.location = getSearchUrl(query);
  }

  render() {
    const fullEvent = new Event(this.props.event);

    // This could be one of many events, so let's be sure to list them all...
    const recurringEvents = expandResults([fullEvent], Event);
    const rightRecurringEvents = recurringEvents.filter(
      x =>
        global.window && x.start_time === global.window.location.hash.slice(1)
    );
    let event = null;
    if (rightRecurringEvents.length) {
      event = rightRecurringEvents[0];
    } else {
      event = fullEvent;
    }

    const adsenseSafe = isEventAdsenseSafe(event);
    const adsenseStyle = getAdsenseStyle(this.props.amp);

    // Google Ad: event-header
    const adHeader = adsenseSafe ? (
      <GoogleAd
        style={{ ...adsenseStyle }}
        data-ad-slot="8283608975"
        amp={this.props.amp}
      />
    ) : null;
    // Google Ad: event-footer
    const adFooter = adsenseSafe ? (
      <GoogleAd
        style={{ ...adsenseStyle }}
        data-ad-slot="5190541772"
        amp={this.props.amp}
      />
    ) : null;

    const initialQuery = {
      location: event.venue.cityStateCountry(),
    };

    const searchBox = this.props.amp ? null : (
      <div style={{ marginBottom: 50 }}>
        <SearchBox query={initialQuery} onNewSearch={this.performSearch} />
      </div>
    );

    const upcomingEvents = this.props.upcomingEvents.map(x => new BaseEvent(x));

    const eventMessages = [];
    if (this.props.pastEvent) {
      eventMessages.push('Note: This event has already taken place.');
    }
    if (this.props.canceledEvent) {
      eventMessages.push('Note: This event has been canceled.');
    }
    let badPromo = null;
    if (eventMessages.length) {
      badPromo = (
        <BadEventWarning
          messages={eventMessages}
          initialQuery={initialQuery}
          upcomingEvents={upcomingEvents}
        />
      );
    }

    const jsonSchemas = recurringEvents.map(x => (
      <JsonSchema key={`${x.id}-${x.start_time}`} json={getEventSchema(x)} />
    ));

    return (
      <div className="container">
        <HtmlHead event={event} />
        {jsonSchemas}
        <JsonSchema json={getBreadcrumbsForEvent(event)} />
        {searchBox}
        <div className="row">
          <div className="col-xs-12">{adHeader}</div>
          <div className="col-xs-12">
            <Title event={event} />
            <AdminPanel
              event={event}
              userId={this.props.userId}
              forceAdmin={this.props.forceAdmin}
            />
            {badPromo}
          </div>
        </div>
        <div className="row">
          <div className="col-sm-5">
            <ImageWithLinks event={event} amp={this.props.amp} />
            <EventLinks
              event={event}
              amp={this.props.amp}
              userId={this.props.userId}
              userRsvp={this.props.userRsvp}
            />
            <MapWithLinks event={event} amp={this.props.amp} />
          </div>
          <div className="col-sm-7">
            <Description event={event} amp={this.props.amp} />
            <WallPosts
              amp={this.props.amp}
              posts={event.posts}
              admins={event.admins}
            />
          </div>
        </div>
        <div className="col-xs-12">{adFooter}</div>
      </div>
    );
  }
}

export const HelmetRewind = Helmet.rewind;
export default intlWeb(EventPage);
