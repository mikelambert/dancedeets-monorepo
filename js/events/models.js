/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import url from 'url';

type JSON = string | number | boolean | null | JSONObject | JSONArray;
type JSONObject = { [key:string]: JSON };
type JSONArray = Array<JSON>;
type MiniImageProp = {
  uri: string;
  width: number;
  height: number;
};

export type Cover = {
  source: string,
  height: number,
  width: number,
};

export class JsonDerivedObject {
  constructor(data: any) {
    for (var attr in data) {
      if (data.hasOwnProperty(attr)) {
        (this: any)[attr] = data[attr];
      }
    }
  }
}

export class Venue extends JsonDerivedObject {
  geocode: {
    latitude: number,
    longitude: number,
  };
  address: ?{
    street: string,
    city: string,
    state: string,
    zip: string,
    country: string,
  };
  name: string;
  id: string;

  fullAddress() {
    if (this.address) {
      return [this.name, this.address.street, this.address.city, this.address.state, this.address.country].filter((x) => x).join(', ');
    } else {
      return this.name;
    }
  }

  cityState() {
    if (this.address) {
      return [this.address.city, this.address.state].filter((x) => x).join(', ');
    } else {
      return null;
    }
  }

  cityStateCountry() {
    if (this.address) {
      return [this.address.city, this.address.state, this.address.country].filter((x) => x).join(', ');
    } else {
      return null;
    }
  }
}

export type Admin = {
  id: string;
  name: string;
};

export class Event extends JsonDerivedObject {
  id: string;
  name: string;
  description: string;
  start_time: string;
  end_time: string;
  source: {
    url: string,
    name: string,
  };
  rsvp: {
    attendingCount: number,
    maybeCount: number,
  };
  picture: ?Cover;
  venue: Venue;
  annotations: {
    categories: Array<string>,
    creation: {
      creator: ?string,
      method: string,
      time: string,
    },
  };
  admins: Array<Admin>;
  ticket_uri: string;

  constructor(eventData: JSONObject) {
    super(eventData);
    this.venue = new Venue(eventData['venue']);
  }

  getResponsiveFlyers() {
    if (!this.picture) {
      return [];
    }
    const ratio = this.picture.width / this.picture.height;
    const parsedSource = url.parse(this.picture.source, true);
    const results = [320, 480, 720, 1080, 1440].map((x) => {
      // Careful! We are re-using parsedSource here.
      // If we do more complex things, we may need to create and modify copies...
      parsedSource.query.width = x;
      const result = {
        uri: url.format(parsedSource),
        width: x,
        height: Math.floor(x / ratio),
      };
      return result;
    });
    return results;
  }

  getUrl() {
    return 'http://www.dancedeets.com/events/' + this.id + '/';
  }
}
