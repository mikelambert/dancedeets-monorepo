import React from 'react';
import moment from 'moment';
import {
  MiniEvent,
  Event,
} from 'dancedeets-common/js/events/models';

function formatSchemaDate(dateTime) {
  return moment(dateTime).format('YYYY-MM-DD[T]HH:mm:ss');
}

function getDanceEventSchema(event: MiniEvent|Event) {
  const schema = {
    '@context': 'http://schema.org/',
    '@type': 'DanceEvent',
    name: event.name,
    mainEntityOfPage: event.getUrl(),
    url: event.getUrl(),
    organizer: event.admins.map(x => x.name).join(', '),
    startDate: formatSchemaDate(event.start_time),
  };
  if (event.end_time) {
    schema.endDate = formatSchemaDate(event.end_time);
  }
  if (event.picture) {
    schema.image = event.picture.source;
  }
  schema.location = {};
  if (event.venue.id) {
    schema.location.sameAs = `https://www.facebook.com/${event.venue.id}`;
  }
  if (event.venue.geocode) {
    schema.location.geo = {
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

export function getReactDanceEventSchema(event) {
  const jsonMetadata = getDanceEventSchema(event);
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonMetadata) }} // eslint-disable-line react/no-danger
    />
  );
}

export function getNewsArticleAmpSchema(event: Event) {
  const schema = {
    '@context': 'http://schema.org',
    '@type': 'NewsArticle',
    mainEntityOfPage: event.getUrl(),
    headline: event.name,
    datePublished: formatSchemaDate(event.annotations.creation.time),
    description: event.description,
    author: {
      '@type': 'Organization',
      name: 'DanceDeets',
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
  };
  if (event.picture) {
    schema.image = {
      '@type': 'ImageObject',
      url: event.picture.source,
      height: event.picture.height,
      width: event.picture.width,
    };
  }
  return schema;
}
