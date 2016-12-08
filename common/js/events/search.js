/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  Event,
  SearchEvent,
} from './models';

export type TimePeriod = 'UPCOMING' | 'ONGOING' | 'PAST' | 'ALL_FUTURE';

export type SearchQuery = {
  location: string;
  keywords: string;
  timePeriod: TimePeriod;
};

export type Onebox = {
  url: string;
  title: string;
};

export type SearchResults = {
  onebox_links: Array<Onebox>;
  results: Array<Event>;
  query: SearchQuery;
};

export type NewSearchResults = {
  onebox_links: Array<Onebox>;
  results: Array<SearchEvent>;
  query: SearchQuery;
};
