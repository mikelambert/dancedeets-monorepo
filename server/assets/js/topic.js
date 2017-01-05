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
import {
  SelectButton,
} from './MultiSelectList';


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

    return (<div
      className="grid-item"
      style={{ width: '20%' }}
    >
      <Card>
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
      </Card>
    </div>);
  }
}
const TopicEvent = injectIntl(_TopicEvent);

type VideoData = Object;

class Video extends React.Component {
  props: {
    video: VideoData;
  };

  render() {
    return (<div
      className="grid-item"
      style={{ width: '40%' }}
    >
      <Card>
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
      </Card>
    </div>);
  }
}

class EventList extends React.Component {
  props: {
    results: NewSearchResults;
    videos: Object;
  };

  state: {
    showVideos: boolean;
    showEvents: boolean;
  };

  constructor(props) {
    super(props);
    this.state = {
      showVideos: true,
      showEvents: true,
    };
  }

  render() {
    const resultEvents = this.props.results.results.map(eventData => new SearchEvent(eventData)).reverse();

    const resultVideos = this.props.videos.items.filter(x => x.id.videoId);

    const dateMap = {};
    if (this.state.showEvents) {
      resultEvents.forEach((event) => {
        dateMap[`${event.start_time}event${event.id}`] = { event };
      });
    }
    if (this.state.showVideos) {
      resultVideos.forEach((video) => {
        dateMap[`${video.snippet.publishedAt}video${video.id.videoId}`] = { video };
      });
    }

    const dates = Object.keys(dateMap).sort().reverse();
    const resultItems = dates.map((x, index) => {
      const item = dateMap[x];
      if (item.event) {
        return <TopicEvent key={item.event.id} event={item.event} lazyLoad={index > 50} />;
      } else if (item.video) {
        return <Video key={item.video.id.videoId} video={item.video} lazyLoad={index < 50} />;
      } else {
        console.log('Error unknown item:', item);
        return null;
      }
    });

    return (<div style={{ display: 'flex' }}>
      <div style={{ flex: 1, padding: 10 }}>
        Show:{' '}
        <div className="btn-group" role="group">
          <SelectButton
            toggleState={() => {
              this.setState({ showEvents: !this.state.showEvents });
            }}
            active={this.state.showEvents}
            item={`${resultEvents.length} Events`}
          />
          <SelectButton
            toggleState={() => {
              this.setState({ showVideos: !this.state.showVideos });
            }}
            active={this.state.showVideos}
            item={`${resultVideos.length} Videos`}
          />
        </div>
        <Masonry
          options={{
            // set itemSelector so .grid-sizer is not used in layout
            itemSelector: '.grid-item',
            // use element for option
            columnWidth: '.grid-sizer',
            percentPosition: true,
          }}
        >
          <div className="grid-sizer" style={{ width: '20%' }} >&nbsp;</div>

          {resultItems}
        </Masonry>
      </div>
    </div>);
  }
}

export default intlWeb(EventList);
