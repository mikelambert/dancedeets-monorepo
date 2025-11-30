/**
 * Unit tests for events/models.ts
 */

import moment from 'moment';
import { Venue, BaseEvent, SearchEvent, Event, Picture, JSONObject } from '../../events/models';

describe('Venue', () => {
  const basicVenueData: JSONObject = {
    id: '12345',
    name: 'Test Venue',
    address: {
      street: '123 Main St',
      city: 'New York',
      state: 'NY',
      country: 'USA',
      countryCode: 'US',
    },
    geocode: {
      latitude: 40.7128,
      longitude: -74.006,
    },
  };

  describe('cityStateCountry', () => {
    it('should return city, state, and country with default separator', () => {
      const venue = new Venue(basicVenueData);
      expect(venue.cityStateCountry()).toBe('New York, NY, USA');
    });

    it('should return city, state, and country with custom separator', () => {
      const venue = new Venue(basicVenueData);
      expect(venue.cityStateCountry(' - ')).toBe('New York - NY - USA');
    });

    it('should return null when address is missing', () => {
      const venue = new Venue({ name: 'Test' });
      expect(venue.cityStateCountry()).toBeNull();
    });

    it('should filter out missing parts', () => {
      const venue = new Venue({
        address: {
          city: 'Tokyo',
          country: 'Japan',
          countryCode: 'JP',
        },
      });
      expect(venue.cityStateCountry()).toBe('Tokyo, Japan');
    });
  });

  describe('cityState', () => {
    it('should return city and state', () => {
      const venue = new Venue(basicVenueData);
      expect(venue.cityState()).toBe('New York, NY');
    });

    it('should return null when address is missing', () => {
      const venue = new Venue({ name: 'Test' });
      expect(venue.cityState()).toBeNull();
    });
  });

  describe('fullAddress', () => {
    it('should return full address with name', () => {
      const venue = new Venue(basicVenueData);
      expect(venue.fullAddress()).toBe('Test Venue, 123 Main St, New York, NY, USA');
    });

    it('should return just name if no address', () => {
      const venue = new Venue({ name: 'Test Venue' });
      expect(venue.fullAddress()).toBe('Test Venue');
    });
  });

  describe('streetCityStateCountry', () => {
    it('should return street and cityStateCountry', () => {
      const venue = new Venue(basicVenueData);
      expect(venue.streetCityStateCountry()).toBe('123 Main St, New York, NY, USA');
    });

    it('should return null when address is missing', () => {
      const venue = new Venue({ name: 'Test' });
      expect(venue.streetCityStateCountry()).toBeNull();
    });
  });
});

describe('Picture', () => {
  const pictureData: JSONObject = {
    source: 'https://example.com/image.jpg',
    width: 800,
    height: 600,
  };

  describe('getCroppedCover', () => {
    it('should return cropped cover with dimensions', () => {
      const picture = new Picture(pictureData);
      const cropped = picture.getCroppedCover(400, 300);
      expect(cropped.uri).toContain('width=400');
      expect(cropped.uri).toContain('height=300');
      expect(cropped.width).toBe(400);
      expect(cropped.height).toBe(300);
    });

    it('should add index to URL when provided', () => {
      const picture = new Picture(pictureData);
      const cropped = picture.getCroppedCover(400, 300, 2);
      expect(cropped.uri).toContain('/2');
    });
  });

  describe('getFlyer', () => {
    it('should return original dimensions when no dimensions specified', () => {
      const picture = new Picture(pictureData);
      const flyer = picture.getFlyer({});
      expect(flyer.width).toBe(800);
      expect(flyer.height).toBe(600);
    });

    it('should calculate height from width', () => {
      const picture = new Picture(pictureData);
      const flyer = picture.getFlyer({ width: 400 });
      expect(flyer.width).toBe(400);
      expect(flyer.height).toBe(300); // 400 / (800/600)
    });

    it('should calculate width from height', () => {
      const picture = new Picture(pictureData);
      const flyer = picture.getFlyer({ height: 300 });
      // width = floor(height / ratio) = floor(300 / (800/600)) = floor(225) = 225
      expect(flyer.width).toBe(225);
      expect(flyer.height).toBe(300);
    });
  });
});

