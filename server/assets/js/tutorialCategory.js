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
import Helmet from 'react-helmet';
import upperFirst from 'lodash/upperFirst';
import {
  intlWeb,
} from 'dancedeets-common/js/intl';
import {
  getTutorials,
} from 'dancedeets-common/js/tutorials/playlistConfig';
import type {
  Category,
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
        <img
          width="320" height="180"
          src={tutorial.thumbnail} role="presentation"
          style={{ display: 'block', marginLeft: 'auto', marginRight: 'auto' }}
        />
        <div>{tutorial.title}</div>
        <div>{numVideosDuration}</div>
      </Card>
    );
  }
}
const Tutorial = injectIntl(_Tutorial);

class HtmlHead extends React.Component {
  props: {
    category: ?Category;
  }

  render() {
    const category = this.props.category;
    return <Helmet title={category ? `${category.style.title} Tutorials` : 'Unknown Style'} />;
  }
}

class _TutorialCategory extends React.Component {
  props: {
    style: string;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const matching = getTutorials(this.props.intl.locale).filter(category => category.style.id === this.props.style);
    let result = null;
    const category = matching.length ? matching[0] : null;
    if (category) {
      const tutorials = category.tutorials.map(tutorial => (
        <a
          key={tutorial.title}
          style={{ float: 'left' }}
          href={`/tutorials/${tutorial.getId()}/`}
        >
          <Tutorial tutorial={tutorial} />
        </a>
      ));
      result = (
        <div>
          <h2>{category.style.title}</h2>
          {tutorials}
          <div style={{ clear: 'both' }} />
        </div>
      );
    } else {
      result = <div>Unknown Style!</div>;
    }
    return <div><HtmlHead category={category} />{result}</div>;
  }
}
const TutorialCategory = injectIntl(_TutorialCategory);

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TutorialCategory);
