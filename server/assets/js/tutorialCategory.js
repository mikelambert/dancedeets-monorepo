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
// TODO: Can/should we trim this file? It is 150KB, and we probably only need 10KB of it...
import languages from 'dancedeets-common/js/languages';
import {
  Card,
  Link,
} from './ui';
import {
  generateUniformState,
  MultiSelectList,
  MultiSelectState,
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

type ValidKey = 'languages' | 'styles';

type StringWithFrequency = {
  name: string;
  count: string;
};

class _FilterBar extends React.Component {
  props: {
    initialLanguages: Array<StringWithFrequency>;
    initialStyles: Array<StringWithFrequency>;
    languages: MultiSelectState;
    styles: MultiSelectState;
    onChange: (key: ValidKey, newState: any) => void;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    return (
      <div>
        <div>
          Language:
          <MultiSelectList
            list={this.props.initialLanguages.map(x => `${languages[this.props.intl.locale][x.name]} (${x.count})`)}
            selected={this.props.languages}
            // ref={(x) => { this._styles = x; }}
            onChange={state => this.props.onChange('languages', state)}
          />
        </div>
        <div>
          Styles:
          <MultiSelectList
            list={this.props.initialStyles.map(x => `${x.name} (${x.count})`)}
            selected={this.props.styles}
            // ref={(x) => { this._styles = x; }}
            onChange={state => this.props.onChange('styles', state)}
          />
        </div>
      </div>
    );
  }
}
const FilterBar = injectIntl(_FilterBar);

class TutorialLayout extends React.Component {
  props: {
    categories: Array<Category>;
  }

  state: {
    languages: MultiSelectState;
    styles: MultiSelectState;
    keywords: string;
  }

  _tutorials: Array<Playlist>;
  _languages: Array<StringWithFrequency>;
  _styles: Array<StringWithFrequency>;

  constructor(props) {
    super(props);

    this._tutorials = [].concat(...this.props.categories.map(x => x.tutorials));
    this._languages = this.generateOrderedList(x => x.language);
    this._styles = this.generateOrderedList(x => x.style);

    this.state = {
      languages: generateUniformState(this._languages, true),
      styles: generateUniformState(this._styles, true),
      keywords: '',
    };

    (this: any).onChange = this.onChange.bind(this);
  }

  onChange(key: ValidKey, state: any) {
    this.setState({ [key]: state });
  }

  generateOrderedList(getProperty: (tutorial: Playlist) => any) {
    const frequencies = countBy(this._tutorials.map(x => getProperty(x)));
    const dataList = Object.keys(frequencies).map(name => ({ name, count: frequencies[name] }));
    return sortNumber(dataList, x => -x.count);
  }

  render() {
    const tutorialComponents = this._tutorials.map(tutorial => <Tutorial key={tutorial.getId()} tutorial={tutorial} />);
    const title = this.props.categories.length === 1 ? `${this.props.categories[0].style.title} Tutorials` : 'Tutorials';

    return (
      <div>
        <Helmet title={title} />
        <FilterBar
          initialLanguages={this._languages} languages={this.state.languages}
          initialStyles={this._styles} styles={this.state.styles}
          onChange={this.onChange}
        />
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
