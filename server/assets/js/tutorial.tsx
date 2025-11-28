/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { injectIntl, InjectedIntlProps } from 'react-intl';
import YouTube from 'react-youtube';
import Helmet from 'react-helmet';
import ExecutionEnvironment from 'exenv';
import { intlWeb } from 'dancedeets-common/js/intl';
import { getTutorials } from 'dancedeets-common/js/tutorials/playlistConfig';
import { Playlist, Video } from 'dancedeets-common/js/tutorials/models';
import { formatDuration } from 'dancedeets-common/js/tutorials/format';
import { Link, ShareLinks, wantsWindowSizes } from './ui';
import type { WindowProps } from './ui';
import { generateMetaTags } from './meta';

const backgroundPlaylistHeaderColor = 'white';
const backgroundSectionHeaderColor = '#656595';
const backgroundVideoColor = 'white';
const backgroundVideoColorActive = '#E0E0F5';

// Calculate header height dynamically to account for navbar + promo messages
const getHeaderHeight = (): number => {
  if (typeof document === 'undefined') return 50;
  const navbar = document.querySelector('.navbar');
  const promoMessages = document.querySelector('.alert.alert-info');
  let height = 0;
  if (navbar) height += (navbar as HTMLElement).offsetHeight;
  if (promoMessages) height += (promoMessages as HTMLElement).offsetHeight;
  return height || 50;
};

interface DurationProps {
  duration: number;
  style?: React.CSSProperties;
}

type DurationPropsWithIntl = DurationProps & InjectedIntlProps;

class _Duration extends React.Component<DurationPropsWithIntl> {
  render(): React.ReactElement {
    const duration = formatDuration(
      this.props.intl.formatMessage,
      this.props.duration
    );
    return (
      <div
        style={{
          fontSize: '80%',
          ...this.props.style,
        }}
      >
        {duration}
      </div>
    );
  }
}
const Duration = injectIntl(_Duration);

interface TutorialViewProps {
  tutorial: Playlist;
  videoIndex: number | null;
  window: WindowProps;
}

type TutorialViewPropsWithIntl = TutorialViewProps & InjectedIntlProps;

interface TutorialViewState {
  video: Video;
}

class _TutorialView extends React.Component<TutorialViewPropsWithIntl, TutorialViewState> {
  _youtube: YouTube | null = null;

  constructor(props: TutorialViewPropsWithIntl) {
    super(props);

    this.state = {
      video: this.props.tutorial.getVideo(this.props.videoIndex || 0),
    };
    this.onVideoEnd = this.onVideoEnd.bind(this);
  }

  componentDidUpdate(prevProps: TutorialViewProps, prevState: TutorialViewState): void {
    if (this.props.videoIndex !== prevProps.videoIndex) {
      const video = this.props.tutorial.getVideo(this.props.videoIndex || 0);
      this.setState({ video });
    }

    if (prevState.video !== this.state.video) {
      const videoIndex = this.props.tutorial.getVideoIndex(this.state.video);
      const oldHash = window.location.hash || '#0';
      const newHash = `#${videoIndex}`;
      if (oldHash !== newHash) {
        window.location.hash = newHash;
      }

      window.mixpanel?.track('Tutorial Video Selected', {
        tutorialName: this.props.tutorial.title,
        tutorialStyle: this.props.tutorial.style,
        tutorialVideoIndex: videoIndex,
      });
    }
  }

  onVideoClick(video: Video): void {
    this.setState({ video });
  }

  onVideoEnd(): void {
    const videoIndex = this.props.tutorial.getVideoIndex(this.state.video) + 1;
    if (videoIndex < this.props.tutorial.getVideoCount()) {
      const video = this.props.tutorial.getVideo(videoIndex);
      this.setState({ video });
    }
  }

  renderVideoLine(video: Video): React.ReactElement {
    const activeRow = this.state.video.youtubeId === video.youtubeId;
    const backgroundColor = activeRow
      ? backgroundVideoColorActive
      : backgroundVideoColor;

    return (
      <Link
        onClick={() => this.onVideoClick(video)}
        style={{
          backgroundColor,
          display: 'flex',
          alignItems: 'center',
          padding: 7,
          borderBottomWidth: 0.5,
          borderBottomStyle: 'solid',
          borderBottomColor: backgroundSectionHeaderColor,
        }}
      >
        <div>
          <i
            className="fa fa-play-circle"
            aria-hidden="true"
            style={{ fontSize: '200%' }}
          />
        </div>
        <div style={{ marginLeft: 10 }}>
          <div style={{ fontWeight: 'bold' }}>{video.title}</div>
          <Duration
            duration={video.getDurationSeconds()}
            style={{ color: '#777' }}
          />
        </div>
      </Link>
    );
  }

  renderSectionHeader(section: { title: string; getDurationSeconds: () => number }): React.ReactElement {
    return (
      <div
        style={{
          color: 'white',
          padding: 7,
          backgroundColor: backgroundSectionHeaderColor,
        }}
      >
        <div>{section.title}</div>
        <Duration duration={section.getDurationSeconds()} />
      </div>
    );
  }

