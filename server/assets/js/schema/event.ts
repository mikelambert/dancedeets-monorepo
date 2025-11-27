/**
 * Copyright 2016 DanceDeets.
 */

import moment from 'moment';
import { SearchEvent, Event } from 'dancedeets-common/js/events/models';

function formatSchemaDate(dateTime: moment.Moment): string {
  return dateTime.format('YYYY-MM-DD[T]HH:mm:ss');
}

interface Location {
  '@type': string;
  sameAs?: string;
  geo?: {
    '@type': string;
    latitude: number;
    longitude: number;
  };
  name?: string;
  address?: string;
}

interface EventSchema {
  '@context': string;
  '@type': string;
  name: string;
  mainEntityOfPage: string;
  url: string;
  startDate: string;
  description?: string;
  organizer?: string;
  endDate?: string;
  image?: string;
  location?: Location;
  offers?: {
    url: string;
  };
}

export function getEventSchema(event: Event | SearchEvent): EventSchema {
  const schema: EventSchema = {
    '@context': 'http://schema.org/',
    '@type': 'Event',
    name: event.name,
    mainEntityOfPage: event.getUrl(),
    url: event.getUrl(),
    startDate: formatSchemaDate(event.getStartMoment({ timezone: false })),
  };
  if (event.description) {
    // only true for full Event objects
    schema.description = event.description;
  }
  if (event instanceof Event) {
    schema.organizer = event.admins.map(x => x.name).join(', ');
  }
  if (event.end_time) {
    schema.endDate = formatSchemaDate(event.getEndMoment({ timezone: false }));
  }
  if (event.picture) {
    schema.image = event.picture.source;
  }
  const location: Location = {
    '@type': 'Place',
  };
  if (event.venue.id) {
    location.sameAs = `https://www.facebook.com/${event.venue.id}`;
  }
  if (event.venue.geocode) {
    location.geo = {
      '@type': 'GeoCoordinates',
      latitude: event.venue.geocode.latitude,
      longitude: event.venue.geocode.longitude,
    };
  }
  if (event.venue.name) {
    location.name = event.venue.name;
  }
  if (event.venue.address) {
    const address = event.venue.streetCityStateCountry();
    if (address) {
      location.address = address;
    }
  }
  schema.location = location;
  if (event.ticket_uri) {
    schema.offers = {
      url: event.ticket_uri,
    };
  }
  return schema;
}

interface ArticleSchema {
  '@context': string;
  '@type': string;
  mainEntityOfPage: string;
  headline: string;
  image: {
    '@type': string;
    url: string;
    height: number | undefined;
    width: number | undefined;
  };
  publisher: {
    '@type': string;
    name: string;
    logo: {
      '@type': string;
      url: string;
      width: number;
      height: number;
    };
  };
  datePublished: string;
  author: {
    '@type': string;
    name: string;
  };
  description: string | undefined;
}

export function getArticleSchema(event: Event): ArticleSchema | null {
  // NewsArticles require an image:
  // https://developers.google.com/structured-data/rich-snippets/articles#article_markup_properties
  if (!event.picture) {
    return null;
  }
  const { picture } = event;

  const datePublished = event.annotations.creation
    ? event.annotations.creation.time
    : event.start_time;
  const schema: ArticleSchema = {
    '@context': 'http://schema.org',
    '@type': 'Article',
    mainEntityOfPage: event.getUrl(),
    headline: event.name,
    image: {
      '@type': 'ImageObject',
      url: picture.source,
      height: picture.height,
      width: picture.width,
    },
    publisher: {
      '@type': 'Organization',
      name: 'DanceDeets',
      logo: {
        '@type': 'ImageObject',
        url:
          'https://storage.googleapis.com/dancedeets-static/img/deets-head-and-title-on-black.png',
        width: 246,
        height: 60,
      },
    },
    datePublished: formatSchemaDate(moment(datePublished)),
    author: {
      '@type': 'Organization',
      name: 'DanceDeets',
    },
    description: event.description,
  };
  return schema;
}
