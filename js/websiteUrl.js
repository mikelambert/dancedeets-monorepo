/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import urllib from 'url';

export default class WebsiteUrl {
  url: Object;

  constructor(url: string) {
    this.url = urllib.parse(url, true);
  }

  isEventUrl() {
    return this.url.pathname.startsWith('/event/');
  }

  eventId() {
    if (!this.isEventUrl()) {
      return null;
    }
    const elems = this.url.pathname.split('/');
    if (elems[1] != 'event') {
      throw 'Confusing pathname: ' + this.url.pathname;
    }
    return elems[2];
  }

  isSearchUrl() {
    return (this.url.query.location || this.url.query.keywords);
  }

  location() {
    return this.url.query.location;
  }

  keywords() {
    return this.url.query.keywords;
  }
}
