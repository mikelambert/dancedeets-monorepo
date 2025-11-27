/**
 * Copyright 2016 DanceDeets.
 */

import moment, { Moment } from 'moment';
import { addUrlArgs } from '../util/url';

type JSON = string | number | boolean | null | JSONObject | JSONArray;
export type JSONObject = { [key: string]: JSON };
type JSONArray = Array<JSON>;

export interface ImageWithSizes {
  uri: string;
  width: number;
  height: number;
}

const squareImageSize = 180;

export interface ImageOptionalSizes {
  uri: string;
  height: number | null | undefined;
  width: number | null | undefined;
}

export class JsonDerivedObject {
  constructor(data: Record<string, unknown>) {
    Object.keys(data).forEach(attr => {
      (this as Record<string, unknown>)[attr] = data[attr];
    });
  }
}

export class Venue extends JsonDerivedObject {
  geocode?: {
    latitude: number;
    longitude: number;
  } | null;
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zip?: string;
    country: string;
    countryCode: string;
  } | null;
  name?: string | null;
  id?: string | null;

  fullAddress(seperator: string = ', '): string | null | undefined {
    if (this.address) {
      return [this.name, this.address.street, this.cityStateCountry()]
        .filter(x => x)
        .join(seperator);
    } else {
      return this.name;
    }
  }

  streetCityStateCountry(seperator: string = ', '): string | null {
    if (this.address) {
      return [this.address.street, this.cityStateCountry()]
        .filter(x => x)
        .join(seperator);
    } else {
      return null;
    }
  }

  cityState(seperator: string = ', '): string | null {
    if (this.address) {
      return [this.address.city, this.address.state]
        .filter(x => x)
        .join(seperator);
    } else {
      return null;
    }
  }

  cityStateCountry(separator: string = ', '): string | null {
    if (this.address) {
      return [this.address.city, this.address.state, this.address.country]
        .filter(x => x)
        .join(separator);
    } else {
      return null;
    }
  }
}

export interface Admin {
  id: string;
  name: string;
}

export interface EventRsvpList {
  attending_count: number;
  maybe_count: number;
}

export class Picture extends JsonDerivedObject {
  source!: string;
  height!: number;
  width!: number;

  getCroppedCover(
    width: number | null | undefined,
    height: number | null | undefined,
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

  getFlyer(dimensions: { width?: number; height?: number }): ImageWithSizes {
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

export interface EventTime {
  start_time: string;
  end_time: string;
}

export class BaseEvent extends JsonDerivedObject {
  id!: string;
  name!: string;
  slugged_name!: string; // eslint-disable-line camelcase
  start_time!: string; // eslint-disable-line camelcase
  end_time?: string | null; // eslint-disable-line camelcase
  venue!: Venue;
  picture?: Picture | null;
  event_times?: Array<EventTime> | null; // eslint-disable-line camelcase
  had_event_times?: boolean | null; // eslint-disable-line camelcase

  constructor(eventData: JSONObject) {
    super(eventData as Record<string, unknown>);
    this.venue = new Venue(eventData.venue as Record<string, unknown>);
    this.picture = eventData.picture
      ? new Picture(eventData.picture as Record<string, unknown>)
      : null;
  }

  getRelativeUrl(): string {
    let url = `/events/${this.id}/${this.slugged_name}`;
    if (this.had_event_times) {
      url += `#${this.start_time}`;
    }
    return url;
  }

  getUrl(args?: Record<string, string | number | boolean | null | undefined> | null): string {
    const url = `https://www.dancedeets.com${this.getRelativeUrl()}`;
    return addUrlArgs(url, args);
  }

  getCroppedCover(
    width: number | null | undefined,
    height: number | null | undefined,
    index?: number
  ): ImageOptionalSizes | null {
    if (!this.picture) {
      return null;
    }
    return this.picture
      ? this.picture.getCroppedCover(width, height, index)
      : null;
  }

  startTime({ timezone }: { timezone: boolean }): string {
    if (timezone) {
      return this.start_time;
    } else {
      return this.start_time.substr(0, 19);
    }
  }

  endTime({ timezone }: { timezone: boolean }): string | null {
    if (!this.end_time) {
      return null;
    }
    if (timezone) {
      return this.end_time;
    } else {
      return this.end_time.substr(0, 19);
    }
  }

  getStartMoment({ timezone }: { timezone: boolean }): Moment {
    return moment(this.startTime({ timezone }));
  }

  getEndMoment({ timezone }: { timezone: boolean }): Moment | null {
    if (!this.end_time) {
      return null;
    }
    return moment(this.endTime({ timezone }));
  }

  getEndMomentWithFallback({ timezone }: { timezone: boolean }): Moment {
    const endMoment = this.getEndMoment({ timezone });
    if (endMoment) {
      return endMoment;
    } else {
      return this.getStartMoment({ timezone }).add(1.5, 'hours');
    }
  }

  getListDateMoment({ timezone }: { timezone: boolean }): Moment {
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

  getFlyer(dimensions: { width?: number; height?: number }): ImageWithSizes | null {
    return this.picture ? this.picture.getFlyer(dimensions) : null;
  }

  getSquareFlyer(): ImageWithSizes | null {
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
  rsvp?: EventRsvpList | null;
  annotations!: {
    categories: Array<string>;
    keywords: Array<string>;
  };
}

export interface Post {
  message: string;
  link?: string;
  created_time: string;
  from?: { id: string; name?: string };
}

export class Event extends BaseEvent {
  description!: string;
  source!: {
    url: string;
    name: string;
  };
  rsvp?: EventRsvpList | null;
  override venue!: Venue;
  annotations!: {
    categories: Array<string>;
    creation: {
      creator?: string | null;
      creatorName?: string | null;
      method: string;
      time: string;
    };
  };
  language!: string;
  admins!: Array<Admin>;
  posts!: Array<Post>;
  ticket_uri!: string; // eslint-disable-line camelcase
  extraImageCount!: number;
}
