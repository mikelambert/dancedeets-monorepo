/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import url from 'url';
import FormatText from 'react-format-text';
import moment from 'moment';
import _ from 'lodash/string';
import {
  injectIntl,
  intlShape,
} from 'react-intl';
import LazyLoad from 'react-lazyload';
import { StickyContainer, Sticky } from 'react-sticky';
import {
  Internationalize,
} from 'dancedeets-common/js/intl';
import type {
  Cover,
  JSONObject,
} from 'dancedeets-common/js/events/models';
import {
  SearchEvent,
} from 'dancedeets-common/js/events/models';
import type {
  NewSearchResults,
} from 'dancedeets-common/js/events/search';
import {
  formatStartEnd,
  weekdayDate,
  weekdayTime,
} from 'dancedeets-common/js/dates';
import {
  formatAttending,
} from 'dancedeets-common/js/events/helpers';

type OneboxResult = any;
type EventResult = SearchEvent;
type Result = OneboxResult | EventResult;

class EventFlyer extends React.Component {
  props: {
    event: SearchEvent;
    lazyLoad: boolean;
  }

  generateCroppedCover(picture: Cover, width: number, height: number) {
    const parsedSource = url.parse(picture.source, true);
    parsedSource.query = { ...parsedSource.query, width, height };
    const newSourceUrl = url.format(parsedSource);

    return {
      source: newSourceUrl,
      width,
      height,
    };
  }

  render() {
    const event = this.props.event;
    const picture = event.picture;
    if (!picture) {
      return null;
    }
    const eventImageUrl = picture.source;

    const width = 180;
    const height = 180;

    const croppedPicture = this.generateCroppedCover(picture, width, height);
    let imageTag = (<img
      role="presentation"
      src={croppedPicture.source}
      width={width}
      height={height}
      className="no-border"
    />);
    if (this.props.lazyLoad) {
      imageTag = <LazyLoad height={height} once>{imageTag}</LazyLoad>;
    }
    return (
      <div className="event-image">
        <a className="link-event-flyer" href={eventImageUrl}>
          {imageTag}
        </a>
      </div>
    );
  }
}

class _EventDescription extends React.Component {
  props: {
    event: SearchEvent;
    indexingBot: boolean;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const event = this.props.event;
    const keywords = [...event.annotations.categories];
    if (this.props.indexingBot) {
      keywords.push(...event.annotations.keywords);
    }

    let rsvpElement = null;
    if (event.rsvp && (event.rsvp.attending_count || event.rsvp.maybe_count)) {
      rsvpElement = <div className="event-attending">{formatAttending(this.props.intl, event.rsvp)}</div>;
    }

    // TODO: fix up event venue display
    return (
      <div className="event-description">
        <h3 className="event-title">
          <a href={event.getUrl()}>
            <span>{event.name}</span>
          </a>
        </h3>
        <div className="event-types">
          ({keywords.join(', ')})
        </div>
        <div className="event-date">
          {formatStartEnd(event.start_time, event.end_time, this.props.intl)}
        </div>
        <div className="event-city">
          <div>{event.venue.name}</div>
          <FormatText>{event.venue.streetCityStateCountry('\n')}</FormatText>
        </div>
        {rsvpElement}
      </div>
    );
  }
}
const EventDescription = injectIntl(_EventDescription);

class HorizontalEvent extends React.Component {
  props: {
    event: SearchEvent;
    lazyLoad: boolean;
  }

  render() {
    const event = this.props.event;
    return (
      <div className="wide-event clearfix">
        <EventFlyer event={this.props.event} lazyLoad={this.props.lazyLoad} />
        <EventDescription event={this.props.event} />
      </div>
    );
  }
}

class _ResultsList extends React.Component {
  props: {
    results: NewSearchResults;
    past: boolean;

    // Self-managed props
    intl: intlShape;
  }
  render() {
    const resultEvents = this.props.results.results.map(eventData => new SearchEvent(eventData));

    const now = moment();
    let events = [];
    if (this.props.past) {
      events = resultEvents.filter(event => moment(event.start_time) < now);
    } else {
      events = resultEvents.filter(event => moment(event.end_time) > now);
    }
    // const futureEvents = resultEvents.filter(event => moment(event.start_time) > now);
    // const currentEvents = resultEvents.filter(event => moment(event.start_time) < now && moment(event.end_time) > now);
    // const nonPastEvents = resultEvents.filter(event => moment(event.end_time) > now);
    const resultItems = [];
    events.forEach((event, index) => {
      const eventStart = moment(event.start_time);
      const eventStartDate = _.upperFirst(this.props.intl.formatDate(eventStart.toDate(), weekdayDate));
      const eventStartTime = _.upperFirst(this.props.intl.formatDate(eventStart.toDate(), weekdayTime));
      let currentDate = null;
      let currentTime = null;
      if (eventStartDate !== currentDate) {
        resultItems.push(<li key={eventStartDate} className="wide-event day-header"><Sticky className="opaque">{eventStartDate}</Sticky></li>);
        currentDate = eventStartDate;
        currentTime = null;
      }
      if (eventStartTime !== currentTime) {
        resultItems.push(<li key={`${eventStartDate} ${eventStartTime}`}><b>{eventStartTime}</b></li>);
        currentTime = eventStartTime;
      }
      resultItems.push(<li><HorizontalEvent key={event.id} event={event} lazyLoad={index > 8} /></li>);
    });
    return (
      <StickyContainer>
        <ol className="events-list">
          {resultItems}
        </ol>
      </StickyContainer>
    );
  }
}
const ResultsList = injectIntl(_ResultsList);


class InternationalizedResultsList extends React.Component {
  render() {
    return (
      <Internationalize {...this.props}>
        <ResultsList {...this.props} />
      </Internationalize>
    );
  }
}

export default InternationalizedResultsList;
