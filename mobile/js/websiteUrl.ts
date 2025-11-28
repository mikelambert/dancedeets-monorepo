/**
 * Copyright 2016 DanceDeets.
 */

import { Url } from 'url';

interface ParsedUrl {
  pathname: string;
  query: {
    location?: string;
    keywords?: string;
  };
}

export function canHandleUrl(url: string | null | undefined): boolean {
  if (url) {
    const websiteUrl = new WebsiteUrl(url);
    if (websiteUrl.canHandleUrl()) {
      return true;
    }
  }
  return false;
}

export default class WebsiteUrl {
  url: ParsedUrl | null;

  constructor(url: string) {
    this.url = url ? new Url().parse(url, true) as ParsedUrl : null;
  }

  isEventUrl(): boolean {
    return !!(
      this.url &&
      this.url.pathname.startsWith('/events/') &&
      !this.url.pathname.startsWith('/events/relevant')
    );
  }

  eventId(): string {
    if (!this.url || !this.isEventUrl()) {
      const url = this.url || 'null';
      throw new Error(`Not a valid event url: ${url}`);
    }
    const pathname = this.url.pathname;
    const elems = pathname.split('/');
    if (elems[1] !== 'events') {
      throw new Error(`Confusing pathname: ${pathname}`);
    }
    return elems[2];
  }

  isSearchUrl(): boolean {
    return this.url
      ? !!(this.url.query.location || this.url.query.keywords)
      : false;
  }

  canHandleUrl(): boolean {
    return this.isEventUrl() || this.isSearchUrl();
  }

  location(): string | undefined {
    if (!this.url || !this.isSearchUrl()) {
      const url = this.url || 'null';
      throw new Error(`Not a valid search url: ${url}`);
    }
    return this.url.query.location;
  }

  keywords(): string | undefined {
    if (!this.url || !this.isSearchUrl()) {
      const url = this.url || 'null';
      throw new Error(`Not a valid search url: ${url}`);
    }
    return this.url.query.keywords;
  }
}
