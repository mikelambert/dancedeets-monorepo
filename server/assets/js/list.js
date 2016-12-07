/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import url from 'url';
import FormatText from 'react-format-text';
import type {
  Cover,
  JSONObject,
} from 'dancedeets-common/js/events/models';
import {
  formatStartEnd,
} from 'dancedeets-common/js/dates';
import {
  formatAttending,
} from 'dancedeets-common/js/events/helpers';

type SearchEvent = {
  id: string;
  picture: Cover;
  categories: Array<string>;
  keywords: Array<string>;
  start_time: Date;
  end_time: Date;
};
type OneboxResult = any;
type EventResult = SearchEvent;
type Result = OneboxResult | EventResult;

class EventFlyer extends React.Component {
  props: {
    event: SearchEvent;
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

    if (event.image) {
      const croppedPicture = this.generateCroppedCover(picture, width, height);
      const extraImageProps = {
        width,
        height,
        border: 0,
      };
      const imageTag = (<img
        role="presentation"
        src={croppedPicture.source}
        {...extraImageProps}
      />);
      const lazyImageTag = (<span>
        <img
          role="presentation"
          className="lazy-wide"
          src="/images/placeholder.gif"
          data-original={croppedPicture.source}
          {...extraImageProps}
        />
        <noscript>{imageTag}</noscript>
      </span>);

      return (
        <a className="link-event-flyer" href={eventImageUrl}>
          {this.props.lazyLoad ? lazyImageTag : imageTag }
        </a>
      );
    }
    return null;
  }
}

class EventDescription extends React.Component {
  props: {
    event: SearchEvent;
    indexingBot: boolean;
  }

  render() {
    const event = this.props.event;
    const keywords = [...event.categories];
    if (self.indexingBot) {
      keywords.push(...event.keywords);
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

class HorizontalEvent extends React.Component {
  props: {
    event: SearchEvent;
    lazyLoad: boolean;
  }

  render() {
    const event = this.props.event;
    return (
      <li className="wide-event clearfix">
        <div className="event-image">
          <EventFlyer event={this.props.event} lazyLoad={this.props.lazyLoad} />
          <EventDescription event={this.props.event} />
        </div>
      </li>
    );
  }
}

class ResultsList extends React.Component {
  props: {
    results: Array<Result>;
  }
  render() {
    const results = this.props.results.map(x => x);
    return (
      <ol className="events-list">
        {results}
      </ol>
    );
  }
}

/*
{% macro render_wide_results(results, use_rsvp_form=True) %}
  {% set cur_date = None %}
  {% set cur_time = None %}
  <ol class="events-list">
  {% for result in results %}
    {% if cur_date != result.start_time.date() %}
      {% set cur_date = result.start_time.date() %}
      <li class="wide-event day-header">{{ cur_date|date_only_human_format }}</li>
      {% set cur_time = None %}
    {% endif %}
    {% if cur_time != result.start_time.time() %}
      {% set cur_time = result.start_time.time() %}
      <li><b>{{ cur_time|time_human_format }}</b></li>
    {% endif %}
  {% endfor %}
  </ol>
{% endmacro %}
*/
