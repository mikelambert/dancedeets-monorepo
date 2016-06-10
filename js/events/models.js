/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

type JSON = string | number | boolean | null | JSONObject | JSONArray;
type JSONObject = { [key:string]: JSON };
type JSONArray = Array<JSON>;

import { PixelRatio } from 'react-native';

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
  address: {
    street: string,
    city: string,
    state: string,
    zip: string,
    country: string,
  };
  name: string;
  id: string;

  fullAddress() {
    return [this.name, this.address.street, this.address.city, this.address.state, this.address.country].filter((x) => x).join(', ');
  }

  cityStateCountry() {
    return [this.address.city, this.address.state, this.address.country].filter((x) => x).join(', ');
  }
}

export type Admin = {
  id: string;
  name: string;
};

export class Event extends JsonDerivedObject {
  id: string;
  venue: string;
  picture: string;
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
  cover: {
    cover_id: string,
    images: Array<Cover>,
  };
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

  constructor(eventData: JSONObject) {
    super(eventData);
    this.venue = new Venue(eventData['venue']);
  }

  getImageProps() {
    var source = this.picture;
    var width = 100;
    var height = 100;
    if (this.cover !== null && this.cover.images.length > 0) {
      var image = this.cover.images[0];
      source = image.source;
      width = image.width;
      height = image.height;
    }
    return {source, width, height};
  }

  getImagePropsForWidth(width: number) {
    const rawPixelWidth = PixelRatio.getPixelSizeForLayoutSize(width);
    let bestImageProps = {
      source: this.picture,
      width: 100,
      height: 100,
    };
    if (this.cover !== null && this.cover.images.length > 0) {
      bestImageProps = this.cover.images[0];
      this.cover.images.forEach((i) => {
        // Get the best image that is *smaller* than our screen size in pixels (ie, round down)
        if (bestImageProps.width < i.width && i.width < rawPixelWidth) {
          bestImageProps = i;
        }
      });
    }
    return bestImageProps;
  }

  getUrl() {
    return 'http://www.dancedeets.com/events/' + this.id + '/';
  }
}
