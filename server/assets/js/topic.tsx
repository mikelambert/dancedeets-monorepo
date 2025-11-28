/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import Masonry from 'react-masonry-component';
import FormatText from 'react-format-text';
import Helmet from 'react-helmet';
import { injectIntl, InjectedIntlProps } from 'react-intl';
import { SearchEvent } from 'dancedeets-common/js/events/models';
import type { NewSearchResponse } from 'dancedeets-common/js/events/search';
import { formatStartDateOnly } from 'dancedeets-common/js/dates';
import { intlWeb } from 'dancedeets-common/js/intl';
import { SquareEventFlyer } from './eventCommon';
import {
  Card,
  ImagePrefix,
  ImagePrefixInline,
  Truncate,
  wantsWindowSizes,
} from './ui';
import type { WindowProps } from './ui';
import { SelectButton } from './MultiSelectList';

type Topic = Record<string, unknown>;
type VideoData = Record<string, unknown>;

interface TopicEventProps {
  event: SearchEvent;
  lazyLoad: boolean;
  width: number;
}

type TopicEventPropsWithIntl = TopicEventProps & InjectedIntlProps;

export class _TopicEvent extends React.Component<TopicEventPropsWithIntl> {
  render(): React.ReactElement {
    const { event } = this.props;

    const eventStartDate = formatStartDateOnly(
      event.getStartMoment({ timezone: false }),
      this.props.intl
    );

    return (
      <div className="grid-item" style={{ width: this.props.width }}>
        <Card>
          <SquareEventFlyer event={event} lazyLoad={this.props.lazyLoad} />
          <h3 className="event-title" style={{ marginTop: 10 }}>
            <a href={event.getUrl()}>
              <ImagePrefix iconName="calendar">
                <span>{event.name}</span>
              </ImagePrefix>
            </a>
          </h3>
          <div className="event-city">{eventStartDate}</div>
          <div className="event-city">{event.venue.cityStateCountry('\n')}</div>
        </Card>
      </div>
    );
  }
}
const TopicEvent = injectIntl(_TopicEvent);

interface VideoProps {
  video: VideoData;
  width: number;
}

class Video extends React.Component<VideoProps> {
  render(): React.ReactElement {
    const scaledHeight = Math.floor(360 / 480 * 100);
    const video = this.props.video as {
      id: { videoId: string };
      snippet: { thumbnails: { high: { url: string } }; title: string };
    };
    return (
      <div className="grid-item" style={{ width: this.props.width * 2 }}>
        <Card>
          <a
            href={`https://www.youtube.com/watch?v=${video.id.videoId}`}
          >
            <div
              style={{
                height: 0,
                paddingBottom: `${scaledHeight}%`,
              }}
            >
              <img
                src={video.snippet.thumbnails.high.url}
                alt=""
                style={{
                  width: '100%',
                }}
              />
            </div>
            <h3 className="event-title" style={{ marginTop: 10 }}>
              <ImagePrefix iconName="youtube">
                {video.snippet.title}
              </ImagePrefix>
            </h3>
          </a>
        </Card>
      </div>
    );
  }
}

interface InstagramData {
  type: string;
  id: string;
  code: string;
  created_time: number;
  caption: { text: string };
  images: { low_resolution: { url: string } };
}

interface InstagramProps {
  instagram: InstagramData;
  width: number;
}

class Instagram extends React.Component<InstagramProps> {
  processTitle(text: string): string {
    let newText = text;
    newText = newText.split('\n')[0];
    newText = newText.split('. ')[0];
    newText = newText
      .split(' ')
      .splice(0, 20)
      .join(' ');
    return newText;
  }

  render(): React.ReactElement {
    const scaledHeight = Math.floor(100);
    const title = this.processTitle(this.props.instagram.caption.text);
    return (
      <div className="grid-item" style={{ width: this.props.width * 2 }}>
        <Card>
          <a href={`https://www.instagram.com/p/${this.props.instagram.code}`}>
            <div
              style={{
                height: 0,
                paddingBottom: `${scaledHeight}%`,
              }}
            >
              <img
                src={this.props.instagram.images.low_resolution.url}
                alt=""
                style={{
                  width: '100%',
                }}
              />
            </div>
            <h3 className="event-title" style={{ marginTop: 10 }}>
              <ImagePrefix iconName="instagram">{title}</ImagePrefix>
            </h3>
          </a>
        </Card>
      </div>
    );
  }
}

interface PlatformData {
  link: string;
  imageName: string;
}

interface SocialLinkProps {
  platform: string;
  username: string;
}

class SocialLink extends React.Component<SocialLinkProps> {
  static Platforms: Record<string, PlatformData> = {
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
    youtube: {
      link: 'https://www.youtube.com/',
      imageName: 'youtube',
    },
    vimeo: {
      link: 'https://www.vimeo.com/',
      imageName: 'vimeo',
    },
    website: {
      link: '',
      imageName: 'external-link',
    },
    email: {
      link: 'mailto:',
      imageName: 'envelope',
    },
  };

