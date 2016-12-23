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
import querystring from 'querystring';
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
  Section,
  Video,
} from 'dancedeets-common/js/tutorials/models';
import {
  formatDuration,
} from 'dancedeets-common/js/tutorials/format';
import messages from 'dancedeets-common/js/tutorials/messages';
import { sortNumber } from 'dancedeets-common/js/util/sort';
// TODO: Can/should we trim this file? It is 150KB, and we probably only need 10KB of it...
import languageData from 'dancedeets-common/js/languages';
import { messages as styleMessages } from 'dancedeets-common/js/styles';
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
import {
  getSelected,
  generateUniformState,
  isAllSelected,
  MultiSelectList,
  MultiSelectState,
} from './MultiSelectList';

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

class MatchedVideo extends React.Component {
  props: {
    tutorial: Playlist;
    video: Video;
  }

  render() {
    const tutorialUrl = this.props.tutorial.getUrl();
    const videoIndex = this.props.tutorial.getVideoIndex(this.props.video);
    const url = `${tutorialUrl}#${videoIndex}`;
    return (
      <div
        style={{
          backgroundColor: purpleColors[1],

          paddingLeft: 15,
          borderBottomWidth: 0.5,
          borderBottomStyle: 'solid',
          borderBottomColor: purpleColors[0],
        }}
      >
        <a href={url}>
          <div style={{ fontWeight: 'bold' }}>{this.props.video.title}</div>
        </a>
      </div>
    );
  }
}

class MatchedSection extends React.Component {
  props: {
    tutorial: Playlist;
    section: Section;
    children?: React.Element<*>;
  }

  render() {
    const tutorialUrl = this.props.tutorial.getUrl();
    const videoIndex = this.props.tutorial.getVideoIndex(this.props.section.videos[0]);
    const url = `${tutorialUrl}#${videoIndex}`;
    return (
      <div style={{ backgroundColor: purpleColors[2] }}>
        <div><a href={url}>{this.props.section.title}</a></div>
        {this.props.children}
      </div>
    );
  }
}

class _Tutorial extends React.Component {
  props: {
    tutorial: Playlist;
    searchKeywords: Array<string>;

    // Self-managed-props
    intl: intlShape;
    window: windowProps;
  }

  matchesKeywords(obj: Video | Section) {
    const text = obj.getSearchText();
    return this.props.searchKeywords.filter(x => text.indexOf(x) !== -1).length > 0;
  }

  renderMatchingVideos() {
    if (!this.props.searchKeywords.length) {
      return null;
    }
    const sections = [];
    this.props.tutorial.sections.forEach((section) => {
      const sectionVideos = [];
      section.videos.forEach((video) => {
        if (this.matchesKeywords(video)) {
          sectionVideos.push(<MatchedVideo tutorial={this.props.tutorial} video={video} />);
        }
      });
      if (sectionVideos.length || this.matchesKeywords(section)) {
        sections.push(<MatchedSection tutorial={this.props.tutorial} section={section}>{sectionVideos}</MatchedSection>);
      }
    });
    return sections;
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

    const matchingVideos = this.renderMatchingVideos();

    const margin = 2 * 10;
    let cardSize = 320 + margin;
    if (this.props.window) {
      cardSize = (this.props.window.width / Math.floor(this.props.window.width / cardSize)) - margin;
    }

    return (
      <Card style={{ width: cardSize, float: 'left', maxWidth: '100%' }}>
        <a href={`/tutorials/${tutorial.getId()}`}>
          <img
            src={tutorial.thumbnail} role="presentation"
            style={{ width: '100%', display: 'block', marginLeft: 'auto', marginRight: 'auto' }}
          />
          <div style={{ backgroundColor: purpleColors[2] }}>
            <div>{tutorial.title}</div>
            <div>{numVideosDuration}</div>
          </div>
        </a>
        {matchingVideos}
      </Card>
    );
  }
}
const Tutorial = wantsWindowSizes(injectIntl(_Tutorial));

