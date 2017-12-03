/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import moment from 'moment';
import { addUrlArgs } from '../util/url';

type JSON = string | number | boolean | null | JSONObject | JSONArray;
export type JSONObject = { [key: string]: JSON };
type JSONArray = Array<JSON>;

export type ImageWithSizes = {
  uri: string,
  width: number,
  height: number,
};

const squareImageSize = 180;

export type ImageOptionalSizes = {
  uri: string,
  height: ?number,
  width: ?number,
};

export class JsonDerivedObject {
  constructor(data: any) {
    Object.keys(data).forEach(attr => {
      (this: any)[attr] = data[attr];
    });
  }
}

export class Venue extends JsonDerivedObject {
  geocode: ?{
    latitude: number,
    longitude: number,
  };
  address: ?{
    street?: string,
    city?: string,
    state?: string,
    zip?: string,
    country: string,
    countryCode: string,
  };
  name: ?string;
  id: ?string;

  fullAddress(seperator: string = ', ') {
    if (this.address) {
      return [this.name, this.address.street, this.cityStateCountry()]
        .filter(x => x)
        .join(seperator);
    } else {
      return this.name;
    }
  }

  streetCityStateCountry(seperator: string = ', ') {
    if (this.address) {
      return [this.address.street, this.cityStateCountry()]
        .filter(x => x)
        .join(seperator);
    } else {
      return null;
    }
  }

  cityState(seperator: string = ', ') {
    if (this.address) {
      return [this.address.city, this.address.state]
        .filter(x => x)
        .join(seperator);
    } else {
      return null;
    }
  }

  cityStateCountry(separator: string = ', ') {
    if (this.address) {
      return [this.address.city, this.address.state, this.address.country]
        .filter(x => x)
        .join(separator);
    } else {
      return null;
    }
  }
}

export type Admin = {
  id: string,
  name: string,
};

export type EventRsvpList = {
  attending_count: number,
  maybe_count: number,
};

export class Picture extends JsonDerivedObject {
  source: string;
  height: number;
  width: number;

  getCroppedCover(
    width: ?number,
    height: ?number,
    index?: number
  ): ImageOptionalSizes {
    let { source } = this;
    if (index) {
      source += `/${index}`;
    }
    return {
      uri: addUrlArgs(source, { width, height }),
      width,
      height,
    };
  }

  getFlyer(dimensions: { width?: number, height?: number }): ImageWithSizes {
    let { width, height } = dimensions;
    if (!width && !height) {
      return {
        uri: this.source,
        width: this.width,
        height: this.height,
      };
    } else {
      const ratio = this.width / this.height;
      if (!height && width) {
        height = Math.floor(width / ratio);
      } else if (!width && height) {
        width = Math.floor(height / ratio);
      }
      const cover = this.getCroppedCover(width, height);
      if (!cover.width || !cover.height) {
        throw new Error('Unexpectedly got cover with');
      }
      return {
        uri: cover.uri,
        width: cover.width,
        height: cover.height,
      };
    }
  }
}

export class BaseEvent extends JsonDerivedObject {
  id: string;
  name: string;
  slugged_name: string; // eslint-disable-line camelcase
  start_time: string; // eslint-disable-line camelcase
  end_time: ?string; // eslint-disable-line camelcase
  venue: Venue;
  picture: ?Picture;
  event_times: ?Array<EventTime>; // eslint-disable-line camelcase
  had_event_times: ?boolean; // eslint-disable-line camelcase

  constructor(eventData: JSONObject) {
    super(eventData);
    this.venue = new Venue(eventData.venue);
    this.picture = eventData.picture ? new Picture(eventData.picture) : null;
  }

  getRelativeUrl() {
    let url = `/events/${this.id}/${this.slugged_name}`;
    if (this.had_event_times) {
      url += `#${this.start_time}`;
    }
    return url;
  }

  getUrl(args: ?Object) {
    const url = `https://www.dancedeets.com${this.getRelativeUrl()}`;
    return addUrlArgs(url, args);
  }

