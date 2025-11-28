/**
 * Copyright 2016 DanceDeets.
 */

import { Event, SearchEvent } from './models';

export type TimePeriod = 'UPCOMING' | 'ONGOING' | 'PAST' | 'ALL_FUTURE';

export interface SearchQuery {
  location: string;
  keywords: string;
  timePeriod: TimePeriod;
  locale?: string;
}

export interface Onebox {
  url: string;
  title: string;
}

interface LatLong {
  latitude: number;
  longitude: number;
}

export interface FeaturedInfo {
  event: Event;
  showTitle: boolean;
  overrideFlyer: string;
  promotionText?: string | null;
}

interface Person {
  id: string;
  name: string;
  count: number;
}

type Style = string;

export type StylePersonLookup = { [style: Style]: Array<Person> };

export interface PeopleListing {
  ADMIN?: StylePersonLookup;
  ATTENDEE?: StylePersonLookup;
}

// API Requests 1.x
export interface SearchResponse {
  people: PeopleListing;
  onebox_links: Array<Onebox>;
  results: Array<Event>;
  featuredInfos: Array<FeaturedInfo>;
  query: SearchQuery;
}

export interface Address {
  city?: string;
  state?: string;
  country?: string;
}

// API Requests 2.0+
export interface NewSearchResponse {
  people: PeopleListing;
  onebox_links: Array<Onebox>;
  results: Array<SearchEvent>;
  featuredInfos: Array<FeaturedInfo>;
  query: SearchQuery;
  // These are technically in SearchResponse too, but they weren't necessary there.
  // They aren't necessary here (yet), but this helps document the schema.
  title: string;
  location: string;
  address: Address;
  location_box?: {
    southwest: LatLong;
    northeast: LatLong;
  };
}
