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
import {
  intlWeb,
} from 'dancedeets-common/js/intl';
import {
  getTutorials,
} from 'dancedeets-common/js/tutorials/playlistConfig';
import {
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

class _TutorialView extends React.Component {
  props: {
    tutorial: any;

    // Self-managed props
    intl: intlShape;
  };

  state: {
    video: Video;
    windowWidth: number;
    windowHeight: number;
  }

  _youtube: YouTube;

  constructor(props) {
    super(props);
    this.state = {
      ...this.getWindowState(),
      video: this.props.tutorial.sections[0].videos[0],
    };
    (this: any).updateDimensions = this.updateDimensions.bind(this);
  }


  componentWillMount() {
    this.updateDimensions();
  }

  componentDidMount() {
    window.addEventListener('resize', this.updateDimensions);
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.updateDimensions);
  }

  onVideoClick(video) {
    this.setState({ video });
  }

  getWindowState() {
    const windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    const windowWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    return { windowWidth, windowHeight };
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
    </div>);
  }

  render() {
    const tutorial = this.props.tutorial;
    const video = this.state.video;
    const flexDirection = this.state.windowWidth > 1024 ? 'row' : 'column';
    return (
      <div
        style={{
          height: '100vh',
          display: 'flex',
          flexDirection,
        }}
      >
        <div
          style={{
            flex: 2,
            width: '100%',
            maxWidth: (this.state.windowHeight * video.width) / video.height,
            maxHeight: (this.state.windowWidth * video.height) / video.width,
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
          />
        </div>
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

class _TutorialPage extends React.Component {
  props: {
    style: string;
    tutorial: string;

    // Self-managed props
    intl: intlShape;
  };

  render() {
    const matching = getTutorials(this.props.intl.locale).filter(category => category.style.id === this.props.style);

    if (matching.length) {
      const category = matching[0];
      const tutorial = category.tutorials[parseInt(this.props.tutorial, 10)];
      return <TutorialView style={this.props.style} tutorial={tutorial} />;
    } else {
      return <div>Unknown style!</div>;
    }
  }
}
const TutorialPage = injectIntl(_TutorialPage);

export default intlWeb(TutorialPage);
