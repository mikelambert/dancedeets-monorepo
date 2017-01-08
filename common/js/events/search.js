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
  locale?: string;
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
export type SearchResponse = {
  onebox_links: Array<Onebox>;
  results: Array<Event>;
  query: SearchQuery;
};

// API Requests 2.0+
export type NewSearchResponse = {
  onebox_links: Array<Onebox>;
  results: Array<SearchEvent>;
  query: SearchQuery;
  // These are technically in SearchResponse too, but they weren't necessary there.
  // They aren't necessary here (yet), but this helps document the schema.
  title: string;
  location: string;
  location_box?: {
    southwest: LatLong;
    northeast: LatLong;
  };
};
