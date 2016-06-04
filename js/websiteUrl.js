/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import urllib from 'url';

export default class WebsiteUrl {
  url: ?Object;

  constructor(url: string) {
    this.url = url ? urllib.parse(url, true) : null;
  }

  isEventUrl() {
    return this.url && this.url.pathname.startsWith('/event/');
  }

  eventId() {
    if (!this.url || !this.isEventUrl()) {
      return null;
    }
    const pathname = this.url.pathname;
    const elems = pathname.split('/');
    if (elems[1] != 'event') {
      throw 'Confusing pathname: ' + pathname;
    }
    return elems[2];
  }

  isSearchUrl() {
    return this.url ? (this.url.query.location || this.url.query.keywords) : false;
  }

  location() {
    if (!this.url || !this.isSearchUrl()) {
      return null;
    }
    return this.url.query.location;
  }

  keywords() {
    if (!this.url || !this.isSearchUrl()) {
      return null;
    }
    return this.url.query.keywords;
  }
}
