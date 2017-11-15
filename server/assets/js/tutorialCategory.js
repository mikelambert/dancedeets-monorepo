/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import countBy from 'lodash/countBy';
import { injectIntl, intlShape } from 'react-intl';
import Helmet from 'react-helmet';
import Masonry from 'react-masonry-component';
import LazyLoad from 'react-lazyload';
import querystring from 'querystring';
import createBrowserHistory from 'history/createBrowserHistory';
import { intlWeb } from 'dancedeets-common/js/intl';
import { getTutorials } from 'dancedeets-common/js/tutorials/playlistConfig';
import type { Category } from 'dancedeets-common/js/tutorials/playlistConfig';
import {
  Playlist,
  Section,
  Video,
} from 'dancedeets-common/js/tutorials/models';
import { formatDuration } from 'dancedeets-common/js/tutorials/format';
import messages from 'dancedeets-common/js/tutorials/messages';
import { sortNumber } from 'dancedeets-common/js/util/sort';
import { cdnBaseUrl } from 'dancedeets-common/js/util/url';
import { Card, ShareLinks, wantsWindowSizes } from './ui';
import type { windowProps } from './ui';
import { generateMetaTags } from './meta';
import {
  getSelected,
  generateUniformState,
  isAllSelected,
  MultiSelectList,
} from './MultiSelectList';
import type { MultiSelectState } from './MultiSelectList';

// Can/should we trim this file? It is 150KB, and we probably only need 10KB of it...
// import languageData from 'dancedeets-common/js/languages';
// Instead, let's just us a small hardcoded list of languages for now...
// We can revisit this later when we are producing per-locale bundles
// and when we can pre-process the above file to include just the relevant languages we need to translate
const languageData = {
  cs: 'Czech',
  en: 'English',
  es: 'Spanish',
  it: 'Italian',
  ja: 'Japanese',
  ko: 'Korean',
  lt: 'Lithuanian',
  pl: 'Polish',
  ru: 'Russian',
  zh: 'Chinese',
};

class MatchedVideo extends React.Component<{
  tutorial: Playlist,
  video: Video,
}> {
  render() {
    const tutorialUrl = this.props.tutorial.getUrl();
    const videoIndex = this.props.tutorial.getVideoIndex(this.props.video);
    const url = `${tutorialUrl}#${videoIndex}`;
    return (
      <div
        style={{
          paddingLeft: 15,
          borderBottomWidth: 0.5,
          borderBottomStyle: 'solid',
        }}
      >
        <a href={url}>
          <div style={{ fontWeight: 'bold' }}>{this.props.video.title}</div>
        </a>
      </div>
    );
  }
}

class MatchedSection extends React.Component<{
  tutorial: Playlist,
  section: Section,
  children: React.Node,
}> {
  render() {
    const tutorialUrl = this.props.tutorial.getUrl();
    const videoIndex = this.props.tutorial.getVideoIndex(
      this.props.section.videos[0]
    );
    const url = `${tutorialUrl}#${videoIndex}`;
    return (
      <div>
        <div>
          <a href={url}>{this.props.section.title}</a>
        </div>
        {this.props.children}
      </div>
    );
  }
}

class _Tutorial extends React.Component<{
  tutorial: Playlist,
  searchKeywords: Array<string>,
  lazyLoad: boolean,

