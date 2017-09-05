/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import moment from 'moment';
import { SearchEvent, Event } from 'dancedeets-common/js/events/models';

function formatSchemaDate(dateTime) {
  return dateTime.format('YYYY-MM-DD[T]HH:mm:ss');
}

export function getEventSchema(event: Event | SearchEvent) {
  const schema: Object = {
    '@context': 'http://schema.org/',
    '@type': 'Event',
    name: event.name,
    mainEntityOfPage: event.getUrl(),
    url: event.getUrl(),
    startDate: formatSchemaDate(event.getStartMoment({ timezone: false })),
    description: event.description,
  };
  if (event.admins) {
    schema.organizer = event.admins.map(x => x.name).join(', ');
  }
  if (event.end_time) {
    schema.endDate = formatSchemaDate(event.getEndMoment({ timezone: false }));
  }
  if (event.picture) {
    schema.image = event.picture.source;
  }
  schema.location = {
    '@type': 'Place',
  };
  if (event.venue.id) {
    schema.location.sameAs = `https://www.facebook.com/${event.venue.id}`;
  }
  if (event.venue.geocode) {
    schema.location.geo = {
      '@type': 'GeoCoordinates',
      latitude: event.venue.geocode.latitude,
      longitude: event.venue.geocode.longitude,
    };
  }
  if (event.venue.name) {
    schema.location.name = event.venue.name;
  }
  if (event.venue.address) {
    schema.location.address = event.venue.streetCityStateCountry();
  }
  if (event.ticket_uri) {
    schema.offers = {
      url: event.ticket_uri,
    };
  }
  return schema;
}

export function getArticleSchema(event: Event) {
  // NewsArticles require an image:
  // https://developers.google.com/structured-data/rich-snippets/articles#article_markup_properties
  if (!event.picture) {
    return null;
  }
  const picture = event.picture;

  const datePublished = event.annotations.creation
    ? event.annotations.creation.time
    : event.start_time;
  const schema = {
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
          'https://static.dancedeets.com/img/deets-head-and-title-on-black.png',
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
