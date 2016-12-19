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
  formatDuration,
} from 'dancedeets-common/js/tutorials/format';
import messages from 'dancedeets-common/js/tutorials/messages';
import {
  Card,
  HorizontalCenter,
  Link,
} from './ui';

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
        <HorizontalCenter>
          <img width="320" height="180" src={tutorial.thumbnail} role="presentation" />
        </HorizontalCenter>
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

  render() {
    const matching = getTutorials(this.props.intl.locale).filter(category => category.style.id === this.props.style);

    if (matching.length) {
      const category = matching[0];

      const tutorials = category.tutorials.map(tutorial => (
        <a
          key={tutorial.title}
          style={{ float: 'left' }}
          href={`/tutorials/${tutorial.getId()}/`}
        >
          <Tutorial tutorial={tutorial} />
        </a>
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
