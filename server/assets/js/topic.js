/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import Masonry from 'react-masonry-component';
import moment from 'moment';
import upperFirst from 'lodash/upperFirst';
import {
  injectIntl,
  intlShape,
} from 'react-intl';
import {
  SearchEvent,
} from 'dancedeets-common/js/events/models';
import type {
  NewSearchResults,
} from 'dancedeets-common/js/events/search';
import {
  weekdayDate,
} from 'dancedeets-common/js/dates';
import {
  intlWeb,
} from 'dancedeets-common/js/intl';
import {
  EventFlyer,
} from './eventSearchResults';
import {
  Card,
  ImagePrefix,
} from './ui';


export class _TopicEvent extends React.Component {
  props: {
    event: SearchEvent;
    lazyLoad: boolean;

    // Self-managed props
    intl: intlShape,
  }

  render() {
    const event = this.props.event;

    const eventStart = moment(event.start_time);
    const eventStartDate = upperFirst(this.props.intl.formatDate(eventStart.toDate(), weekdayDate));

    return (<Card
      style={{
        display: 'inline-block',
        width: 200,
        verticalAlign: 'top',
      }}
    >
      <EventFlyer event={event} lazyLoad={this.props.lazyLoad} />
      <h3 className="event-title" style={{ marginTop: 10 }}>
        <a href={event.getUrl()}>
          <span>{event.name}</span>
        </a>
      </h3>
      <div className="event-city">
        {eventStartDate}
      </div>
      <div className="event-city">
        {event.venue.cityStateCountry('\n')}
      </div>
    </Card>);
  }
}
const TopicEvent = injectIntl(_TopicEvent);

type VideoData = Object;

class Video extends React.Component {
  props: {
    video: VideoData;
  };

  render() {
    return (<Card>
      <a href={`https://www.youtube.com/watch?v=${this.props.video.id.videoId}`}>
        <img
          src={this.props.video.snippet.thumbnails.high.url}
          role="presentation"
          style={{
            width: '100%',
          }}
        />
        <div>
          {this.props.video.snippet.title}
        </div>
      </a>
    </Card>);
  }
}

class VideoList extends React.Component {
  props: {
    videos: {
      items: Array<VideoData>;
    };
  }
  render() {
    const actualVideos = this.props.videos.items.filter(x => x.id.videoId);
    return (<div>
      {actualVideos.map(x => <Video key={x.id.videoId} video={x} />)}
    </div>);
  }
}

class EventList extends React.Component {
  props: {
    results: NewSearchResults;
    videos: Object;
  }

  render() {
    const resultEvents = this.props.results.results.map(eventData => new SearchEvent(eventData)).reverse();

    const resultItems = [];
    resultEvents.forEach((event, index) => {
      resultItems.push(<TopicEvent key={event.id} event={event} lazyLoad={index > 50} />);
    });

    return (<div style={{ display: 'flex' }}>
      <div style={{ flex: 2, padding: 10 }}>
        <div>{resultItems.length} Related Events:</div>
        <Masonry>
          {resultItems}
        </Masonry>
      </div>
      <div style={{ flex: 1, padding: 10 }}>
        <div>Recent Videos:</div>
        <VideoList videos={this.props.videos} />
      </div>
    </div>);
  }
}

export default intlWeb(EventList);
