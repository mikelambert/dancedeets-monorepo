/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  defineMessages,
  injectIntl,
  intlShape,
} from 'react-intl';
import upperFirst from 'lodash/upperFirst';
import {
  intlWeb,
} from 'dancedeets-common/js/intl';
import {
  getTutorials,
} from 'dancedeets-common/js/tutorials/playlistConfig';
import {
  Playlist,
} from 'dancedeets-common/js/tutorials/models';
import {
  Card,
} from './ui';

// De-Dupe
const messages = defineMessages({
  numVideosWithDuration: {
    id: 'tutorialVideos.numVideosWithDuration',
    defaultMessage: '{count,number} videos: {duration}',
    description: 'Total for all videos in a tutorial',
  },
  timeHoursMinutes: {
    id: 'tutorialVideos.timeHoursMinutes',
    defaultMessage: '{hours,number}h {minutes,number}m',
    description: 'Time formatting',
  },
  timeMinutes: {
    id: 'tutorialVideos.timeMinutes',
    defaultMessage: '{minutes,number}m',
    description: 'Time formatting',
  },
  timeSeconds: {
    id: 'tutorialVideos.timeSeconds',
    defaultMessage: '{seconds,number}s',
    description: 'Time formatting',
  },
});

// De-Dupe
function formatDuration(formatMessage: (message: Object, timeData: Object) => string, durationSeconds: number) {
  const hours = Math.floor(durationSeconds / 60 / 60);
  const minutes = Math.floor(durationSeconds / 60) % 60;
  if (durationSeconds > 60 * 60) {
    return formatMessage(messages.timeHoursMinutes, { hours, minutes });
  } else if (durationSeconds > 60) {
    return formatMessage(messages.timeMinutes, { minutes });
  } else {
    const seconds = durationSeconds;
    return formatMessage(messages.timeSeconds, { seconds });
  }
}

class _Tutorial extends React.Component {
  props: {
    tutorial: Playlist;

    // Self-managed-props
    intl: intlShape;
  }

  render() {
    // De-Dupe
    const tutorial = this.props.tutorial;
    const duration = formatDuration(this.props.intl.formatMessage, tutorial.getDurationSeconds());

    const title = tutorial.title;
    if (this.props.intl.locale !== tutorial.language) {
      // const localizedLanguage = languages[this.props.intl.locale][tutorial.language];
      // title = this.props.intl.formatMessage(messages.languagePrefixedTitle, { language: upperFirst(localizedLanguage), title: tutorial.title });
    }
    const numVideosDuration = this.props.intl.formatMessage(messages.numVideosWithDuration, { count: tutorial.getVideoCount(), duration });

    return (
      <Card>
        <img src={tutorial.thumbnail} role="presentation" />
        <div>{tutorial.title}</div>
        <div>{numVideosDuration}</div>
      </Card>
    );
  }
}
const Tutorial = injectIntl(_Tutorial);

class _TutorialCategory extends React.Component {
  props: {
    style: string;

    // Self-managed props
    intl: intlShape;
  }

  state: {
    tutorials: Array<{
      style: Object,
      tutorials: Array<Object>,
    }>;
  }

  constructor(props) {
    super(props);
    this.state = {
      tutorials: getTutorials(this.props.intl.locale),
    };
  }

  render() {
    const matching = this.state.tutorials.filter(category => category.style.id === this.props.style);

    if (matching) {
      const category = matching[0];

      const tutorials = category.tutorials.map(tutorial => (
        <div
          key={tutorial.title}
          style={{ float: 'left' }}
        >
          <Tutorial tutorial={tutorial} />
        </div>
      ));
      return (
        <div>
          <h2>{category.style.title}</h2>
          {tutorials}
          <div style={{ clear: 'both' }} />
        </div>
      );
    }
    return <div>Unknown Style!</div>;
  }
}
const TutorialCategory = injectIntl(_TutorialCategory);

export default intlWeb(TutorialCategory);
