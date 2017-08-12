/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import FormatText from 'react-format-text';
import querystring from 'querystring';
import moment from 'moment';
import {
  defineMessages,
  injectIntl,
  intlShape,
  FormattedMessage,
} from 'react-intl';
import url from 'url';
import Helmet from 'react-helmet';
import { Share as TwitterShare } from 'react-twitter-widgets';
import ExecutionEnvironment from 'exenv';
import { intlWeb } from 'dancedeets-common/js/intl';
import { formatStartEnd } from 'dancedeets-common/js/dates';
import { Event } from 'dancedeets-common/js/events/models';
import type { JSONObject } from 'dancedeets-common/js/events/models';
import { formatAttending } from 'dancedeets-common/js/events/helpers';
import messages from 'dancedeets-common/js/events/messages';
import { RsvpComponent } from './eventRsvp';
import type { RsvpValue } from './eventRsvp';
import GoogleAd from './googleAd';
import { JsonSchema } from './schema';
import { getEventSchema, getArticleSchema } from './schema/event';
import { Message } from './intl';
import { AmpImage, Card, ImagePrefix } from './ui';

/* intersperse: Return an array with the separator interspersed between
 * each element of the input array.
 *
 * > _([1,2,3]).intersperse(0)
 * [1,0,2,0,3]
 */
function intersperse(arr: Array<any>, sep: string) {
  if (arr.length === 0) {
    return [];
  }

  return arr.slice(1).reduce((xs, x) => xs.concat([sep, x]), [arr[0]]);
}

function getAdsenseStyle(amp) {
  return {
    display: 'inline-block',
    width: amp ? 300 : '100%',
    height: 100,
  };
}

function isEventAdsenseSafe(event) {
  return !event.description.toLowerCase().includes('twerk');
}

class Title extends React.Component {
  props: {
    event: Event,
  };

  render() {
    const event = this.props.event;

    return (
      <h2 style={{ paddingLeft: 10, paddingRight: 10 }}>
        {this.props.event.name}
      </h2>
    );
  }
}

class ImageWithLinks extends React.Component {
  props: {
    event: Event,
    amp: ?boolean,
  };

  state: {
    lightbox: boolean,
  };

  constructor(props) {
    super(props);
    (this: any).onClick = this.onClick.bind(this);
    this.state = { lightbox: false };
  }

  onClick() {
    this.setState({ lightbox: true });
    return false;
  }

  render() {
    const picture = this.props.event.picture;
    if (!picture) {
      return null;
    }
    // TODO: Lightbox
    // const imageUrl = (this.props.amp || !ExecutionEnvironment.canUseDOM) ? picture.source : '#';
    const imageUrl = picture.source; // (this.props.amp || !ExecutionEnvironment.canUseDOM) ? picture.source : '#';

    const adsenseSafe = isEventAdsenseSafe(this.props.event);
    const adsenseStyle = getAdsenseStyle(this.props.amp);

    // Google Ad: event-inline
    const adInline = adsenseSafe
      ? <GoogleAd
          style={adsenseStyle}
          data-ad-slot="6741973779"
          amp={this.props.amp}
        />
      : null;

    const image = (
      <AmpImage
        picture={picture}
        amp={this.props.amp}
        className="event-flyer"
      />
    );

    const link = (
      <a
        id="view-flyer"
        className="link-event-flyer"
        href={imageUrl}
        onClick={this.onClick}
      >
        {image}
      </a>
    );

    const lightbox = null;
    /*
    // TODO: Lightbox
    let lightbox = null;
    if (this.state.lightbox) {
      lightbox = (<Lightbox
        mainSrc={picture.source}
        onCloseRequest={() => this.setState({ lightbox: false })}
      />);
    }
    */

    return (
      <div style={{ margin: 10 }}>
        {link}
        {adInline}
      </div>
    );
  }
}

