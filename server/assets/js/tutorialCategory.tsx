/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import countBy from 'lodash/countBy';
import { useIntl, IntlShape } from 'react-intl';
import Helmet from 'react-helmet';
import Masonry from 'react-masonry-component';
import LazyLoad from 'react-lazyload';
import querystring from 'querystring';
import { createBrowserHistory } from 'history';
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
import type { WindowProps } from './ui';
import { generateMetaTags } from './meta';
import {
  getSelected,
  generateUniformState,
  isAllSelected,
  MultiSelectList,
} from './MultiSelectList';
import type { MultiSelectState } from './MultiSelectList';

// Hardcoded list of languages
const languageData: Record<string, string> = {
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

interface MatchedVideoProps {
  tutorial: Playlist;
  video: Video;
}

function MatchedVideo({ tutorial, video }: MatchedVideoProps): React.ReactElement {
  const tutorialUrl = tutorial.getUrl();
  const videoIndex = tutorial.getVideoIndex(video);
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
        <div style={{ fontWeight: 'bold' }}>{video.title}</div>
      </a>
    </div>
  );
}

interface MatchedSectionProps {
  tutorial: Playlist;
  section: Section;
  children: React.ReactNode;
}

function MatchedSection({ tutorial, section, children }: MatchedSectionProps): React.ReactElement {
  const tutorialUrl = tutorial.getUrl();
  const videoIndex = tutorial.getVideoIndex(section.videos[0]);
  const url = `${tutorialUrl}#${videoIndex}`;
  return (
    <div>
      <div>
        <a href={url}>{section.title}</a>
      </div>
      {children}
    </div>
  );
}

interface TutorialProps {
  tutorial: Playlist;
  searchKeywords: Array<string>;
  lazyLoad: boolean;
  window: WindowProps;
}

