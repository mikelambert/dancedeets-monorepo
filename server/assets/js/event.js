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
import {
  GoogleMapLoader,
  GoogleMap,
  Marker,
} from 'react-google-maps';
import {
  intl,
  Internationalize,
} from 'dancedeets-common/js/intl';
import {
  formatStartEnd,
} from 'dancedeets-common/js/dates';
import {
  Event,
} from 'dancedeets-common/js/events/models';
import type {
  Cover,
  JSONObject,
} from 'dancedeets-common/js/events/models';
import {
  formatAttending,
} from 'dancedeets-common/js/events/helpers';
import {
  messages,
} from 'dancedeets-common/js/events/messages';
import { RsvpComponent } from './event_common';
import type { RsvpValue } from './event_common';

type RequiredImage = {
  source: number; // aka required package
  width: number;
  height: number;
};
type ClientCover = Cover | RequiredImage;

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

class Card extends React.Component {
  props: {
    children?: Array<React.Element<*>>;
  }

  render() {
    return (<div className="card">
      {this.props.children}
    </div>);
  }
}

class Title extends React.Component {
  props: {
    event: Event;
  }

  render() {
    const event = this.props.event;

    let categoryLinks = null;
    if (event.annotations.categories) {
      const categories = event.annotations.categories.map(x => <a href={`/?keywords=${x}`}>{x}</a>);
      categoryLinks = <li key="category">categorized as: {intersperse(categories, ', ')}.</li>;
    }
    let locationLinks = null;
    const cityStateCountry = event.venue.cityStateCountry();
    if (cityStateCountry) {
      locationLinks = <li key="location">in <a href={`/?location=${cityStateCountry}`}>{cityStateCountry}</a>.</li>;
    }
    let moreLinks = null;
    if (categoryLinks || locationLinks) {
      moreLinks = (<div>
        See more events:
        <ul>
          {locationLinks}
          {categoryLinks}
        </ul>
      </div>);
    }

    return (<Card>
      {moreLinks}
      <h2>{this.props.event.name}</h2>
    </Card>);
  }
}

class ImagePrefix extends React.Component {
  props: {
    icon?: number; // aka required package
    iconName?: string;
    className?: string;
    amp?: boolean;
    children?: Array<React.Element<*>>;
  }

  render() {
    if (!this.props.icon && !this.props.iconName) {
      console.error('Missing icon and iconName');
      return null;
    }
    const { icon, iconName, className, amp, children, ...otherProps } = this.props;
    let iconHtml = null;
    if (icon) {
      const picture: RequiredImage = {
        source: icon,
        width: 18,
        height: 18,
      };
      iconHtml = (<span className="fa fa-lg image-prefix-icon image-prefix-dancer">
        <AmpImage
          picture={picture}
          width="18"
          amp={this.props.amp}
        />
      </span>);
    } else if (this.props.iconName) {
      iconHtml = <i className={`fa fa-${this.props.iconName} fa-lg image-prefix-icon`} />;
    }
    return (<div className={`image-prefix ${className || ''}`} {...otherProps}>
      {iconHtml}
      <div className="image-prefix-contents">
        {children}
      </div>
    </div>);
  }
}

class AmpImage extends React.Component {
  props: {
    picture: ClientCover;
    amp?: boolean;
    width?: string;
  }

  render() {
    const { picture, amp, width, ...otherProps } = this.props;
    if (this.props.amp) {
      return (
        <amp-img
          src={picture.source}
          layout="responsive"
          width={picture.width}
          height={picture.height}
        />
      );
    } else {
      return (
        <img
          role="presentation"
          src={picture.source}
          width={width}
          {...otherProps}
        />
      );
    }
  }
}

class ImageWithLinks extends React.Component {
  props: {
    event: Event;
    amp: boolean;
  }

  render() {
    const picture = this.props.event.picture;
    if (!picture) {
      return null;
    }
    const eventUrl = picture.source;

    return (
      <Card>
        <a className="link-event-flyer" href={eventUrl}>
          <AmpImage
            picture={picture}
            amp={this.props.amp}
            className="event-flyer"
          />
        </a>
        <br />
        <ImagePrefix iconName="picture-o">
          <a className="link-event-flyer" href={eventUrl}>See Full Flyer</a>
        </ImagePrefix>
      </Card>
    );
  }
}