function googleCalendarStartEndFormat(event) {
  const fmt = 'YYYYMMDDTHHmmss[Z]';
  const start = event.getStartMoment().utc().format(fmt);
  let endTime = event.getEndMoment();
  if (!endTime) {
    endTime = event.getStartMoment().add(2, 'hours');
  }
  const end = endTime.utc().format(fmt);
  return `${start}/${end}`;
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

function rsvpString(event) {
  if (!event.rsvp) {
    return null;
  }
  let rsvp = `${event.rsvp.attending_count} Attending`;
  if (event.rsvp.maybe_count) {
    rsvp += `, ${event.rsvp.maybe_count} Maybe`;
  }
  return rsvp;
}

class _EventLinks extends React.Component {
  props: {
    event: Event,
    amp: boolean,
    userId: ?number,
    userRsvp: ?RsvpValue,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    const event = this.props.event;
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
        <div>
          <ImagePrefix iconName="users">
            {formatAttending(this.props.intl, event.rsvp)}
            {rsvpAction}
          </ImagePrefix>
        </div>
      );
    }
    let organizerElement = null;
    if (event.admins.length) {
      const admins = event.admins.map(admin =>
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
      );
      organizerElement = (
        <div>
          <ImagePrefix iconName="user">
            <Message message={messages.organizer} /><br />
            <ul id="view-event-admin">
              {admins}
            </ul>
          </ImagePrefix>
        </div>
      );
    }
    let ticketElement = null;
    if (this.props.event.ticket_uri) {
      const hostname = url.parse(this.props.event.ticket_uri).hostname;
      ticketElement = (
        <div>
          <ImagePrefix iconName="ticket">
            <Message message={messages.ticketsLink} />
            {' '}
            <a
              id="view-tickets"
              href={this.props.event.ticket_uri}
              rel="noopener noreferrer"
              target="_blank"
            >
              {hostname}
            </a>
          </ImagePrefix>
        </div>
      );
    }

    let addedByElement = null;
    if (
      this.props.event.annotations.creation &&
      this.props.event.annotations.creation.creatorName
    ) {
      addedByElement = (
        <div>
          <ImagePrefix iconName="user-plus">
            <Message
              message={messages.addedBy}
              values={{
                name: this.props.event.annotations.creation.creatorName,
              }}
            />
          </ImagePrefix>
        </div>
      );
    }

    let shareLinks = null;
    if (!this.props.amp) {
      shareLinks = (
        <div>
          <ImagePrefix
            iconName="share-square-o"
            className="product-social-links"
          >
            <div style={{ display: 'inline-block' }}>
              <TwitterShare url={event.getUrl()} />
            </div>
            <div
              className="link-event-share fb-share-button"
              data-href={event.getUrl()}
              data-layout="button"
              data-size="small"
              data-mobile-iframe="true"
            >
              <a
                className="fb-xfbml-parse-ignore"
                rel="noopener noreferrer"
                target="_blank"
                href={`https://www.facebook.com/sharer/sharer.php?u=${event.getUrl()}&amp;src=sdkpreparse`}
              >
                Share
              </a>
            </div>
          </ImagePrefix>
        </div>
      );
    }

    const formattedStartEndText = formatStartEnd(
      event.getStartMoment(),
      event.getEndMoment(),
      this.props.intl
    );
    let sourceName = event.source.name;
    // Only add the a-href on the client, not the server.
    // This makes it mildly harder for scrapers to scrape us.
    // This may also help Google not discover the original FB event,
    // which may help our rankings on such events.

    // We want to run this:
    // - For non-fb events
    // - On the client
    // - For amp pages (since there is no client JS)
    if (
      sourceName !== 'Facebook Event' ||
      ExecutionEnvironment.canUseDOM ||
      this.props.amp
    ) {
      sourceName = (
        <a
          className="link-event-source"
          id="view-source"
          href={event.source.url}
          rel="noopener noreferrer"
          target="_blank"
        >
          {sourceName}
        </a>
      );
    }

    const adsenseSafe = isEventAdsenseSafe(this.props.event);
    const adsenseStyle = getAdsenseStyle(this.props.amp);
    // Google Ad: event-inline
    const adInline = adsenseSafe
      ? <GoogleAd
          style={adsenseStyle}
          data-ad-slot="6741973779"
          amp={this.props.amp}
        />
      : null;

    return (
      <Card style={{ padding: 0 }}>
        <div className="card-header">
          <span
            className="bold"
            style={{
              lineHeight: '25px',
            }}
          >
            Details
          </span>
        </div>
        <div className="grey-top-border" style={{ padding: 10 }}>
          <div>
            <ImagePrefix
              iconName={
                event.source.name === 'Facebook Event'
                  ? 'facebook-square'
                  : 'external-link'
              }
            >
              <Message message={messages.source} />{' '}
              {sourceName}
            </ImagePrefix>
          </div>
          <div>
            <ImagePrefix
              icon={require('../img/categories-white.png')} // eslint-disable-line global-require
              amp={this.props.amp}
            >
              {event.annotations.categories.join(', ')}
            </ImagePrefix>
          </div>
          <div>
            <ImagePrefix iconName="clock-o">
              <FormatText>{formattedStartEndText}</FormatText>
            </ImagePrefix>
          </div>
          <div>
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
          </div>
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

class MapWithLinks extends React.Component {
  props: {
    event: Event,
    amp: ?boolean,
  };

  map() {
    const venueName = this.props.event.venue.name;
    if (!venueName) {
      return null;
    }
    const geocode = this.props.event.venue.geocode;
    if (!geocode || !geocode.latitude) {
      return null;
    }
    const mapUrl = `http://maps.google.com/?daddr=${geocode.latitude},${geocode.longitude}`;

    const size = 450;
    const staticMapImageUrl: string =
      `//www.google.com/maps/api/staticmap?key=AIzaSyAvvrWfamjBD6LqCURkATAWEovAoBm1xNQ&size=${size}x${size}&scale=2&zoom=13&` +
      `center=${geocode.latitude},${geocode.longitude}&` +
      `markers=color:blue%7C${geocode.latitude},${geocode.longitude}`;

    const mapContents = (
      <a
        className="link-event-map"
        id="view-map"
        href={mapUrl}
        rel="noopener noreferrer"
        target="_blank"
      >
        <AmpImage
          amp={this.props.amp}
          picture={{
            source: staticMapImageUrl,
            width: size,
            height: size,
          }}
          style={{ width: '100%' }}
        />
      </a>
    );

    return (
      <div>
        <p style={{ paddingLeft: 10, paddingRight: 0 }}>
          Open in
          {' '}
          <a
            className="link-event-map"
            id="view-map-link"
            href={mapUrl}
            rel="noopener noreferrer"
            target="_blank"
          >
            Google Maps
          </a>
          .
        </p>
        {this.props.event.description
          ? <div
              className="visible-xs italics"
              style={{ paddingLeft: 10, paddingRight: 0 }}
            >
              Event description is below the map.
            </div>
          : null}
        <div>
          {mapContents}
        </div>
      </div>
    );
  }

  render() {
    const venue = this.props.event.venue;
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
        <Card style={{ padding: 0 }}>
          <ImagePrefix
            iconName="map-marker"
            style={{ padding: 10, paddingBottom: 0 }}
          >
            <div>{locationName}</div>
            <FormatText>{venue.streetCityStateCountry('\n')}</FormatText>
          </ImagePrefix>
          {this.map()}
        </Card>
      );
    }
    return null;
  }
}

