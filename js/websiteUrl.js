/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { Url } from 'url';

export default class WebsiteUrl {
  url: ?Url;

  constructor(url: string) {
    this.url = url ? new Url().parse(url, true) : null;
  }

  isEventUrl() {
    return this.url && this.url.pathname.startsWith('/event/');
  }

  eventId(): string {
    if (!this.url || !this.isEventUrl()) {
      throw new Error('Not a valid event url: ' + (this.url || 'null'));
    }
    const pathname = this.url.pathname;
    const elems = pathname.split('/');
    if (elems[1] != 'event') {
      throw new Error('Confusing pathname: ' + pathname);
    }
    return elems[2];
  }

  isSearchUrl() {
    return this.url ? (this.url.query.location || this.url.query.keywords) : false;
  }

  location() {
    if (!this.url || !this.isSearchUrl()) {
      throw new Error('Not a valid search url: ' + (this.url || 'null'));
    }
    return this.url.query.location;
  }

  keywords() {
    if (!this.url || !this.isSearchUrl()) {
      throw new Error('Not a valid search url: ' + (this.url || 'null'));
    }
    return this.url.query.keywords;
  }
}
