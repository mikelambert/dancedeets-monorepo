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
  wantsWindowSizes,
} from './ui';
import type {
  windowProps,
} from './ui';
import {
  SelectButton,
} from './MultiSelectList';


export class _TopicEvent extends React.Component {
  props: {
    event: SearchEvent;
    lazyLoad: boolean;
    width: number;

    // Self-managed props
    intl: intlShape,
  }

  render() {
    const event = this.props.event;

    const eventStart = moment(event.start_time);
    const eventStartDate = upperFirst(this.props.intl.formatDate(eventStart.toDate(), weekdayDate));

    return (<div
      className="grid-item"
      style={{ width: this.props.width }}
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
    width: number;
  };

  render() {
    return (<div
      className="grid-item"
      style={{ width: this.props.width * 2 }}
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
          <h3 className="event-title" style={{ marginTop: 10 }}>
            {this.props.video.snippet.title}
          </h3>
        </a>
      </Card>
    </div>);
  }
}

class _EventList extends React.Component {
  props: {
    results: NewSearchResults;
    videos: Object;

    // Self-managed props
    window: windowProps;
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

    const margin = 2 * 10;
    let width = 200 + margin;
    if (this.props.window) {
      width = (this.props.window.width / Math.floor(this.props.window.width / width)) - margin;
    }

    const dates = Object.keys(dateMap).sort().reverse();
    const resultItems = dates.map((x, index) => {
      const item = dateMap[x];
      if (item.event) {
        return <TopicEvent key={item.event.id} event={item.event} lazyLoad={index > 50} width={width} />;
      } else if (item.video) {
        return <Video key={item.video.id.videoId} video={item.video} lazyLoad={index < 50} width={width} />;
      } else {
        console.log('Error unknown item:', item);
        return null;
      }
    });

    return (<div style={{ display: 'flex' }}>
      <div style={{ flex: 1, padding: 10 }}>
        <Card>
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
        </Card>
        <Masonry>
          {resultItems}
        </Masonry>
      </div>
    </div>);
  }
}
const EventList = wantsWindowSizes(_EventList);

export default intlWeb(EventList);
