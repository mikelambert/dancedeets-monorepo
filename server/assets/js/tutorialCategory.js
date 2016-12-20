/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import uniq from 'lodash/uniq';
import countBy from 'lodash/countBy';
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
import { sortNumber } from 'dancedeets-common/js/util/sort';
import {
  Card,
  Link,
} from './ui';
import {
  MultiSelectList,
} from './MultiSelectList';

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
      <Card
        style={{ float: 'left' }}
      >
        <a
          href={`/tutorials/${tutorial.getId()}`}
        >
          <img
            width="320" height="180"
            src={tutorial.thumbnail} role="presentation"
            style={{ display: 'block', marginLeft: 'auto', marginRight: 'auto' }}
          />
          <div>{tutorial.title}</div>
          <div>{numVideosDuration}</div>
        </a>
      </Card>
    );
  }
}
const Tutorial = injectIntl(_Tutorial);

class FilterBar extends React.Component {
  props: {
    tutorials: Array<Playlist>;
  }

  generateOrderedList(getProperty: (tutorial: Playlist) => any) {
    const frequencies = countBy(this.props.tutorials.map(x => getProperty(x)));
    const dataList = Object.keys(frequencies).map(name => ({ name, count: frequencies[name] }));
    return sortNumber(dataList, x => -x.count);
  }

  render() {
    const tutorials = this.props.tutorials;
    const languages = this.generateOrderedList(x => x.language);
    const styles = this.generateOrderedList(x => x.style);
    return (
      <div>
        <div>
          Language:
          <MultiSelectList
            list={languages.map(x => `${x.name} (${x.count})`)}
            selected={[]}
            // ref={(x) => { this._styles = x; }}
            // onChange={state => this.props.onChange('styles', state)}
          />
        </div>
        <div>
          Styles:
          <MultiSelectList
            list={styles.map(x => `${x.name} (${x.count})`)}
            selected={[]}
            // ref={(x) => { this._styles = x; }}
            // onChange={state => this.props.onChange('styles', state)}
          />
        </div>
      </div>
    );
  }
}

class TutorialLayout extends React.Component {
  props: {
    categories: Array<Category>;
  }

  render() {
    const tutorials = [].concat(...this.props.categories.map(x => x.tutorials));
    const tutorialComponents = tutorials.map(tutorial => <Tutorial key={tutorial.getId()} tutorial={tutorial} />);
    const title = this.props.categories.length === 1 ? `${this.props.categories[0].style.title} Tutorials` : 'Tutorials';
    return (
      <div>
        <Helmet title={title} />
        <FilterBar tutorials={tutorials} />
        <h2>{title}</h2>
        {tutorialComponents}
        <div style={{ clear: 'both' }} />
      </div>
    );
  }
}

class _TutorialOverview extends React.Component {
  props: {
    style: string;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const categories = getTutorials(this.props.intl.locale);
    if (this.props.style) {
      const matching = categories.filter(category => category.style.id === this.props.style);
      const category = matching.length ? matching[0] : null;
      if (category) {
        return <TutorialLayout categories={[category]} />;
      } else {
        // 404 not found
        return <div><Helmet title="Unknown Tutorial Category" />Unknown Style!</div>;
      }
    } else {
      // Super overiew
      return <TutorialLayout categories={categories} />;
    }
  }
}
const TutorialOverview = injectIntl(_TutorialOverview);

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TutorialOverview);
