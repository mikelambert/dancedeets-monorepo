/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import querystring from 'querystring';
import { SearchEvent, Event } from 'dancedeets-common/js/events/models';
import type { Address } from 'dancedeets-common/js/events/search';

type BreadcrumbsSchema = ?Object;

function locationFor(components) {
  const query = { location: components.filter(x => x).join(', ') };
  return `/?${querystring.stringify(query)}`;
}

function generateBreadcrumbs(listItems) {
  const schemaListItems = listItems.map((listItem, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    item: {
      '@id': listItem.url,
      name: listItem.name,
    },
  }));
  const schema: BreadcrumbsSchema = {
    '@context': 'http://schema.org/',
    '@type': 'BreadcrumbList',
    itemListElement: schemaListItems,
  };
  return schema;
}

export function getBreadcrumbsForEvent(
  event: Event | SearchEvent
): BreadcrumbsSchema {
  const listItems = [];
  const address = event.venue.address;
  if (!address) {
    return null;
  }
  if (address.country) {
    listItems.push({
      url: locationFor([address.country]),
      name: address.country,
    });
  }
  if (address.state) {
    listItems.push({
      url: locationFor([address.state, address.country]),
      name: address.state,
    });
  }
  if (address.city) {
    listItems.push({
      url: locationFor([address.city, address.state, address.country]),
      name: address.city,
    });
  }
  listItems.push({
    url: event.getUrl(),
    name: event.name,
  });
  return generateBreadcrumbs(listItems);
}

export function getBreadcrumbsForSearch(
  address: Address,
  keywords: string
): BreadcrumbsSchema {
  const listItems = [];
  if (Object.keys(address).length) {
    if (address.country) {
      listItems.push({
        url: locationFor([address.country]),
        name: address.country,
      });
    }
    if (address.state) {
      listItems.push({
        url: locationFor([address.state, address.country]),
        name: address.state,
      });
    }
    if (address.city) {
      listItems.push({
        url: locationFor([address.city, address.state, address.country]),
        name: address.city,
      });
    }
  }
  if (keywords) {
    const query = { keywords };
    const url = `/?${querystring.stringify(query)}`;
    listItems.push({
      url,
      name: `Keywords: ${keywords}`,
    });
  }
  return generateBreadcrumbs(listItems);
}
