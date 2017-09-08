/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import moment from 'moment';
import FormatText from 'react-format-text';
import querystring from 'querystring';
import { injectIntl, intlShape } from 'react-intl';
import Helmet from 'react-helmet';
import { Share as TwitterShare } from 'react-twitter-widgets';
import ExecutionEnvironment from 'exenv';
import { intlWeb } from 'dancedeets-common/js/intl';
import { formatDateTime, formatStartEnd } from 'dancedeets-common/js/dates';
import { Event } from 'dancedeets-common/js/events/models';
import type { JSONObject, Admin } from 'dancedeets-common/js/events/models';
import { formatAttending } from 'dancedeets-common/js/events/helpers';
import messages from 'dancedeets-common/js/events/messages';
import { getHostname } from 'dancedeets-common/js/util/url';
import { RsvpComponent } from './eventRsvp';
import type { RsvpValue } from './eventRsvp';
import GoogleAd from './googleAd';
import { JsonSchema } from './schema';
import { getEventSchema, getArticleSchema } from './schema/event';
import { getBreadcrumbsForEvent } from './schema/breadcrumbs';
import { Message } from './intl';
import { AmpImage, Card, ImagePrefix } from './ui';
import FormatDescription from './formatDescription';

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
    return <h2 className="event-page-header">{this.props.event.name}</h2>;
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
      <a
        id="view-flyer"
        className="link-event-flyer"
        href={fullImageUrl}
        onClick={this.onClick}
      >
        {image}
      </a>
    );

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
      <div className="event-page-image-box">
        {link}
        {adInline}
      </div>
    );
  }
}

function googleCalendarStartEndFormat(event) {
  const fmt = 'YYYYMMDDTHHmmss[Z]';
  const start = event
    .getStartMoment({ timezone: true })
    .utc()
    .format(fmt);
  const end = event
    .getEndMoment({ timezone: true, estimate: true })
    .utc()
    .format(fmt);
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
          >
            <a
              className="fb-xfbml-parse-ignore"
              rel="noopener noreferrer"
              target="_blank"
              href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(
                event.getUrl()
              )}&src=sdkpreparse`}
            >
              Share
            </a>
          </div>
        </ImagePrefix>
      );
    }

    const formattedStartEndText = formatStartEnd(
      event.getStartMoment({ timezone: false }),
      event.getEndMoment({ timezone: false }),
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
    const adInline = adsenseSafe ? (
      <GoogleAd
        style={adsenseStyle}
        data-ad-slot="6741973779"
        amp={this.props.amp}
      />
    ) : null;

    return (
      <Card newStyle>
        <div className="card-header">
          <span className="card-header-text">Details</span>
        </div>
        <div className="grey-top-border card-contents">
          <ImagePrefix
            iconName={
              event.source.name === 'Facebook Event' ? (
                'facebook-square'
              ) : (
                'external-link'
              )
            }
          >
            <Message message={messages.source} /> {sourceName}
          </ImagePrefix>
          <ImagePrefix
            icon={require('../img/categories-black.png')} // eslint-disable-line global-require
            amp={this.props.amp}
          >
            {event.annotations.categories.join(', ')}
          </ImagePrefix>
          <ImagePrefix iconName="clock-o">
            <FormatText>{formattedStartEndText.first}</FormatText>
            <br />
            <FormatText>{formattedStartEndText.second}</FormatText>
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

class MapWithLinks extends React.Component {
  props: {
    event: Event,
    amp: ?boolean,
  };

  mapUrl() {
    const geocode = this.props.event.venue.geocode;
    if (!geocode || !geocode.latitude) {
      return null;
    }
    return `http://maps.google.com/?daddr=${geocode.latitude},${geocode.longitude}`;
  }

  mapHeader() {
    const geocode = this.props.event.venue.geocode;
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
    const geocode = this.props.event.venue.geocode;
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
            source: staticMapImageUrl,
            width: size,
            height: size,
          }}
          style={{ width: '100%' }} // Only used in non-amp pages
        />
      </a>
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

type Post = Object;

class _WallPost extends React.Component {
  props: {
    post: Post,
    // Self-managed props
    intl: intlShape,
  };

  render() {
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
          <FormatDescription>{this.props.post.message}</FormatDescription>
        </div>
      </Card>
    );
  }
}
const WallPost = injectIntl(_WallPost);

class WallPosts extends React.Component {
  props: {
    posts: Array<Post>,
    admins: Array<Admin>,
  };

  render() {
    const adminIds = this.props.admins.map(x => x.id);
    const adminPosts = this.props.posts.filter(x =>
      adminIds.includes(x.from.id)
    );
    return <div>{adminPosts.map(x => <WallPost post={x} />)}</div>;
  }
}

class Description extends React.Component {
  props: {
    event: Event,
    amp?: boolean,
  };

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

    return (
      <div className="container">
        <HtmlHead event={event} />
        <JsonSchema
          json={
            this.props.amp ? getArticleSchema(event) : getEventSchema(event)
          }
        />
        <JsonSchema json={getBreadcrumbsForEvent(event)} />
        <div className="row">
          <div className="col-xs-12">{adHeader}</div>
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
            <Description event={event} amp={this.props.amp} />
            <WallPosts
              amp={this.props.amp}
              posts={this.props.event.posts}
              admins={this.props.event.admins}
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
