/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  injectIntl,
  intlShape,
} from 'react-intl';
import YouTube from 'react-youtube';
import { Share as TwitterShare } from 'react-twitter-widgets';
import {
  intlWeb,
} from 'dancedeets-common/js/intl';
import {
  getTutorials,
} from 'dancedeets-common/js/tutorials/playlistConfig';
import {
  Playlist,
  Video,
} from 'dancedeets-common/js/tutorials/models';
import {
  formatDuration,
} from 'dancedeets-common/js/tutorials/format';
import {
  Card,
  Link,
} from './ui';

// De-Dupe
const purpleColors = [
  '#8283A9',
  '#656595',
  '#4C4D81',
  '#333452',
  '#222238',
  '#171728',
];
const lightPurpleColors = [
  '#E0E0F5',
  '#D0D0F0',
  '#C0C0D0',
];


class _Duration extends React.Component {
  props: {
    duration: number;

    // Self-managed props:
    intl: intlShape;
  }

  render() {
    const duration = formatDuration(this.props.intl.formatMessage, this.props.duration);
    return (
      <div
        style={{
          color: '#ccc',
          fontSize: '80%',
        }}
      >
        {duration}
      </div>
    );
  }
}
const Duration = injectIntl(_Duration);

class ShareLinks extends React.Component {
  props: {
    url: string;
  }

  render() {
    return (
      <div style={{ height: 20 }}>
        <div style={{ display: 'inline-block' }}><TwitterShare url={this.props.url} /></div>
        <span style={{ verticalAlign: 'top' }} className="link-event-share fb-share-button" data-href={this.props.url} data-layout="button" data-size="small" data-mobile-iframe="true">
          <a className="fb-xfbml-parse-ignore" rel="noopener noreferrer" target="_blank" href={`https://www.facebook.com/sharer/sharer.php?u=${this.props.url}&amp;src=sdkpreparse`}>Share</a>
        </span>
      </div>
    );
  }
}

class _TutorialView extends React.Component {
  props: {
    tutorial: Playlist;
    videoIndex: ?number;

    // Self-managed props
    intl: intlShape;
  };

  state: {
    video: Video;
    window: ?{
      width: number;
      height: number;
    };
  }

  _youtube: YouTube;

  constructor(props) {
    super(props);
    this.state = {
      ...this.getWindowState(),
      video: this.props.tutorial.getVideo(this.props.videoIndex || 0),
    };
    (this: any).updateDimensions = this.updateDimensions.bind(this);
    (this: any).onVideoEnd = this.onVideoEnd.bind(this);
  }


  componentWillMount() {
    this.updateDimensions();
  }