type ValidKey = 'languages' | 'categories' | 'query';

type StringWithFrequency = string;

class _FilterBar extends React.Component {
  props: {
    initialLanguages: Array<StringWithFrequency>;
    initialCategories: Array<StringWithFrequency>;
    languages: MultiSelectState;
    categories: MultiSelectState;
    query: string;

    onChange: (key: ValidKey, newState: any) => void;

    // Self-managed props
    intl: intlShape;
  }

  _query: HTMLInputElement;

  render() {
    return (
      <Card>
        <form className="form-inline">
          <div style={{ marginBottom: 10 }}>
            Styles:{' '}
            <MultiSelectList
              list={this.props.initialCategories}
              selected={this.props.categories}
              // ref={(x) => { this._styles = x; }}
              onChange={state => this.props.onChange('categories', state)}
              itemRenderer={(data) => {
                const x = JSON.parse(data);
                return `${x.title} (${x.count})`;
              }}
            />
          </div>
          <div style={{ marginBottom: 10 }}>
            Language:{' '}
            <MultiSelectList
              list={this.props.initialLanguages}
              selected={this.props.languages}
              // ref={(x) => { this._styles = x; }}
              onChange={state => this.props.onChange('languages', state)}
              itemRenderer={(data) => {
                const x = JSON.parse(data);
                return `${languageData[this.props.intl.locale][x.language]} (${x.count})`;
              }}
            />
          </div>
          <div>
            Keywords:{' '}
            <input
              className="form-control"
              // style={{ width: '100%' }}
              type="text"
              value={this.props.query}
              ref={(x) => { this._query = x; }}
              onChange={state => this.props.onChange('query', this._query.value)}
              placeholder="teacher or dance move"
            />{' '}
          </div>
        </form>
        <div style={{ float: 'right' }}><ShareLinks url={'http://www.dancedeets.com/tutorials'} /></div>
        <div style={{ clear: 'both' }} />
      </Card>
    );
  }
}
const FilterBar = injectIntl(_FilterBar);

class _TutorialFilteredLayout extends React.Component {
  props: {
    categories: Array<Category>;
    hashLocation: string;

    // Self-managed props
    intl: intlShape;
  }

  state: {
    languages: MultiSelectState;
    categories: MultiSelectState;
    query: string;
  }

  _tutorials: Array<Playlist>;
  _languages: Array<StringWithFrequency>;
  _categories: Array<StringWithFrequency>;

  constructor(props) {
    super(props);

    const tutorials = [].concat(...this.props.categories.map(x => x.tutorials));
    const languages = countBy(tutorials.map(x => x.language));
    const dataList = Object.keys(languages).map(language => ({ language, count: languages[language] }));
    this._languages = sortNumber(dataList, x => -x.count).map(x => JSON.stringify(x));

    this._categories = this.props.categories.map(x => ({
      categoryId: x.style.id,
      title: x.style.titleMessage ? this.props.intl.formatMessage(x.style.titleMessage) : x.style.title,
      count: x.tutorials.length,
    })).map(x => JSON.stringify(x));

    this.state = {
      languages: generateUniformState(this._languages, true),
      categories: generateUniformState(this._categories, true),
      query: '',
    };


    // Parse incoming querystring state
    if (this.props.hashLocation) {
      this.state = {
        ...this.state,
        ...this.parseHash(this.state, this.props.hashLocation),
      };
    }
    (this: any).onChange = this.onChange.bind(this);
  }

  componentWillUpdate(newProps, newState) {
    if (newState !== this.state) {
      this.updateHash(newState);
    }
  }

  onChange(key: ValidKey, state: any) {
    this.setState({ [key]: state });
  }