  // Self-managed-props
  intl: intlShape,
  window: windowProps,
}> {
  matchesKeywords(obj: Video | Section) {
    const text = obj.getSearchText();
    return (
      this.props.searchKeywords.filter(x => text.indexOf(x) !== -1).length > 0
    );
  }

  renderMatchingVideos() {
    if (!this.props.searchKeywords.length) {
      return null;
    }
    const sections = [];
    this.props.tutorial.sections.forEach(section => {
      const sectionVideos = [];
      section.videos.forEach(video => {
        if (this.matchesKeywords(video)) {
          sectionVideos.push(
            <MatchedVideo
              key={video.youtubeId}
              tutorial={this.props.tutorial}
              video={video}
            />
          );
        }
      });
      if (sectionVideos.length || this.matchesKeywords(section)) {
        sections.push(
          <MatchedSection
            key={section.title}
            tutorial={this.props.tutorial}
            section={section}
          >
            {sectionVideos}
          </MatchedSection>
        );
      }
    });
    return sections;
  }

  render() {
    // De-Dupe
    const { tutorial } = this.props;
    const duration = formatDuration(
      this.props.intl.formatMessage,
      tutorial.getDurationSeconds()
    );

    if (this.props.intl.locale !== tutorial.language) {
      // const localizedLanguage = languages[this.props.intl.locale][tutorial.language];
      // title = this.props.intl.formatMessage(messages.languagePrefixedTitle, { language: upperFirst(localizedLanguage), title: tutorial.title });
    }
    const numVideosDuration = this.props.intl.formatMessage(
      messages.numVideosWithDuration,
      { count: tutorial.getVideoCount(), duration }
    );

    const matchingVideos = this.renderMatchingVideos();

    const margin = 2 * 10;
    let cardSize = 320 + margin;
    if (this.props.window) {
      cardSize =
        this.props.window.width /
          Math.floor(this.props.window.width / cardSize) -
        margin;
    }

    const youtubeThumbnailsRatio = 320 / 180;
    const padding = 2 * 10;
    const imageWidth = cardSize - padding;
    const imageHeight = imageWidth / youtubeThumbnailsRatio;

    let imageTag = (
      <img
        src={tutorial.thumbnail}
        alt=""
        style={{
          width: '100%',
          display: 'block',
          marginLeft: 'auto',
          marginRight: 'auto',
        }}
      />
    );
    if (this.props.lazyLoad) {
      imageTag = (
        <LazyLoad height={imageHeight} once offset={300}>
          {imageTag}
        </LazyLoad>
      );
    }
    return (
      <Card style={{ width: cardSize }}>
        <a href={`/tutorials/${tutorial.getId()}`}>
          {imageTag}
          <div>
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

class _FilterBar extends React.Component<{
  initialLanguages: Array<StringWithFrequency>,
  initialCategories: Array<StringWithFrequency>,
  languages: MultiSelectState,
  categories: MultiSelectState,
  query: string,

  onChange: (key: ValidKey, newState: any) => void,

  // Self-managed props
  // intl: intlShape,
}> {
  _query: ?HTMLInputElement;

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
              itemRenderer={data => {
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
              itemRenderer={data => {
                const x = JSON.parse(data);
                return `${languageData[x.language]} (${x.count})`;
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
              ref={x => {
                this._query = x;
              }}
              onChange={state =>
                this._query
                  ? this.props.onChange('query', this._query.value)
                  : null}
              placeholder="teacher or dance move"
            />{' '}
          </div>
        </form>
        <div style={{ float: 'right' }}>
          <ShareLinks url="https://www.dancedeets.com/tutorials" />
        </div>
        <div style={{ clear: 'both' }} />
      </Card>
    );
  }
}
const FilterBar = injectIntl(_FilterBar);

class _TutorialFilteredLayout extends React.Component<
  {
    categories: Array<Category>,
    hashLocation: string,

    // Self-managed props
    intl: intlShape,
  },
  {
    languages: MultiSelectState,
    categories: MultiSelectState,
    query: string,
  }
> {
  _tutorials: Array<Playlist>;
  _languages: Array<StringWithFrequency>;
  _categories: Array<StringWithFrequency>;

  constructor(props) {
    super(props);

    const tutorials = [].concat(...this.props.categories.map(x => x.tutorials));
    const languages = countBy(tutorials.map(x => x.language));
    const dataList = Object.keys(languages).map(language => ({
      language,
      count: languages[language],
    }));
    this._languages = sortNumber(dataList, x => -x.count).map(x =>
      JSON.stringify(x)
    );

    this._categories = this.props.categories
      .map(x => ({
        categoryId: x.style.id,
        title: x.style.titleMessage
          ? this.props.intl.formatMessage(x.style.titleMessage)
          : x.style.title,
        count: x.tutorials.length,
      }))
      .map(x => JSON.stringify(x));

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
    const newState = {};
    const incomingState = querystring.parse(hashLocation);
    if (incomingState.languages) {
      const incomingLanguages = incomingState.languages.split(',');
      newState.languages = {};
      Object.keys(fullState.languages).forEach(key => {
        const data = JSON.parse(key);
        newState.languages[key] = incomingLanguages.includes(data.language);
      });
    }
    if (incomingState.categories) {
      const incomingCategories = incomingState.categories.split(',');
      newState.categories = {};
      Object.keys(fullState.categories).forEach(key => {
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
      params.languages = getSelected(newState.languages)
        .map(x => JSON.parse(x).language)
        .join(',');
    }
    if (!isAllSelected(newState.categories)) {
      params.categories = getSelected(newState.categories)
        .map(x => JSON.parse(x).categoryId)
        .join(',');
    }
    if (newState.query) {
      params.query = newState.query;
    }
    const contents = querystring.stringify(params);
    const oldHash = window.location.hash || '#';
    const newHash = `#${contents}`;
    if (oldHash !== newHash) {
      const history = createBrowserHistory();
      history.replaceState(undefined, '', newHash);
    }
  }

  render() {
    // Filter based on the 'categories'
    const selectedCategoryNames = getSelected(this.state.categories).map(
      x => JSON.parse(x).categoryId
    );
    const selectedCategories = this.props.categories.filter(x =>
      selectedCategoryNames.includes(x.style.id)
    );
    const tutorials = [].concat(...selectedCategories.map(x => x.tutorials));

    const keywords = this.state.query
      .toLowerCase()
      .split(' ')
      .filter(x => x && x.length >= 2);

    // Filter based on the 'languages'
    const filteredTutorials = tutorials.filter(tutorial => {
      if (
        getSelected(this.state.languages).filter(
          language => JSON.parse(language).language === tutorial.language
        ).length === 0
      ) {
        return false;
      }
      if (keywords.length) {
        const tutorialText = tutorial.getSearchText();
        const missingKeywords = keywords.filter(
          keyword => tutorialText.indexOf(keyword) === -1
        );
        if (missingKeywords.length) {
          return false;
        }
      }
      return true;
    });

    // Now let's render them
    const tutorialComponents = filteredTutorials.map((tutorial, index) => (
      <Tutorial
        key={tutorial.getId()}
        tutorial={tutorial}
        searchKeywords={keywords}
        lazyLoad={index > 30}
      />
    ));
    const title = 'Dance Tutorials';
    const meta = generateMetaTags(
      title,
      'https://www.dancedeets.com/tutorials/',
      `${cdnBaseUrl}/img/screenshot-tutorial.jpg`
    );
    return (
      <div>
        <Helmet title={title} meta={meta} />
        <FilterBar
          initialLanguages={this._languages}
          languages={this.state.languages}
          initialCategories={this._categories}
          categories={this.state.categories}
          query={this.state.query}
          onChange={this.onChange}
        />
        <Masonry>{tutorialComponents}</Masonry>
      </div>
    );
  }
}
const TutorialFilteredLayout = injectIntl(_TutorialFilteredLayout);

class _TutorialOverview extends React.Component<{
  style: string,
  hashLocation: string,

  // Self-managed props
  intl: intlShape,
}> {
  render() {
    const categories = getTutorials(this.props.intl.locale);
    if (this.props.style) {
      const matching = categories.filter(
        category => category.style.id === this.props.style
      );
      const category = matching.length ? matching[0] : null;
      if (category) {
        return (
          <TutorialFilteredLayout
            hasLocation={this.props.hashLocation}
            categories={[category]}
          />
        );
      } else {
        // 404 not found
        return (
          <div>
            <Helmet title="Unknown Tutorial Category" />Unknown Style!
          </div>
        );
      }
    } else {
      // Super overiew
      return (
        <TutorialFilteredLayout
          hashLocation={this.props.hashLocation}
          categories={categories}
        />
      );
    }
  }
}
const TutorialOverview = injectIntl(_TutorialOverview);

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TutorialOverview);
