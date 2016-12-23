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
import Helmet from 'react-helmet';
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
  ShareLinks,
  wantsWindowSizes,
} from './ui';
import type {
  windowProps,
} from './ui';
import { generateMetaTags } from './meta';

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

class _TutorialView extends React.Component {
  props: {
    tutorial: Playlist;
    videoIndex: ?number;

    // Self-managed props
    intl: intlShape;
    window: windowProps;
  };

  state: {
    video: Video;
  }

  _youtube: YouTube;

  constructor(props) {
    super(props);

    // Unfortunately, sticking this code into the constructor directly,
    // triggers a different initial render() than on the server,
    // which triggers invalid checksums and a full react clientside re-render.
    //
    // I can try to avoid it, by doing it on a subsequent render,
    // but I have the same problem with the selected-videoIndex,
    // which triggers a different row highlight than was presupposed by the server.
    //
    // But I'd prefer to have a fast-loading initial page, so instead,
    // I give up and just accept these dev-mode-only warnings:
    // 'React attempted to reuse markup in a container but the checksum was invalid.''

    this.state = {
      video: this.props.tutorial.getVideo(this.props.videoIndex || 0),
    };
    (this: any).onVideoEnd = this.onVideoEnd.bind(this);
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

      window.mixpanel.track('Tutorial Video Selected', {
        tutorialName: this.props.tutorial.title,
        tutorialStyle: this.props.tutorial.style,
        tutorialVideoIndex: videoIndex,
      });
    }
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
    const subline = `${tutorial.author} - ${duration}`;
    return (<div style={{ padding: 7, backgroundColor: purpleColors[4] }}>
      <h3 style={{ marginTop: 0 }}>{tutorial.title}</h3>
      {subtitle}
      <div>{subline}</div>
      <ShareLinks url={tutorial.getUrl()} />
    </div>);
  }

  renderPlayer() {
    let extraStyles = {};
    const video = this.state.video;
    if (this.props.window) {
      extraStyles = {
        maxWidth: (this.props.window.height * video.width) / video.height,
        maxHeight: (this.props.window.width * video.height) / video.width,
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
    const flexDirection = this.props.window && this.props.window.width > 1024 ? 'row' : 'column';
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
const TutorialView = wantsWindowSizes(injectIntl(_TutorialView));

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

class HtmlHead extends React.Component {
  props: {
    tutorial: ?Playlist;
    videoIndex: ?number;
  }

  render() {
    const tutorial = this.props.tutorial;
    let title = 'Unknown tutorial';
    let metaTags = [];
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

class _TutorialPage extends React.Component {
  props: {
    style: string;
    tutorial: string;
    hashLocation: string;

    // Self-managed props
    intl: intlShape;
  };

  trackTutorial(tutorial) {
    if (!window.sentMixpanelPing) {
      window.sentMixpanelPing = true;
      window.mixpanel.track('Tutorial Selected', {
        tutorialName: tutorial.title,
        tutorialStyle: tutorial.style,
      });
    }
  }

  render() {
    const config = getTutorials(this.props.intl.locale);
    const tutorial = findTutorialById(config, this.props.tutorial);

    let result = null;
    const videoIndex = this.props.hashLocation ? parseInt(this.props.hashLocation, 10) : null;
    if (tutorial) {
      this.trackTutorial(tutorial);
      result = (<TutorialView
        style={this.props.style}
        tutorial={tutorial}
        videoIndex={videoIndex}
      />);
    } else {
      result = <div>Unknown tutorial!</div>;
    }
    return <div><HtmlHead tutorial={tutorial} videoIndex={videoIndex} />{result}</div>;
  }
}

const TutorialPage = injectIntl(_TutorialPage);

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TutorialPage);
