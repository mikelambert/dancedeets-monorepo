import React from 'react';
import moment from 'moment';
import {
  SearchEvent,
  Event,
} from 'dancedeets-common/js/events/models';

function formatSchemaDate(dateTime) {
  return moment(dateTime).format('YYYY-MM-DD[T]HH:mm:ss');
}

function getEventSchema(event: Event) {
  const schema = {
    '@context': 'http://schema.org/',
    '@type': 'Event',
    name: event.name,
    mainEntityOfPage: event.getUrl(),
    url: event.getUrl(),
    organizer: event.admins.map(x => x.name).join(', '),
    startDate: formatSchemaDate(event.start_time),
    description: event.description,
  };
  if (event.end_time) {
    schema.endDate = formatSchemaDate(event.end_time);
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

export function getReactEventSchema(event) {
  const jsonMetadata = getEventSchema(event);
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonMetadata) }} // eslint-disable-line react/no-danger
    />
  );
}

function getArticleSchema(event: Event) {
  // NewsArticles require an image:
  // https://developers.google.com/structured-data/rich-snippets/articles#article_markup_properties
  if (!event.picture) {
    return null;
  }

  const datePublished = event.annotations.creation ? event.annotations.creation.time : event.start_time;
  const schema = {
    '@context': 'http://schema.org',
    '@type': 'Article',
    mainEntityOfPage: event.getUrl(),
    headline: event.name,
    image: {
      '@type': 'ImageObject',
      url: event.picture.source,
      height: event.picture.height,
      width: event.picture.width,
    },
    publisher: {
      '@type': 'Organization',
      name: 'DanceDeets',
      logo: {
        '@type': 'ImageObject',
        url: 'http://www.dancedeets.com/dist/img/deets-head-and-title-on-black.png',
        width: 246,
        height: 60,
      },
    },
    datePublished: formatSchemaDate(datePublished),
    author: {
      '@type': 'Organization',
      name: 'DanceDeets',
    },
    description: event.description,
  };
  return schema;
}

export function getReactArticleSchema(event) {
  const jsonMetadata = getArticleSchema(event);
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonMetadata) }} // eslint-disable-line react/no-danger
    />
  );
}
