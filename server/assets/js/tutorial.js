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
  formatDuration,
} from 'dancedeets-common/js/tutorials/format';
import {
  Card,
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

class _TutorialView extends React.Component {
  props: {
    tutorial: any;

    // Self-managed props
    intl: intlShape;
  };

  state: {
    videoId: string;
  }

  _youtube: YouTube;

  constructor(props) {
    super(props);
    this.state = {
      videoId: this.props.tutorial.sections[0].videos[0].youtubeId,
    };
  }

  renderVideoLine(video) {
    const duration = formatDuration(this.props.intl.formatMessage, video.getDurationSeconds());
    return (
      <div style={{ backgroundColor: purpleColors[3] }}>
        <img
          style={{
            float: 'left',
            verticalAlign: 'baseline',
          }}
          width={30} height={30} src="play" alt="Play"
        />
        <div>
          <div>{video.title}</div>
          <div>{duration}</div>
        </div>
      </div>
    );
  }

  renderSectionHeader(section) {
    const duration = formatDuration(this.props.intl.formatMessage, section.getDurationSeconds());
    return (
      <div style={{ backgroundColor: purpleColors[4] }}>
        <div>{section.title}</div>
        <div>{duration}</div>
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
    return (<div style={{ backgroundColor: purpleColors[4] }}>
      <h3 style={{ marginTop: 0 }}>{tutorial.title}</h3>
      {subtitle}
      <div>{tutorial.author} - {duration}</div>
    </div>);
  }

  render() {
    const tutorial = this.props.tutorial;
    return (
      <Card style={{ maxWidth: 660 }}>
        <YouTube
          ref={(x) => { this._youtube = x; }}
          opts={{
            width: '100%',
          }}
          videoId={this.state.videoId}
        />
        <div>
          {this.renderHeader()}
          {this.props.tutorial.sections.map((section, index) =>
            <div key={index}>{this.renderWholeSection(section)}</div>
          )}
        </div>
      </Card>
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
      console.log(this.props.tutorial);
      const tutorial = category.tutorials[parseInt(this.props.tutorial, 10)];
      return <TutorialView style={this.props.style} tutorial={tutorial} />;
    } else {
      return <div>Unknown style!</div>;
    }
  }
}
const TutorialPage = injectIntl(_TutorialPage);

export default intlWeb(TutorialPage);