function googleCalendarStartEndFormat(event) {
  const fmt = 'YYYYMMDDTHHmmss[Z]';
  const start = moment(event.start_time).utc().format(fmt);
  const endTime = event.end_time ? moment(event.end_time) : moment(event.start_time).add(2, 'hours');
  const end = endTime.utc().format(fmt);
  return `${start}/${end}`;
}

function getAddToCalendarLink(event) {
  const args = {
    action: 'TEMPLATE',
    text: event.name,
    dates: googleCalendarStartEndFormat(event),
    details: `Event Details:\n${event.getUrl()}`,
    location: event.venue.fullAddress().replace('\n', ', '),
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

function schemaDateFormat(dateTime) {
  return moment(dateTime).format('%Y-%m-%dT%H:%M:%S');
}

class _EventLinks extends React.Component {
  props: {
    event: Event;
    amp: boolean;
    loggedIn: boolean;
    userRsvp: RsvpValue;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const event = this.props.event;
    let rsvpElement = null;
    if (event.rsvp && (event.rsvp.attending_count || event.rsvp.maybe_count)) {
      let rsvpAction = null;
      if (this.props.loggedIn && !this.props.amp) {
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
        <li><a
          key={admin.id}
          className="link-event-admin"
          href={`https://www.facebook.com/${admin.id}`}
        >{admin.name}</a></li>));
      organizerElement = (
        <ImagePrefix iconName="user">
          <FormattedMessage id={messages.organizer.id} /><br />
          <ul>
            {admins}
          </ul>
        </ImagePrefix>
      );
    }
    let ticketElement = null;
    if (this.props.event.ticket_uri) {
      const hostname = url.parse(this.props.event.ticket_uri).hostname;
      ticketElement = (
        <ImagePrefix iconName="ticket">
          <FormattedMessage id={messages.ticketsLink.id} /> <a href={this.props.event.ticket_uri}>{hostname}</a>
        </ImagePrefix>
      );
    }

    let addedByElement = null;
    if (this.props.event.annotations.creation && this.props.event.annotations.creation.creatorName) {
      addedByElement = (
        <ImagePrefix iconName="user-plus">
          <FormattedMessage id={messages.addedBy.id} values={{ name: this.props.event.annotations.creation.creatorName }} />
        </ImagePrefix>
      );
    }

    let shareLinks = null;
    if (!this.props.amp) {
      shareLinks = (
        <ImagePrefix iconName="share-square-o" className="product-social-links">
          <a className="link-event-share twitter-share-button" href="https://twitter.com/intent/tweet?hashtags=dancedeets" data-count="none">Tweet</a>
          <div className="link-event-share fb-share-button" data-href={event.getUrl()} data-layout="button" data-size="small" data-mobile-iframe="true">
            <a className="fb-xfbml-parse-ignore" rel="noopener noreferrer" target="_blank" href={`https://www.facebook.com/sharer/sharer.php?u=${event.getUrl()}&amp;src=sdkpreparse`}>Share</a>
          </div>
        </ImagePrefix>
      );
    }

    const formattedStartEndText = formatStartEnd(event.start_time, event.end_time, this.props.intl);
    return (
      <Card>
        <ImagePrefix iconName={event.source.name === 'Facebook Event' ? 'facebook-square' : 'external-link'}>
          <FormattedMessage id={messages.source.id} /> <a className="link-event-source" href={event.source.url}>{event.source.name}</a>
        </ImagePrefix>
        <ImagePrefix
          icon={require('../img/categories.png')} // eslint-disable-line global-require
          amp={this.props.amp}
        >
          {event.annotations.categories.join(', ')}
        </ImagePrefix>
        <ImagePrefix iconName="clock-o">
          <FormatText>{formattedStartEndText}</FormatText>
          <meta itemProp="startDate" content={schemaDateFormat(event.start_time)} />
          {event.end_time ?
            <meta itemProp="endDate" content={schemaDateFormat(event.end_time)} /> :
            null}
        </ImagePrefix>
        <ImagePrefix iconName="calendar-plus-o">
          <a href={getAddToCalendarLink(event)} className="link-event-add-to-calendar"><FormattedMessage id={messages.addToCalendar.id} /></a>
        </ImagePrefix>
        {rsvpElement}
        {ticketElement}
        {addedByElement}
        {organizerElement}
        {shareLinks}
      </Card>
    );
  }
}
const EventLinks = injectIntl(_EventLinks);

class SimpleMap extends React.Component {
  props: {
    name: string;
    latitude: number;
    longitude: number;
  }
  render() {
    return (
      <GoogleMapLoader
        containerElement={
          <div
            style={{
              height: '100%',
            }}
          />
        }
        googleMapElement={
          <GoogleMap
            defaultZoom={13}
            defaultCenter={{ lat: this.props.latitude, lng: this.props.longitude }}
            /*
            scrollwheel={false}
            draggable={false}
            */
          >
            <Marker
              position={{ lat: this.props.latitude, lng: this.props.longitude }}
              label={this.props.name}
            />
          </GoogleMap>
        }
      />
    );
  }
}

class MapWithLinks extends React.Component {
  props: {
    event: Event;
    amp: boolean;
  }

  map() {
    const geocode = this.props.event.venue.geocode;
    if (!geocode || !geocode.latitude) {
      return null;
    }
    const mapUrl = `http://maps.google.com/?daddr=${geocode.latitude},${geocode.longitude}`;

    let mapContents = null;
    if (this.props.amp) {
      const staticMapImageUrl = (
        'http://www.google.com/maps/api/staticmap?key=AIzaSyAvvrWfamjBD6LqCURkATAWEovAoBm1xNQ&size=450x450&scale=2&zoom=13&' +
        `center=${geocode.latitude},${geocode.longitude}&` +
        `markers=color:blue%7C${geocode.latitude},${geocode.longitude}`
      );
      mapContents = (
        <amp-img
          src={staticMapImageUrl}
          layout="responsive"
          width="300"
          height="300"
        />
      );
    } else {
      mapContents = (<SimpleMap
        name={this.props.event.venue.name}
        latitude={geocode.latitude}
        longitude={geocode.longitude}
      />);
    }

    return (
      <div>
        <p>Open in <a className="link-event-map" href={mapUrl} rel="noopener noreferrer" target="_blank">Google Maps</a>.</p>
        { this.props.event.description ?
          <div className="visible-xs italics">Event description is below the map.</div> :
          null
        }
        <div style={{ height: '300px' }}>
          {mapContents}
        </div>
      </div>
    );
  }

  render() {
    const venue = this.props.event.venue;
    if (venue) {
      let locationName = <FormatText>{venue.name}</FormatText>;
      if (venue.id) {
        locationName = <a href={`https://www.facebook.com/${venue.id}`}>{locationName}</a>;
      }
      return (
        <Card>
          <ImagePrefix iconName="map-marker">
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
    event: Event;
  }

  render() {
    return (
      <Card>
        <div className="bold">Description:</div>
        <div className="google-translate" id="google_translate_element" />
        <FormatText>{this.props.event.description}</FormatText>
      </Card>
    );
  }
}

class EventPage extends React.Component {
  props: {
    event: JSONObject;
    amp: boolean;
    loggedIn: boolean;
    userRsvp: RsvpValue;
  }

  render() {
    const event = new Event(this.props.event);
    return (
      <div className="container" itemScope itemType="http://schema.org/DanceEvent">
        <meta itemProp="url" content="canonical_url" />
        <div className="row">
          <div className="col-xs-12">
            <Title event={event} />
          </div>
        </div>
        <div className="row">
          <div className="col-sm-5">
            <ImageWithLinks event={event} amp={this.props.amp} />
            <EventLinks
              event={event}
              amp={this.props.amp}
              loggedIn={this.props.loggedIn}
              userRsvp={this.props.userRsvp}
            />
            <MapWithLinks event={event} amp={this.props.amp} />
          </div>
          <div className="col-sm-7">
            <Description event={event} />
          </div>
        </div>
      </div>
    );
  }
}

class InternationalizedEventPage extends React.Component {
  render() {
    return (
      <Internationalize {...this.props}>
        <EventPage {...this.props} />
      </Internationalize>
    );
  }
}

export default InternationalizedEventPage;
