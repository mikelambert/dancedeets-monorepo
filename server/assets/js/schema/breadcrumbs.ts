/**
 * Copyright 2016 DanceDeets.
 */

import querystring from 'querystring';
import { SearchEvent, Event } from 'dancedeets-common/js/events/models';
import type { Address } from 'dancedeets-common/js/events/search';

interface ListItem {
  url: string;
  name: string;
}

interface SchemaListItem {
  '@type': string;
  position: number;
  item: {
    '@id': string;
    name: string;
  };
}

interface BreadcrumbsSchema {
  '@context': string;
  '@type': string;
  itemListElement: SchemaListItem[];
}

function locationFor(components: (string | undefined | null)[]): string {
  const query = { location: components.filter(x => x).join(', ') };
  return `/?${querystring.stringify(query)}`;
}

function generateBreadcrumbs(listItems: ListItem[]): BreadcrumbsSchema {
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
): BreadcrumbsSchema | null {
  const listItems: ListItem[] = [];
  const { address } = event.venue;
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
): BreadcrumbsSchema | null {
  const listItems: ListItem[] = [];
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
  return listItems.length ? generateBreadcrumbs(listItems) : null;
}
