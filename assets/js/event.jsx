/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import FormatText from 'react-format-text';
import querystring from 'querystring';
import moment from 'moment';
import {intl} from './intl';
import {StartEnd} from './shared';

/* intersperse: Return an array with the separator interspersed between
 * each element of the input array.
 *
 * > _([1,2,3]).intersperse(0)
 * [1,0,2,0,3]
 */
function intersperse(arr, sep) {
  if (arr.length === 0) {
    return [];
  }

  return arr.slice(1).reduce(function(xs, x) {
    return xs.concat([sep, x]);
  }, [arr[0]]);
}

class Card extends React.Component {
  render() {
    return <div style={{borderRadius: '15px', backgroundColor: '#4C4D81', padding: '10px', margin: '10px'}}>
      {this.props.children}
    </div>;
  }
}

class Title extends React.Component {
  render() {
    const event = this.props.event;

    let categoryLinks = null;
    if (event.annotations.categories) {
      const categories = event.annotations.categories.map(x => <a href={`/?keywords=${x}`}>{x}</a>);
      categoryLinks = <li>categorized as: {intersperse(categories, ', ')}.</li>;
    }
    let locationLinks = null;
    if (event.cityStateCountry) {
      locationLinks = <li>in <a href={`/?location=${event.cityStateCountry}`}>{event.cityStateCountry}</a>.</li>;
    }
    let moreLinks = null;
    if (categoryLinks || locationLinks) {
      moreLinks = <div>
        See more events:
        <ul>
          {locationLinks}
          {categoryLinks}
        </ul>
      </div>;
    }

    return <Card>
      {moreLinks}
      <h2>{this.props.event.name}</h2>
    </Card>;
  }
}

class ImagePrefix extends React.Component {
  render() {
    return <div style={{paddingLeft: '5px', paddingTop: '5px', display: 'table'}}>
      {this.props.iconName ?
        <i className={'fa fa-' + this.props.iconName + ' fa-lg'} style={{paddingRight: '5px', width: '1.5em', display: 'table-cell'}}></i> :
        null
      }
      <div style={{display: 'table-cell'}}>
      {this.props.children}
      </div>
    </div>;
  }
}

class ImageWithLinks extends React.Component {
  render() {
    return <Card><img
      src={this.props.event.picture.source}
      style={{
        width: '100%',
        borderRadius: '5px',
      }}
    /><br/>
    <ImagePrefix iconName="picture-o">
      <a className="link-event-flyer" href={'/events/image_proxy/' + this.props.event.id}>See Full Flyer</a>
    </ImagePrefix>
    </Card>;
  }
}
// TODO: add calendar_start_end
// TODO: add full_address
// TODO: add canonical_url
function getAddToCalendarLink(event) {
  const args = {
    action: 'TEMPLATE',
    text: event.name,
    dates: '{{event.calendar_start_end|urlencode }}',
    details: 'Event Details:\nevent.canonical_url',
    location: 'event.full_address'.replace('\n', ', '),
    sf: true,
    output: 'xml',
  };
  return 'https://www.google.com/calendar/render?' + querystring.stringify(args);
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

// TODO: add duration_human_format() for Time
class EventLinks extends React.Component {
  render() {
    const event = this.props.event;
    let rsvpElement = null;
    if (event.rsvp.attending_count || event.rsvp.maybe_count) {
      rsvpElement = <ImagePrefix iconName="users">
        {rsvpString(event)}
      </ImagePrefix>;
    }
    let organizerElement = null;
    if (event.admins) {
      const admins = event.admins.map(admin => (
        <li><a
          key={admin.id}
          className="link-event-admin"
          href={`https://www.facebook.com/${admin.id}`}
        >{admin.name}</a></li>));
      organizerElement = <ImagePrefix iconName="user">
        Organizers:<br/>
        <ul>
        {admins}
        </ul>
      </ImagePrefix>;
    }

    return <Card>
      <ImagePrefix iconName={event.source.name === 'Facebook Event' ? 'facebook-square' : 'external-link'}>
        <a className="link-event-source" href={event.source.url}>{'View Original: ' + event.source.name}</a>
      </ImagePrefix>
      <ImagePrefix>
        <a className="link-event-share twitter-share-button" href="https://twitter.com/intent/tweet?hashtags=dancedeets" data-count="none">Tweet</a>
        <div className="link-event-share fb-share-button" data-href="{{ canonical_url }}" data-layout="button" data-size="small" data-mobile-iframe="true"><a className="fb-xfbml-parse-ignore" target="_blank" href="https://www.facebook.com/sharer/sharer.php?u={{ canonical_url }}&amp;src=sdkpreparse">Share</a></div>
      </ImagePrefix>
      <ImagePrefix iconName="clock-o">
        <StartEnd start={event.start_time} end={event.end_time} tagName={FormatText} />
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
    </Card>;
  }
}

// TODO: full_address
class MapWithLinks extends React.Component {
  map() {
    const geocode = this.props.event.venue.geocode;
    if (!geocode.latitude) {
      return null;
    }
    const mapUrl = `http://maps.google.com/?daddr=${geocode.latitude},${geocode.longitude}`;
    return <div>
      { this.props.event.description ?
        <div className="visible-xs" style={{fontStyle: 'italic'}}>Event description is below the map.</div> :
        null
      }
      <a className="link-event-map" href={mapUrl} target="_blank">
        <div id="map-wrapper" className="responsive-map-wrapper" />
      </a>
    </div>;
  }

  render() {
    const venue = this.props.event.venue;
    if (venue) {
      let locationName = venue.name;
      if (venue.id) {
        locationName = <a href={`https://www.facebook.com/${venue.id}`}>{locationName}</a>;
      }
      return <Card>
        <ImagePrefix iconName="map-marker">
          {locationName}<br/>
          <FormatText>{venue.full_address}</FormatText>
        </ImagePrefix>
        {this.map()}
      </Card>;
    }
    return null;
  }
}

class Description extends React.Component {
  render() {
    return <Card><FormatText>{this.props.event.description}</FormatText></Card>;
  }
}

export default class EventPage extends React.Component {
  render() {
    return <div>
      <div className="row">
        <div className="col-xs-12">
          <Title event={this.props.event}/>
        </div>
      </div>
      <div className="row">
        <div className="col-sm-5">
          <ImageWithLinks event={this.props.event}/>
          <EventLinks event={this.props.event}/>
          <MapWithLinks event={this.props.event}/>
        </div>
        <div className="col-sm-7">
          <Description event={this.props.event}/>
        </div>
      </div>
    </div>;
  }
}

module.exports = intl(EventPage);