describe('BaseEvent', () => {
  const eventData: JSONObject = {
    id: 'event123',
    name: 'Dance Party',
    slugged_name: 'dance-party',
    start_time: '2024-06-15T20:00:00-07:00',
    end_time: '2024-06-15T23:00:00-07:00',
    venue: {
      name: 'Test Venue',
      address: {
        city: 'Los Angeles',
        state: 'CA',
        country: 'USA',
        countryCode: 'US',
      },
    },
    picture: {
      source: 'https://example.com/event.jpg',
      width: 800,
      height: 600,
    },
  };

  describe('getRelativeUrl', () => {
    it('should return relative URL with id and slugged name', () => {
      const event = new BaseEvent(eventData);
      expect(event.getRelativeUrl()).toBe('/events/event123/dance-party');
    });

    it('should include hash for events with event_times', () => {
      const eventWithTimes = new BaseEvent({
        ...eventData,
        had_event_times: true,
      });
      expect(eventWithTimes.getRelativeUrl()).toContain('#');
    });
  });

  describe('getUrl', () => {
    it('should return full URL', () => {
      const event = new BaseEvent(eventData);
      expect(event.getUrl()).toBe('https://www.dancedeets.com/events/event123/dance-party');
    });

    it('should append query args', () => {
      const event = new BaseEvent(eventData);
      const url = event.getUrl({ utm_source: 'test' });
      expect(url).toContain('utm_source=test');
    });
  });

  describe('getStartMoment', () => {
    it('should return moment without timezone info when timezone is false', () => {
      const event = new BaseEvent(eventData);
      const start = event.getStartMoment({ timezone: false });
      expect(start.format('YYYY-MM-DD')).toBe('2024-06-15');
      expect(start.format('HH:mm')).toBe('20:00');
    });
  });

  describe('getEndMoment', () => {
    it('should return moment for end time', () => {
      const event = new BaseEvent(eventData);
      const end = event.getEndMoment({ timezone: false });
      expect(end).not.toBeNull();
      expect(end?.format('HH:mm')).toBe('23:00');
    });

    it('should return null when no end_time', () => {
      const eventNoEnd = new BaseEvent({
        ...eventData,
        end_time: null,
      });
      expect(eventNoEnd.getEndMoment({ timezone: false })).toBeNull();
    });
  });

  describe('getEndMomentWithFallback', () => {
    it('should return end time when present', () => {
      const event = new BaseEvent(eventData);
      const end = event.getEndMomentWithFallback({ timezone: false });
      expect(end.format('HH:mm')).toBe('23:00');
    });

    it('should return start + 1.5 hours when no end time', () => {
      const eventNoEnd = new BaseEvent({
        ...eventData,
        end_time: null,
      });
      const end = eventNoEnd.getEndMomentWithFallback({ timezone: false });
      expect(end.format('HH:mm')).toBe('21:30'); // 20:00 + 1:30
    });
  });

  describe('getCroppedCover', () => {
    it('should return cropped cover when picture exists', () => {
      const event = new BaseEvent(eventData);
      const cover = event.getCroppedCover(200, 200);
      expect(cover).not.toBeNull();
      expect(cover?.uri).toContain('width=200');
    });

    it('should return null when no picture', () => {
      const eventNoPic = new BaseEvent({
        ...eventData,
        picture: null,
      });
      expect(eventNoPic.getCroppedCover(200, 200)).toBeNull();
    });
  });

  describe('getFlyer', () => {
    it('should return flyer when picture exists', () => {
      const event = new BaseEvent(eventData);
      const flyer = event.getFlyer({ width: 400 });
      expect(flyer).not.toBeNull();
    });

    it('should return null when no picture', () => {
      const eventNoPic = new BaseEvent({
        ...eventData,
        picture: null,
      });
      expect(eventNoPic.getFlyer({ width: 400 })).toBeNull();
    });
  });

  describe('getSquareFlyer', () => {
    it('should return 180x180 flyer', () => {
      const event = new BaseEvent(eventData);
      const flyer = event.getSquareFlyer();
      expect(flyer).not.toBeNull();
      expect(flyer?.width).toBe(180);
      expect(flyer?.height).toBe(180);
    });
  });
});

describe('SearchEvent', () => {
  const searchEventData: JSONObject = {
    id: 'event123',
    name: 'Breaking Battle',
    slugged_name: 'breaking-battle',
    start_time: '2024-07-20T18:00:00-07:00',
    venue: {
      name: 'Studio',
      address: {
        city: 'San Francisco',
        state: 'CA',
        country: 'USA',
        countryCode: 'US',
      },
    },
    annotations: {
      categories: ['Breaking', 'Battle'],
      keywords: ['bboy', 'breaking'],
    },
    rsvp: {
      attending_count: 50,
      maybe_count: 100,
    },
  };

  it('should have annotations with categories and keywords', () => {
    const event = new SearchEvent(searchEventData);
    expect(event.annotations.categories).toEqual(['Breaking', 'Battle']);
    expect(event.annotations.keywords).toEqual(['bboy', 'breaking']);
  });

  it('should have rsvp counts', () => {
    const event = new SearchEvent(searchEventData);
    expect(event.rsvp?.attending_count).toBe(50);
    expect(event.rsvp?.maybe_count).toBe(100);
  });
});

describe('Event', () => {
  const eventData: JSONObject = {
    id: 'event456',
    name: 'Dance Workshop',
    slugged_name: 'dance-workshop',
    start_time: '2024-08-10T14:00:00-07:00',
    end_time: '2024-08-10T17:00:00-07:00',
    description: 'Learn to dance!',
    venue: {
      name: 'Dance Studio',
      address: {
        city: 'Oakland',
        state: 'CA',
        country: 'USA',
        countryCode: 'US',
      },
    },
    source: {
      url: 'https://facebook.com/events/123',
      name: 'Facebook',
    },
    annotations: {
      categories: ['Workshop'],
      creation: {
        method: 'auto',
        time: '2024-07-01T00:00:00Z',
      },
    },
    language: 'en',
    admins: [
      { id: 'admin1', name: 'John Doe' },
    ],
    posts: [],
    ticket_uri: 'https://tickets.example.com',
    extraImageCount: 0,
  };

  it('should have description', () => {
    const event = new Event(eventData);
    expect(event.description).toBe('Learn to dance!');
  });

  it('should have admins', () => {
    const event = new Event(eventData);
    expect(event.admins).toHaveLength(1);
    expect(event.admins[0].name).toBe('John Doe');
  });

  it('should have ticket_uri', () => {
    const event = new Event(eventData);
    expect(event.ticket_uri).toBe('https://tickets.example.com');
  });

  it('should have source info', () => {
    const event = new Event(eventData);
    expect(event.source.name).toBe('Facebook');
  });
});