  componentDidMount() {
    window.addEventListener('resize', this.updateDimensions);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.videoIndex !== this.props.videoIndex) {
      const video = this.props.tutorial.getVideo(nextProps.videoIndex || 0);
      this.setState({ video });
    }
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.video !== this.state.video) {
      const videoIndex = this.props.tutorial.getVideoIndex(this.state.video);
      const oldHash = window.location.hash || '#0';
      const newHash = `#${videoIndex}`;
      if (oldHash !== newHash) {
        window.location.hash = newHash;
      }
    }
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.updateDimensions);
  }

  onVideoClick(video) {
    this.setState({ video });
  }

  onVideoEnd() {
    const videoIndex = this.props.tutorial.getVideoIndex(this.state.video) + 1;
    if (videoIndex < this.props.tutorial.getVideoCount()) {
      const video = this.props.tutorial.getVideo(videoIndex);
      this.setState({ video });
    }
  }

  getWindowState() {
    if (global.window != null) {
      const width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
      const height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
      return { window: { width, height } };
    } else {
      return { window: null };
    }
  }

  updateDimensions() {
    this.setState(this.getWindowState());
  }

  renderVideoLine(video) {
    const activeRow = this.state.video.youtubeId === video.youtubeId;
    const backgroundColor = activeRow ? purpleColors[0] : purpleColors[3];
    const imageSize = 30;
    const playIcon = require('../img/play.png'); // eslint-disable-line global-require
    return (
      <Link
        onClick={() => this.onVideoClick(video)}
        style={{
          backgroundColor,

          // Do left-to-right with vertical centering
          display: 'flex',
          alignItems: 'center',

          padding: 7,

          borderBottomWidth: 0.5,
          borderBottomStyle: 'solid',
          borderBottomColor: purpleColors[4],
        }}
      >
        <div >
          <img
            style={{
              float: 'left',
              verticalAlign: 'baseline',
            }}
            width={imageSize} height={imageSize} src={playIcon} alt="Play"
          />
        </div>
        <div style={{ marginLeft: 10 }}>
          <div style={{ fontWeight: 'bold' }}>{video.title}</div>
          <Duration duration={video.getDurationSeconds()} />
        </div>
      </Link>
    );
  }

  renderSectionHeader(section) {
    return (
      <div style={{ padding: 7, backgroundColor: purpleColors[4] }}>
        <div>{section.title}</div>
        <Duration duration={section.getDurationSeconds()} />
      </div>
    );
  }

  renderWholeSection(section) {
    return (<div>
      {this.renderSectionHeader(section)}
      {section.videos.map((video, index) =>
        <div key={index}>{this.renderVideoLine(video)}</div>
      )}
    </div>);
  }

  renderHeader() {
    const tutorial = this.props.tutorial;
    const subtitle = tutorial.subtitle ? <div>{tutorial.subtitle}</div> : null;
    const duration = formatDuration(this.props.intl.formatMessage, tutorial.getDurationSeconds());
    return (<div style={{ padding: 7, backgroundColor: purpleColors[4] }}>
      <h3 style={{ marginTop: 0 }}>{tutorial.title}</h3>
      {subtitle}
      <div>{tutorial.author} - {duration}</div>
      <ShareLinks url={tutorial.getUrl()} />
    </div>);
  }

  renderPlayer() {
    let extraStyles = {};
    const video = this.state.video;
    if (this.state.window) {
      extraStyles = {
        maxWidth: (this.state.window.height * video.width) / video.height,
        maxHeight: (this.state.window.width * video.height) / video.width,
      };
    }
    return (
      <div
        style={{
          flex: 2,
          width: '100%',
          ...extraStyles,
        }}
      >
        <YouTube
          ref={(x) => { this._youtube = x; }}
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

  render() {
    const tutorial = this.props.tutorial;
    const video = this.state.video;
    const flexDirection = this.state.window && this.state.window.width > 1024 ? 'row' : 'column';
    return (
      <div
        style={{
          height: '100vh',
          display: 'flex',
          flexDirection,
        }}
      >
        {this.renderPlayer()}
        <div
          style={{
            flex: 1,
            overflow: 'scroll',
          }}
        >
          {this.renderHeader()}
          {this.props.tutorial.sections.map((section, index) =>
            <div key={index}>{this.renderWholeSection(section)}</div>
          )}
        </div>
      </div>
    );
  }
}
const TutorialView = injectIntl(_TutorialView);

function findTutorialById(config, id) {
  let foundTutorial = null;
  config.forEach((style) => {
    style.tutorials.forEach((tutorial) => {
      if (tutorial.getId() === id) {
        foundTutorial = tutorial;
      }
    });
  });
  return foundTutorial;
}

class _TutorialPage extends React.Component {
  props: {
    style: string;
    tutorial: string;
    locationComponents?: Array<string>;

    // Self-managed props
    intl: intlShape;
  };

  render() {
    const config = getTutorials(this.props.intl.locale);
    const tutorial = findTutorialById(config, this.props.tutorial);

    if (tutorial) {
      const videoIndex = this.props.locationComponents && this.props.locationComponents.length ? this.props.locationComponents[0] : null;
      return (<TutorialView
        style={this.props.style}
        tutorial={tutorial}
        videoIndex={videoIndex}
      />);
    } else {
      return <div>Unknown tutorial!</div>;
    }
  }
}
const TutorialPage = injectIntl(_TutorialPage);

export default intlWeb(TutorialPage);
