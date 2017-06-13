/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { Event, SearchEvent } from './models';

export type TimePeriod = 'UPCOMING' | 'ONGOING' | 'PAST' | 'ALL_FUTURE';

export type SearchQuery = {
  location: string,
  keywords: string,
  timePeriod: TimePeriod,
  locale?: string,
};

export type Onebox = {
  url: string,
  title: string,
};

type LatLong = {
  latitude: number,
  longitude: number,
};

export type FeaturedInfo = {
  event: Event,
  showTitle: boolean,
  overrideFlyer: string,
};

type Person = {
  id: string,
  name: string,
  count: number,
};

type Style = string;

export type StylePersonLookup = { [style: Style]: Array<Person> };

export type PeopleListing = {
  ADMIN?: StylePersonLookup,
  ATTENDEE?: StylePersonLookup,
};

// API Requests 1.x
export type SearchResponse = {
  people: PeopleListing,
  onebox_links: Array<Onebox>,
  results: Array<Event>,
  featuredInfos: Array<FeaturedInfo>,
  query: SearchQuery,
};

// API Requests 2.0+
export type NewSearchResponse = {
  people: PeopleListing,
  onebox_links: Array<Onebox>,
  results: Array<SearchEvent>,
  featuredInfos: Array<FeaturedInfo>,
  query: SearchQuery,
  // These are technically in SearchResponse too, but they weren't necessary there.
  // They aren't necessary here (yet), but this helps document the schema.
  title: string,
  location: string,
  location_box?: {
    southwest: LatLong,
    northeast: LatLong,
  },
};
