/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import Masonry from 'react-masonry-component';
import moment from 'moment';
import Helmet from 'react-helmet';
import upperFirst from 'lodash/upperFirst';
import { injectIntl, intlShape } from 'react-intl';
import { SearchEvent } from 'dancedeets-common/js/events/models';
import type { NewSearchResponse } from 'dancedeets-common/js/events/search';
import { formatStartDateOnly } from 'dancedeets-common/js/dates';
import { intlWeb } from 'dancedeets-common/js/intl';
import { SquareEventFlyer } from './eventCommon';
import { Card, ImagePrefix, wantsWindowSizes } from './ui';
import type { windowProps } from './ui';
import { SelectButton } from './MultiSelectList';

type Topic = Object;

export class _TopicEvent extends React.Component {
  props: {
    event: SearchEvent,
    lazyLoad: boolean,
    width: number,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    const event = this.props.event;

    const eventStart = moment(event.start_time);
    const eventStartDate = formatStartDateOnly(
      eventStart.toDate(),
      this.props.intl
    );

    return (
      <div className="grid-item" style={{ width: this.props.width }}>
        <Card>
          <SquareEventFlyer event={event} lazyLoad={this.props.lazyLoad} />
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
      </div>
    );
  }
}
const TopicEvent = injectIntl(_TopicEvent);

type VideoData = Object;

class Video extends React.Component {
  props: {
    video: VideoData,
    width: number,
  };

  render() {
    const scaledHeight = Math.floor(360 / 480 * 100);
    return (
      <div className="grid-item" style={{ width: this.props.width * 2 }}>
        <Card>
          <a
            href={`https://www.youtube.com/watch?v=${this.props.video.id
              .videoId}`}
          >
            <div
              style={{
                height: 0,
                paddingBottom: `${scaledHeight}%`,
              }}
            >
              <img
                src={this.props.video.snippet.thumbnails.high.url}
                role="presentation"
                style={{
                  width: '100%',
                }}
              />
            </div>
            <h3 className="event-title" style={{ marginTop: 10 }}>
              {this.props.video.snippet.title}
            </h3>
          </a>
        </Card>
      </div>
    );
  }
}

class SocialLink extends React.Component {
  static Platforms = {
    fb: {
      link: 'https://www.facebook.com/',
      imageName: 'facebook',
    },
    twitter: {
      link: 'https://www.twitter.com/',
      imageName: 'twitter',
    },
    instagram: {
      link: 'https://www.instagram.com/',
      imageName: 'instagram',
    },
    snapchat: {
      link: 'https://www.snapchat.com/add/',
      imageName: 'snapchat',
    },
    linkedin: {
      link: 'https://www.linkedin.com/in/',
      imageName: 'linkedin',
    },
    soundcloud: {
      link: 'https://www.soundcloud.com/',
      imageName: 'soundcloud',
    },
    medium: {
      link: 'https://www.medium.com/',
      imageName: 'medium',
    },
    youtube: {
      link: 'https://www.youtube.com/',
      imageName: 'youtube',
    },
    vimeo: {
      link: 'https://www.vimeo.com/',
      imageName: 'vimeo',
    },
    // tumblr, skype, whatsapp, medium, reddit, pinterest, wechat, vimeo,
  };

  props: {
    platform: string,
    username: string,
  };

  render() {
    const platform = SocialLink.Platforms[this.props.platform];
    const link = platform.link + this.props.username;
    const image = <ImagePrefix iconName={platform.imageName} />;
    return <a href={link}>{image}</a>;
  }
}

class Social extends React.Component {
  props: {
    topic: Topic,
  };

  render() {
    const socialLinks = Object.keys(this.props.topic.social).map(key =>
      <SocialLink
        key={key}
        platform={key}
        username={this.props.topic.social[key]}
      />
    );
    return <div>{socialLinks}</div>;
  }
}

class _EventList extends React.Component {
  props: {
    response: NewSearchResponse,
    videos: Object,
    topic: Topic,

    // Self-managed props
    window: windowProps,
  };

  state: {
    showVideos: boolean,
    showEvents: boolean,
  };

  constructor(props) {
    super(props);
    this.state = {
      showVideos: true,
      showEvents: true,
    };
  }

  render() {
    const resultEvents = this.props.response.results
      .map(eventData => new SearchEvent(eventData))
      .reverse();

    const resultVideos = this.props.videos.items.filter(x => x.id.videoId);

    const dateMap = {};
    if (this.state.showEvents) {
      resultEvents.forEach(event => {
        dateMap[`${event.start_time}event${event.id}`] = { event };
      });
    }
    if (this.state.showVideos) {
      resultVideos.forEach(video => {
        dateMap[`${video.snippet.publishedAt}video${video.id.videoId}`] = {
          video,
        };
      });
    }

    const margin = 2 * 10;
    let width = 200 + margin;
    if (this.props.window) {
      width =
        this.props.window.width / Math.floor(this.props.window.width / width) -
        margin;
    }

    const dates = Object.keys(dateMap).sort().reverse();
    const resultItems = dates.map((x, index) => {
      const item = dateMap[x];
      if (item.event) {
        return (
          <TopicEvent
            key={item.event.id}
            event={item.event}
            lazyLoad={index > 50}
            width={width}
          />
        );
      } else if (item.video) {
        return (
          <Video
            key={item.video.id.videoId}
            video={item.video}
            lazyLoad={index < 50}
            width={width}
          />
        );
      } else {
        console.log('Error unknown item:', item);
        return null;
      }
    });

    return (
      <div style={{ display: 'flex' }}>
        <Helmet title={this.props.topic.title} />
        <Social topic={this.props.topic} />
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
      </div>
    );
  }
}
const EventList = wantsWindowSizes(_EventList);

export const HelmetRewind = Helmet.rewind;
export default intlWeb(EventList);