  getCroppedCover(
    width: ?number,
    height: ?number,
    index?: number
  ): ?ImageOptionalSizes {
    if (!this.picture) {
      return null;
    }
    return this.picture
      ? this.picture.getCroppedCover(width, height, index)
      : null;
  }

  startTime({ timezone }: { timezone: boolean }) {
    if (timezone) {
      return this.start_time;
    } else {
      return this.start_time.substr(0, 19);
    }
  }

  endTime({ timezone }: { timezone: boolean }) {
    if (!this.end_time) {
      return null;
    }
    if (timezone) {
      return this.end_time;
    } else {
      return this.end_time.substr(0, 19);
    }
  }

  getStartMoment({ timezone }: { timezone: boolean }): moment {
    return moment(this.startTime({ timezone }));
  }

  getEndMoment({ timezone }: { timezone: boolean }): ?moment {
    if (!this.end_time) {
      return null;
    }
    return moment(this.endTime({ timezone }));
  }

  getEndMomentWithFallback({ timezone }: { timezone: boolean }): moment {
    const endMoment = this.getEndMoment({ timezone });
    if (endMoment) {
      return endMoment;
    } else {
      return this.getStartMoment({ timezone }).add(1.5, 'hours');
    }
  }

  getListDateMoment({ timezone }: { timezone: boolean }): moment {
    const startFinalTimezone = this.getStartMoment({ timezone });
    const start = this.getStartMoment({ timezone: true });
    const end = this.getEndMoment({ timezone: true });
    if (!end) {
      return startFinalTimezone;
    }
    // This code can get tricky. It uses moment(), which has an embedded timezone.
    // So anytime we compare it with something, we should also be using timezones (start, end).
    // But this function may be asked to return a timezone-less time.
    // So when we return something, we return startFinalTimezone (or something computed off that),
    // to ensure we meet our contract.
    // This is all super-important since moment() differs between server and client,
    // and any differences in rendering between them can cause major DOM screwups.
    const now = moment();
    if (now.isBefore(start)) {
      return startFinalTimezone;
    }
    // If the event looks to be a weekly event (ends <24 hours after it begins, plus N weeks),
    // then return the next instance of that weekly event as our ListDate.
    const duration = end.diff(start);
    const durationMinusWeeks =
      duration % moment.duration(1, 'week').asMilliseconds();
    const lessThan24Hours =
      durationMinusWeeks < moment.duration(1, 'day').asMilliseconds();
    if (lessThan24Hours) {
      // Assume it's a weekly event!
      const nowDiff = now.diff(start);
      const weeksUntilNow =
        nowDiff / moment.duration(1, 'week').asMilliseconds();
      const nextStart = startFinalTimezone
        .clone()
        .add(Math.ceil(weeksUntilNow), 'week');
      if (nextStart.isBefore(end)) {
        return nextStart;
      }
    }
    return startFinalTimezone;
  }

  getFlyer(dimensions: { width?: number, height?: number }): ?ImageWithSizes {
    return this.picture ? this.picture.getFlyer(dimensions) : null;
  }

  getSquareFlyer(): ?ImageWithSizes {
    return this.picture
      ? this.picture.getFlyer({
          width: squareImageSize,
          height: squareImageSize,
        })
      : null;
  }

  getResponsiveFlyers(): Array<ImageWithSizes> {
    const { picture } = this;
    return picture
      ? [320, 480, 720, 1080, 1440].map(width => picture.getFlyer({ width }))
      : [];
  }
}

export class SearchEvent extends BaseEvent {
  rsvp: ?EventRsvpList;
  annotations: {
    categories: Array<string>,
    keywords: Array<string>,
  };
}

export type Post = Object;

export type EventTime = {
  start_time: string,
  end_time: string,
};

export class Event extends BaseEvent {
  description: string;
  source: {
    url: string,
    name: string,
  };
  rsvp: ?EventRsvpList;
  venue: Venue;
  annotations: {
    categories: Array<string>,
    creation: {
      creator: ?string,
      creatorName: ?string,
      method: string,
      time: string,
    },
  };
  language: string;
  admins: Array<Admin>;
  posts: Array<Post>;
  ticket_uri: string; // eslint-disable-line camelcase
  extraImageCount: number;
}
