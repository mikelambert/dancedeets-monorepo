/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import uniq from 'lodash/uniq';
import countBy from 'lodash/countBy';
import includes from 'lodash/includes';
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
import { messages as styleMessages } from 'dancedeets-common/js/styles';
import {
  Card,
  Link,
} from './ui';
import {
  getSelected,
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

type ValidKey = 'languages' | 'categories';

type StringWithFrequency = string;

class _FilterBar extends React.Component {
  props: {
    initialLanguages: Array<StringWithFrequency>;
    initialCategories: Array<StringWithFrequency>;
    languages: MultiSelectState;
    categories: MultiSelectState;
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
            list={this.props.initialLanguages}
            selected={this.props.languages}
            // ref={(x) => { this._styles = x; }}
            onChange={state => this.props.onChange('languages', state)}
            itemRenderer={(data) => {
              const x = JSON.parse(data);
              return `${languages[this.props.intl.locale][x.name]} (${x.count})`;
            }}
          />
        </div>
        <div>
          Styles:
          <MultiSelectList
            list={this.props.initialCategories}
            selected={this.props.categories}
            // ref={(x) => { this._styles = x; }}
            onChange={state => this.props.onChange('categories', state)}
            itemRenderer={(data) => {
              const x = JSON.parse(data);
              return `${this.props.intl.formatMessage(styleMessages[x.name])} (${x.count})`;
            }}
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
    categories: MultiSelectState;
    keywords: string;
  }

  _tutorials: Array<Playlist>;
  _languages: Array<StringWithFrequency>;
  _categories: Array<StringWithFrequency>;

  constructor(props) {
    super(props);

    this._languages = this.generateOrderedList(x => x.language).map(x => JSON.stringify(x));
    this._categories = this.props.categories.map(x => ({
      name: x.style.id,
      count: x.tutorials.length,
    })).map(x => JSON.stringify(x));

    this.state = {
      languages: generateUniformState(this._languages, true),
      categories: generateUniformState(this._categories, true),
      keywords: '',
    };

    (this: any).onChange = this.onChange.bind(this);
  }

  onChange(key: ValidKey, state: any) {
    this.setState({ [key]: state });
  }

  generateOrderedList(getProperty: (tutorial: Playlist) => any) {
    const tutorials = [].concat(...this.props.categories.map(x => x.tutorials));
    const frequencies = countBy(tutorials.map(x => getProperty(x)));
    const dataList = Object.keys(frequencies).map(name => ({ name, count: frequencies[name] }));
    return sortNumber(dataList, x => -x.count);
  }

  render() {
    // Filter based on the 'categories'
    const selectedCategoryNames = getSelected(this.state.categories).map(x => JSON.parse(x).name);
    const selectedCategories = this.props.categories.filter(x => includes(selectedCategoryNames, x.style.id));
    const tutorials = [].concat(...selectedCategories.map(x => x.tutorials));

    // Filter based on the 'languages'
    const filteredTutorials = tutorials.filter((tutorial) => {
      if (getSelected(this.state.languages).filter(language => JSON.parse(language).name === tutorial.language).length === 0) {
        return false;
      }
      return true;
    });

    // Now let's render them
    const tutorialComponents = filteredTutorials.map(tutorial => <Tutorial key={tutorial.getId()} tutorial={tutorial} />);
    const title = this.props.categories.length === 1 ? `${this.props.categories[0].style.title} Tutorials` : 'Tutorials';

    return (
      <div>
        <Helmet title={title} />
        <FilterBar
          initialLanguages={this._languages} languages={this.state.languages}
          initialCategories={this._categories} categories={this.state.categories}
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
