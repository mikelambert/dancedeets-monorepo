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
  injectIntl,
  intlShape,
} from 'react-intl';
import {
  defaultLocale,
  intl,
} from 'dancedeets-common/js/intl';
import {
  formatStartEnd,
} from 'dancedeets-common/js/dates';
import {
  Event,
  JSONObject,
} from 'dancedeets-common/js/events/models';

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
    children: Array<React.Element<*>>;
  }

  render() {
    return (<div style={{ borderRadius: '15px', backgroundColor: '#4C4D81', padding: '10px', margin: '10px' }}>
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
      categoryLinks = <li>categorized as: {intersperse(categories, ', ')}.</li>;
    }
    let locationLinks = null;
    if (event.venue.cityStateCountry()) {
      locationLinks = <li>in <a href={`/?location=${event.venue.cityStateCountry()}`}>{event.venue.cityStateCountry()}</a>.</li>;
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
    iconName: string;
    children: Array<React.Element<*>>;
  }

  render() {
    const { iconName, children, ...props } = this.props;
    return (<div style={{ paddingLeft: '5px', paddingTop: '5px', display: 'table' }} {...props}>
      {iconName ?
        <i className={`fa fa-${this.props.iconName} fa-lg`} style={{ paddingRight: '5px', width: '1.5em', display: 'table-cell', textAlign: 'center' }} /> :
        null
      }
      <div style={{ display: 'table-cell' }}>
        {children}
      </div>
    </div>);
  }
}

class ImageWithLinks extends React.Component {
  props: {
    event: Event;
  }

  render() {
    if (!this.props.event.picture) {
      return null;
    }
    const url = `/events/image_proxy/${this.props.event.id}`;
    return (
      <Card>
        <a className="link-event-flyer" href={url}>
          <img
            role="presentation"
            src={this.props.event.picture.source}
            style={{
              width: '100%',
              borderRadius: '5px',
            }}
          />
        </a>
        <br />
        <ImagePrefix iconName="picture-o">
          <a className="link-event-flyer" href={url}>See Full Flyer</a>
        </ImagePrefix>
      </Card>
    );
  }
}
// TODO: add calendar_start_end
function getAddToCalendarLink(event) {
  const args = {
    action: 'TEMPLATE',
    text: event.name,
    dates: '{{event.calendar_start_end|urlencode }}',
    details: `Event Details:\n${event.getUrl()}`,
    location: event.venue.fullAddress().replace('\n', ', '),
    sf: true,
    output: 'xml',
  };
  const query = querystring.stringify(args);
  return `https://www.google.com/calendar/render?${query}`;
}

function rsvpString(event) {
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

    // Self-managed props
    intl: intlShape;

  }

  render() {
    const event = this.props.event;
    let rsvpElement = null;
    if (event.rsvp.attending_count || event.rsvp.maybe_count) {
      rsvpElement = (
        <ImagePrefix iconName="users">
          {rsvpString(event)}
        </ImagePrefix>
      );
    }
    let organizerElement = null;
    if (event.admins) {
      const admins = event.admins.map(admin => (
        <li><a
          key={admin.id}
          className="link-event-admin"
          href={`https://www.facebook.com/${admin.id}`}
        >{admin.name}</a></li>));
      organizerElement = (
        <ImagePrefix iconName="user">
          Organizers:<br />
          <ul>
            {admins}
          </ul>
        </ImagePrefix>
      );
    }

    const formattedStartEndText = formatStartEnd(event.start_time, event.end_time, this.props.intl);
    return (
      <Card>
        <ImagePrefix className="product-social-links">
          <a className="link-event-share twitter-share-button" href="https://twitter.com/intent/tweet?hashtags=dancedeets" data-count="none">Tweet</a>
          <div className="link-event-share fb-share-button" data-href="{{ canonical_url }}" data-layout="button" data-size="small" data-mobile-iframe="true">
            <a className="fb-xfbml-parse-ignore" rel="noopener noreferrer" target="_blank" href="https://www.facebook.com/sharer/sharer.php?u={{ canonical_url }}&amp;src=sdkpreparse">Share</a>
          </div>
        </ImagePrefix>
        <ImagePrefix iconName={event.source.name === 'Facebook Event' ? 'facebook-square' : 'external-link'}>
          <a className="link-event-source" href={event.source.url}>{`View Original: ${event.source.name}`}</a>
        </ImagePrefix>
        <ImagePrefix iconName="clock-o">
          <FormatText>{formattedStartEndText}</FormatText>
          <meta itemProp="startDate" content={schemaDateFormat(event.start_time)} />
          {event.end_time ?
            <meta itemProp="endDate" content={schemaDateFormat(event.end_time)} /> :
            null}
        </ImagePrefix>
        <ImagePrefix iconName="calendar-plus-o">
          <a href={getAddToCalendarLink(event)} className="link-event-add-to-calendar">Add to Google Calendar</a>
        </ImagePrefix>
        {rsvpElement}
        {organizerElement}
      </Card>
    );
  }
}
const EventLinks = injectIntl(_EventLinks);

class MapWithLinks extends React.Component {
  props: {
    event: Event;
  }

  map() {
    const geocode = this.props.event.venue.geocode;
    if (!geocode.latitude) {
      return null;
    }
    const mapUrl = `http://maps.google.com/?daddr=${geocode.latitude},${geocode.longitude}`;
    return (
      <div>
        { this.props.event.description ?
          <div className="visible-xs" style={{ fontStyle: 'italic' }}>Event description is below the map.</div> :
          null
        }
        <a className="link-event-map" href={mapUrl} rel="noopener noreferrer" target="_blank">
          <div id="map-wrapper" className="responsive-map-wrapper" />
        </a>
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
        <div style={{ fontWeight: 'bold' }}>Description:</div>
        <div style={{ height: '25px' }} id="google_translate_element" />
        <FormatText>{this.props.event.description}</FormatText>
      </Card>
    );
  }
}

export default class EventPage extends React.Component {
  props: {
    event: JSONObject;
  }

  render() {
    const event = new Event(this.props.event);
    return (
      <div className="container" itemScope itemType="http://schema.org/DanceEvent">
        <span itemProp="url" content="canonical_url" />
        <div className="row">
          <div className="col-xs-12">
            <Title event={event} />
          </div>
        </div>
        <div className="row">
          <div className="col-sm-5">
            <ImageWithLinks event={event} />
            <EventLinks event={event} />
            <MapWithLinks event={event} />
          </div>
          <div className="col-sm-7">
            <Description event={event} />
          </div>
        </div>
      </div>
    );
  }
}

function getCurrentLocale() {
  // TODO: load the locale from the incoming request headers
  return defaultLocale;
}

module.exports = intl(EventPage, getCurrentLocale());