  renderWholeSection(section: { title: string; videos: Video[]; getDurationSeconds: () => number }): React.ReactElement {
    return (
      <div>
        {this.renderSectionHeader(section)}
        {section.videos.map((video) => (
          <div key={video.youtubeId}>{this.renderVideoLine(video)}</div>
        ))}
      </div>
    );
  }

  renderHeader(): React.ReactElement {
    const { tutorial } = this.props;
    const subtitle = tutorial.subtitle ? <div>{tutorial.subtitle}</div> : null;
    const duration = formatDuration(
      this.props.intl.formatMessage,
      tutorial.getDurationSeconds()
    );
    const subline = `${tutorial.author} - ${duration}`;
    return (
      <div
        style={{ padding: 7, backgroundColor: backgroundPlaylistHeaderColor }}
      >
        <h3 style={{ marginTop: 0 }}>
          {tutorial.title} - <a href="/tutorials">See All Tutorials</a>
        </h3>
        {subtitle}
        <div>{subline}</div>
        <ShareLinks url={tutorial.getUrl()} />
      </div>
    );
  }

  renderPlayer(): React.ReactElement {
    const { video } = this.state;

    return (
      <div
        className="video-player-container"
        style={{
          flex: 2,
          width: '100%',
          height: '100%',
          backgroundColor: '#000',
        }}
      >
        <YouTube
          ref={x => {
            this._youtube = x;
          }}
          opts={{
            width: '100%',
            height: '100%',
            playerVars: {
              autoplay: 1,
            },
          }}
          videoId={video.youtubeId}
          onEnd={this.onVideoEnd}
        />
      </div>
    );
  }

  render(): React.ReactElement {
    const height = this.props.window
      ? this.props.window.height - getHeaderHeight()
      : '100vh';
    return (
      <div
        className="media-width-row-or-column"
        style={{
          display: 'flex',
          height,
        }}
      >
        {this.renderPlayer()}
        <div
          style={{
            flex: 1,
            overflow: 'auto',
            minHeight: 0,
            minWidth: 0,
          }}
        >
          {this.renderHeader()}
          {this.props.tutorial.sections.map((section) => (
            <div key={section.title}>{this.renderWholeSection(section)}</div>
          ))}
        </div>
      </div>
    );
  }
}
const TutorialView = wantsWindowSizes(injectIntl(_TutorialView));

interface StyleConfig {
  tutorials: Playlist[];
}

function findTutorialById(config: StyleConfig[], id: string): Playlist | null {
  let foundTutorial: Playlist | null = null;
  config.forEach(style => {
    style.tutorials.forEach(tutorial => {
      if (tutorial.getId() === id) {
        foundTutorial = tutorial;
      }
    });
  });
  return foundTutorial;
}

interface HtmlHeadProps {
  tutorial: Playlist | null;
  videoIndex: number | null;
}

class HtmlHead extends React.Component<HtmlHeadProps> {
  render(): React.ReactElement {
    const { tutorial } = this.props;
    let title = 'Unknown tutorial';
    let metaTags: Array<{ property?: string; name?: string; content: string }> = [];
    if (tutorial) {
      title = tutorial.title;
      if (this.props.videoIndex != null) {
        const video = tutorial.getVideo(this.props.videoIndex);
        title += `: ${video.title}`;
      }
      title += ' | DanceDeets Tutorial';

      metaTags = generateMetaTags(title, tutorial.getUrl(), tutorial.thumbnail);
    }

    return <Helmet title={title} meta={metaTags} />;
  }
}

interface TutorialPageProps {
  style: string;
  tutorial: string;
  hashLocation: string;
  intl: { locale: string; formatMessage: (msg: unknown) => string };
}

class _TutorialPage extends React.Component<TutorialPageProps> {
  trackTutorial(tutorial: Playlist): void {
    if (!ExecutionEnvironment.canUseDOM) {
      return;
    }
    if (!(global as unknown as { window: Window & { sentMixpanelPing?: boolean } }).window.sentMixpanelPing) {
      window.sentMixpanelPing = true;
      window.mixpanel?.track('Tutorial Selected', {
        tutorialName: tutorial.title,
        tutorialStyle: tutorial.style,
      });
    }
  }

  render(): React.ReactElement {
    const config = getTutorials(this.props.intl.locale);
    const tutorial = findTutorialById(config, this.props.tutorial);

    let result: React.ReactElement;
    const videoIndex = this.props.hashLocation
      ? parseInt(this.props.hashLocation, 10)
      : null;
    if (tutorial) {
      this.trackTutorial(tutorial);
      result = (
        <TutorialView
          style={this.props.style}
          tutorial={tutorial}
          videoIndex={videoIndex}
        />
      );
    } else {
      result = <div>Unknown tutorial!</div>;
    }
    return (
      <div>
        <HtmlHead tutorial={tutorial} videoIndex={videoIndex} />
        {result}
      </div>
    );
  }
}

const TutorialPage = injectIntl(_TutorialPage);

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TutorialPage);

// Window extensions
declare global {
  interface Window {
    sentMixpanelPing?: boolean;
  }
}
