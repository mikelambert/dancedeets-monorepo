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

class _TutorialView extends React.Component {
  props: {
    tutorial: any;

    // Self-managed props
    intl: intlShape;
  }

  renderSectionHeader(section) {
    const duration = formatDuration(this.props.intl.formatMessage, section.getDurationSeconds());
    return (
      <div>
        <div>{section.title}</div>
        <div>{duration}</div>
      </div>
    );
  }

  renderVideoLine(video) {
    const duration = formatDuration(this.props.intl.formatMessage, video.getDurationSeconds());
    return (
      <div>
        <img src="play" alt="Play" />
        <span>
          <span>{video.title}</span>
          <span>{duration}</span>
        </span>
      </div>
    );
  }

  renderSection(section) {
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
    return (<div>
      <div>{tutorial.title}</div>
      {subtitle}
      <div>{tutorial.author} - {duration}</div>
    </div>);
  }

  render() {
    const tutorial = this.props.tutorial;
    return (
      <div>
        <YouTube />
        {this.renderHeader()}
        {this.props.tutorial.sections.map((section, index) =>
          <div key={index}>{this.renderSection(section)}</div>
        )}
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
  }

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