function TutorialInner({ tutorial, searchKeywords, lazyLoad, window: windowProp }: TutorialProps): React.ReactElement {
  const intl = useIntl();

  function matchesKeywords(obj: Video | Section): boolean {
    const text = obj.getSearchText();
    return (
      searchKeywords.filter(x => text.indexOf(x) !== -1).length > 0
    );
  }

  function renderMatchingVideos(): React.ReactElement[] | null {
    if (!searchKeywords.length) {
      return null;
    }
    const sections: React.ReactElement[] = [];
    tutorial.sections.forEach(section => {
      const sectionVideos: React.ReactElement[] = [];
      section.videos.forEach(video => {
        if (matchesKeywords(video)) {
          sectionVideos.push(
            <MatchedVideo
              key={video.youtubeId}
              tutorial={tutorial}
              video={video}
            />
          );
        }
      });
      if (sectionVideos.length || matchesKeywords(section)) {
        sections.push(
          <MatchedSection
            key={section.title}
            tutorial={tutorial}
            section={section}
          >
            {sectionVideos}
          </MatchedSection>
        );
      }
    });
    return sections;
  }

  const duration = formatDuration(
    intl.formatMessage,
    tutorial.getDurationSeconds()
  );

  const numVideosDuration = intl.formatMessage(
    messages.numVideosWithDuration,
    { count: tutorial.getVideoCount(), duration }
  );

  const matchingVideos = renderMatchingVideos();

  const margin = 2 * 10;
  let cardSize = 320 + margin;
  if (windowProp) {
    cardSize =
      windowProp.width /
        Math.floor(windowProp.width / cardSize) -
      margin;
  }

  const youtubeThumbnailsRatio = 320 / 180;
  const padding = 2 * 10;
  const imageWidth = cardSize - padding;
  const imageHeight = imageWidth / youtubeThumbnailsRatio;

  let imageTag: React.ReactElement = (
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
  if (lazyLoad) {
    imageTag = (
      <LazyLoad
        height={imageHeight}
        once
        offset={300}
        overflow
      >
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
const Tutorial = wantsWindowSizes(TutorialInner);

type ValidKey = 'languages' | 'categories' | 'query';
type StringWithFrequency = string;

interface FilterBarProps {
  initialLanguages: Array<StringWithFrequency>;
  initialCategories: Array<StringWithFrequency>;
  languages: MultiSelectState;
  categories: MultiSelectState;
  query: string;
  onChange: (key: ValidKey, newState: unknown) => void;
}

function FilterBar({
  initialLanguages,
  initialCategories,
  languages,
  categories,
  query,
  onChange,
}: FilterBarProps): React.ReactElement {
  const queryRef = React.useRef<HTMLInputElement | null>(null);

  return (
    <Card>
      <form className="form-inline">
        <div style={{ marginBottom: 10 }}>
          Styles:{' '}
          <MultiSelectList
            list={initialCategories}
            selected={categories}
            onChange={state => onChange('categories', state)}
            itemRenderer={data => {
              const x = JSON.parse(data);
              return `${x.title} (${x.count})`;
            }}
          />
        </div>
        <div style={{ marginBottom: 10 }}>
          Language:{' '}
          <MultiSelectList
            list={initialLanguages}
            selected={languages}
            onChange={state => onChange('languages', state)}
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
            type="text"
            value={query}
            ref={x => {
              queryRef.current = x;
            }}
            onChange={() =>
              queryRef.current
                ? onChange('query', queryRef.current.value)
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

// Helper function to compute initial data
function computeInitialData(
  categoriesData: Array<Category>,
  intl: IntlShape
): { languages: Array<StringWithFrequency>; categories: Array<StringWithFrequency> } {
  const tutorials = ([] as Playlist[]).concat(...categoriesData.map(x => x.tutorials));
  const languageCounts = countBy(tutorials.map(x => x.language));
  const dataList = Object.keys(languageCounts).map(language => ({
    language,
    count: languageCounts[language],
  }));
  const languagesList = sortNumber(dataList, x => -x.count).map(x =>
    JSON.stringify(x)
  );

  const categoriesList = categoriesData
    .map(x => ({
      categoryId: x.style.id,
      title: x.style.titleMessage
        ? intl.formatMessage(x.style.titleMessage)
        : x.style.title,
      count: x.tutorials.length,
    }))
    .map(x => JSON.stringify(x));

  return { languages: languagesList, categories: categoriesList };
}

interface TutorialFilteredLayoutProps {
  categories: Array<Category>;
  hashLocation: string;
}

interface TutorialFilteredLayoutState {
  languages: MultiSelectState;
  categories: MultiSelectState;
  query: string;
}

function TutorialFilteredLayout({ categories: categoriesData, hashLocation }: TutorialFilteredLayoutProps): React.ReactElement {
  const intl = useIntl();

  // Compute initial data using intl
  const initialData = React.useMemo(
    () => computeInitialData(categoriesData, intl),
    [categoriesData, intl]
  );

  // Initialize state
  const getInitialState = React.useCallback((): TutorialFilteredLayoutState => {
    const baseState: TutorialFilteredLayoutState = {
      languages: generateUniformState(initialData.languages, true),
      categories: generateUniformState(initialData.categories, true),
      query: '',
    };

    if (hashLocation) {
      return { ...baseState, ...parseHash(baseState, hashLocation) };
    }
    return baseState;
  }, [initialData, hashLocation]);

  const [state, setState] = React.useState<TutorialFilteredLayoutState>(getInitialState);

  function parseHash(fullState: TutorialFilteredLayoutState, hash: string): Partial<TutorialFilteredLayoutState> {
    const newState: Partial<TutorialFilteredLayoutState> = {};
    const incomingState = querystring.parse(hash) as Record<string, string>;
    if (incomingState.languages) {
      const incomingLanguages = incomingState.languages.split(',');
      newState.languages = {};
      Object.keys(fullState.languages).forEach(key => {
        const data = JSON.parse(key);
        newState.languages![key] = incomingLanguages.includes(data.language);
      });
    }
    if (incomingState.categories) {
      const incomingCategories = incomingState.categories.split(',');
      newState.categories = {};
      Object.keys(fullState.categories).forEach(key => {
        const data = JSON.parse(key);
        newState.categories![key] = incomingCategories.includes(data.categoryId);
      });
    }
    if (incomingState.query) {
      newState.query = incomingState.query;
    }
    return newState;
  }

  // Update hash when state changes
  React.useEffect(() => {
    const params: Record<string, string> = {};
    if (!isAllSelected(state.languages)) {
      params.languages = getSelected(state.languages)
        .map(x => JSON.parse(x).language)
        .join(',');
    }
    if (!isAllSelected(state.categories)) {
      params.categories = getSelected(state.categories)
        .map(x => JSON.parse(x).categoryId)
        .join(',');
    }
    if (state.query) {
      params.query = state.query;
    }
    const contents = querystring.stringify(params);
    const oldHash = window.location.hash || '#';
    const newHash = `#${contents}`;
    if (oldHash !== newHash) {
      const history = createBrowserHistory();
      if (history) {
        history.replace(window.location.pathname + newHash);
      } else {
        console.log(
          'Failed to create browser history object, falling back to direct manipulation.'
        );
        window.location.hash = newHash;
      }
    }
  }, [state]);

  function onChange(key: ValidKey, newValue: unknown): void {
    setState(prev => ({ ...prev, [key]: newValue }));
  }

  // Filter based on the 'categories'
  const selectedCategoryNames = getSelected(state.categories).map(
    x => JSON.parse(x).categoryId
  );
  const selectedCategories = categoriesData.filter(x =>
    selectedCategoryNames.includes(x.style.id)
  );
  const tutorials = ([] as Playlist[]).concat(...selectedCategories.map(x => x.tutorials));

  const keywords = state.query
    .toLowerCase()
    .split(' ')
    .filter(x => x && x.length >= 2);

  // Filter based on the 'languages'
  const filteredTutorials = tutorials.filter(tutorial => {
    if (
      getSelected(state.languages).filter(
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
      lazyLoad={index > 5}
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
        initialLanguages={initialData.languages}
        languages={state.languages}
        initialCategories={initialData.categories}
        categories={state.categories}
        query={state.query}
        onChange={onChange}
      />
      <Masonry>{tutorialComponents}</Masonry>
    </div>
  );
}

interface TutorialOverviewProps {
  style: string;
  hashLocation: string;
  currentLocale: string;
}

function TutorialOverview({ style, hashLocation }: TutorialOverviewProps): React.ReactElement {
  const intl = useIntl();
  const categories = getTutorials(intl.locale);
  if (style) {
    const matching = categories.filter(
      category => category.style.id === style
    );
    const category = matching.length ? matching[0] : null;
    if (category) {
      return (
        <TutorialFilteredLayout
          hashLocation={hashLocation}
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
    // Super overview
    return (
      <TutorialFilteredLayout
        hashLocation={hashLocation}
        categories={categories}
      />
    );
  }
}

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TutorialOverview);