  render(): React.ReactElement {
    const platformData = SocialLink.Platforms[this.props.platform];
    const link = platformData.link + this.props.username;
    const image = (
      <ImagePrefixInline iconName={platformData.imageName}>
        {this.props.username}
      </ImagePrefixInline>
    );
    return <a href={link}>{image}</a>;
  }
}

interface SocialLinksProps {
  topic: Topic;
}

class SocialLinks extends React.Component<SocialLinksProps> {
  render(): React.ReactElement {
    const social = this.props.topic.social as Record<string, string>;
    const socialLinks = Object.keys(social).map(key => (
      <div key={key}>
        <SocialLink platform={key} username={social[key]} />
      </div>
    ));
    return <div>{socialLinks}</div>;
  }
}

interface EventListProps {
  response: NewSearchResponse;
  videos: { items: VideoData[] };
  instagrams: { items: InstagramData[] };
  window: WindowProps;
}

interface EventListState {
  showVideos: boolean;
  showEvents: boolean;
  showInstagrams: boolean;
}

class _EventList extends React.Component<EventListProps, EventListState> {
  constructor(props: EventListProps) {
    super(props);
    this.state = {
      showVideos: true,
      showEvents: true,
      showInstagrams: true,
    };
  }

  render(): React.ReactElement {
    const resultEvents = this.props.response.results
      .map(eventData => new SearchEvent(eventData))
      .reverse();

    const videos = this.props.videos as {
      items: Array<{ id: { videoId: string }; snippet: { publishedAt: string } }>;
    };
    const resultVideos = videos.items.filter(x => x.id.videoId);
    const resultInstagramVideos = this.props.instagrams.items.filter(
      x => x.type === 'video'
    );

    const dateMap: Record<string, { event?: SearchEvent; video?: VideoData; instagram?: InstagramData }> = {};
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
    if (this.state.showInstagrams) {
      resultInstagramVideos.forEach(instagram => {
        const timestamp = new Date(instagram.created_time * 1000).toISOString();
        dateMap[`${timestamp}instagram${instagram.id}`] = {
          instagram,
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

    const dates = Object.keys(dateMap)
      .sort()
      .reverse();
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
            key={(item.video as { id: { videoId: string } }).id.videoId}
            video={item.video}
            width={width}
          />
        );
      } else if (item.instagram) {
        return (
          <Instagram
            key={item.instagram.id}
            instagram={item.instagram}
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
        <div style={{ flex: 1, padding: 10 }}>
          <Card>
            Show:{' '}
            <div className="btn-group" role="group">
              {resultEvents.length ? (
                <SelectButton
                  toggleState={() => {
                    this.setState({ showEvents: !this.state.showEvents });
                  }}
                  active={this.state.showEvents}
                  item={`${resultEvents.length} Events`}
                />
              ) : null}
              {resultVideos.length ? (
                <SelectButton
                  toggleState={() => {
                    this.setState({ showVideos: !this.state.showVideos });
                  }}
                  active={this.state.showVideos}
                  item={`${resultVideos.length} Videos`}
                />
              ) : null}
              {resultInstagramVideos.length ? (
                <SelectButton
                  toggleState={() => {
                    this.setState({
                      showInstagrams: !this.state.showInstagrams,
                    });
                  }}
                  active={this.state.showInstagrams}
                  item={`${resultInstagramVideos.length} Instagram Videos`}
                />
              ) : null}
            </div>
          </Card>
          <Masonry>{resultItems}</Masonry>
        </div>
      </div>
    );
  }
}
const EventList = wantsWindowSizes(_EventList);

interface TopicPageProps {
  response: NewSearchResponse;
  videos: { items: VideoData[] };
  instagrams: { items: InstagramData[] };
  topic: Topic;
  currentLocale: string;
}

class TopicPage extends React.Component<TopicPageProps> {
  render(): React.ReactElement {
    const topic = this.props.topic as { title: string; image_url: string; description: string };
    return (
      <div>
        <Helmet title={topic.title} />
        <h2>{topic.title}</h2>
        <div style={{ float: 'left' }}>
          <img height={300} alt="" src={topic.image_url} />
        </div>
        <div style={{ float: 'right' }}>
          <SocialLinks topic={this.props.topic} />
        </div>
        <Truncate height={250}>
          <FormatText>{topic.description}</FormatText>
        </Truncate>
        <div style={{ clear: 'both' }} />
        <EventList
          response={this.props.response}
          videos={this.props.videos}
          instagrams={this.props.instagrams}
        />
      </div>
    );
  }
}

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TopicPage);