  parseHash(fullState, hashLocation: string) {
    const newState = {
    };
    const incomingState = querystring.parse(hashLocation);
    if (incomingState.languages) {
      const incomingLanguages = incomingState.languages.split(',');
      newState.languages = {};
      Object.keys(fullState.languages).forEach((key) => {
        const data = JSON.parse(key);
        newState.languages[key] = incomingLanguages.includes(data.language);
      });
    }
    if (incomingState.categories) {
      const incomingCategories = incomingState.categories.split(',');
      newState.categories = {};
      Object.keys(fullState.categories).forEach((key) => {
        const data = JSON.parse(key);
        newState.categories[key] = incomingCategories.includes(data.categoryId);
      });
    }
    if (incomingState.query) {
      newState.query = incomingState.query;
    }
    return newState;
  }

  updateHash(newState) {
    const params = {};
    if (!isAllSelected(newState.languages)) {
      params.languages = getSelected(newState.languages).map(x => JSON.parse(x).language).join(',');
    }
    if (!isAllSelected(newState.categories)) {
      params.categories = getSelected(newState.categories).map(x => JSON.parse(x).categoryId).join(',');
    }
    if (newState.query) {
      params.query = newState.query;
    }
    const contents = querystring.stringify(params);
    const oldHash = window.location.hash || '#';
    const newHash = `#${contents}`;
    if (oldHash !== newHash) {
      history.replaceState(undefined, '', newHash);
    }
  }

  render() {
    // Filter based on the 'categories'
    const selectedCategoryNames = getSelected(this.state.categories).map(x => JSON.parse(x).categoryId);
    const selectedCategories = this.props.categories.filter(x => includes(selectedCategoryNames, x.style.id));
    const tutorials = [].concat(...selectedCategories.map(x => x.tutorials));

    const keywords = this.state.query.toLowerCase().split(' ').filter(x => x && x.length >= 2);

    // Filter based on the 'languages'
    const filteredTutorials = tutorials.filter((tutorial) => {
      if (getSelected(this.state.languages).filter(language => JSON.parse(language).language === tutorial.language).length === 0) {
        return false;
      }
      if (keywords.length) {
        const tutorialText = tutorial.getSearchText();
        const missingKeywords = keywords.filter(keyword => tutorialText.indexOf(keyword) === -1);
        if (missingKeywords.length) {
          return false;
        }
      }
      return true;
    });


    // Now let's render them
    const tutorialComponents = filteredTutorials.map(tutorial =>
      <Tutorial key={tutorial.getId()} tutorial={tutorial} searchKeywords={keywords} />);
    const title = 'Dance Tutorials';
    const meta = generateMetaTags(title, 'http://www.dancedeets.com/tutorials/', 'http://www.dancedeets.com/dist/img/screenshot-tutorial.jpg');
    return (
      <div>
        <Helmet title={title} meta={meta} />
        <FilterBar
          initialLanguages={this._languages} languages={this.state.languages}
          initialCategories={this._categories} categories={this.state.categories}
          query={this.state.query}
          onChange={this.onChange}
        />
        {tutorialComponents}
        <div style={{ clear: 'both' }} />
      </div>
    );
  }
}
const TutorialFilteredLayout = injectIntl(_TutorialFilteredLayout);

class _TutorialOverview extends React.Component {
  props: {
    style: string;
    hashLocation: string;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const categories = getTutorials(this.props.intl.locale);
    if (this.props.style) {
      const matching = categories.filter(category => category.style.id === this.props.style);
      const category = matching.length ? matching[0] : null;
      if (category) {
        return <TutorialFilteredLayout hasLocation={this.props.hashLocation} categories={[category]} />;
      } else {
        // 404 not found
        return <div><Helmet title="Unknown Tutorial Category" />Unknown Style!</div>;
      }
    } else {
      // Super overiew
      return <TutorialFilteredLayout hashLocation={this.props.hashLocation} categories={categories} />;
    }
  }
}
const TutorialOverview = injectIntl(_TutorialOverview);

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TutorialOverview);