class Description extends React.Component {
  props: {
    event: Event,
  };

  render() {
    return (
      <Card style={{ padding: 0 }}>
        <div className="card-header">
          <span
            className="bold"
            style={{
              lineHeight: '25px',
            }}
          >
            Description
          </span>
          <span className="google-translate" id="google_translate_element" />
        </div>
        <div className="grey-top-border" style={{ padding: 12 }}>
          <FormatText>
            {this.props.event.description}
          </FormatText>
        </div>
      </Card>
    );
  }
}

class AdminButton extends React.Component {
  props: {
    path: string,
    children?: React.Element<*>,
  };

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

class AdminPanel extends React.Component {
  props: {
    forceAdmin: boolean,
    event: Event,
    userId: ?number,
  };

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
        </AdminButton>
        {' '}
        |
        <AdminButton path={`/promoters/events/${eventId}/delete`}>
          Delete from DanceDeets
        </AdminButton>
        {' '}
        |
        <AdminButton path={`/promoters/events/${eventId}/feature`}>
          Pay to Promote
        </AdminButton>
        {' '}
        |
        <AdminButton path={`/promoters/events/${eventId}/categories`}>
          Edit Categories
        </AdminButton>
      </div>
    );
  }
}

class HtmlHead extends React.Component {
  props: {
    event: Event,
  };

  render() {
    return <Helmet title={this.props.event.name} />;
  }
}

export class EventPage extends React.Component {
  props: {
    event: JSONObject,
    forceAdmin?: boolean,
    amp?: boolean,
    userId?: number,
    userRsvp?: RsvpValue,
  };

  render() {
    const event = new Event(this.props.event);

    const adsenseSafe = isEventAdsenseSafe(event);
    const adsenseStyle = getAdsenseStyle(this.props.amp);

    // Google Ad: event-header
    const adHeader = adsenseSafe
      ? <GoogleAd
          style={{ ...adsenseStyle }}
          data-ad-slot="8283608975"
          amp={this.props.amp}
        />
      : null;
    // Google Ad: event-footer
    const adFooter = adsenseSafe
      ? <GoogleAd
          style={{ ...adsenseStyle }}
          data-ad-slot="5190541772"
          amp={this.props.amp}
        />
      : null;

    return (
      <div className="container">
        <HtmlHead event={event} />
        <JsonSchema
          json={
            this.props.amp ? getArticleSchema(event) : getEventSchema(event)
          }
        />
        <div className="row">
          <div className="col-xs-12">
            {adHeader}
          </div>
          <div className="col-xs-12">
            <Title event={event} />
            <AdminPanel
              event={event}
              userId={this.props.userId}
              forceAdmin={this.props.forceAdmin}
            />
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
            <Description event={event} />
          </div>
        </div>
        <div className="col-xs-12">
          {adFooter}
        </div>
      </div>
    );
  }
}

export const HelmetRewind = Helmet.rewind;
export default intlWeb(EventPage);
