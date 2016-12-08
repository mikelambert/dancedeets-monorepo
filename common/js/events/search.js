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
  locale: string;
  timePeriod: TimePeriod;
};

export type Onebox = {
  url: string;
  title: string;
};

type LatLong = {
  latitude: number;
  longitude: number;
};

// API Requests 1.x
export type SearchResults = {
  onebox_links: Array<Onebox>;
  results: Array<Event>;
  query: SearchQuery;
};

// API Requests 2.0+
export type NewSearchResults = {
  onebox_links: Array<Onebox>;
  results: Array<SearchEvent>;
  query: SearchQuery;
  // These are technically in SearchResults too, but they weren't necessary there.
  // They aren't necessary here (yet), but this helps document the schema.
  title: string;
  location: string;
  location_box?: {
    southwest: LatLong;
    northeast: LatLong;
  };
};
