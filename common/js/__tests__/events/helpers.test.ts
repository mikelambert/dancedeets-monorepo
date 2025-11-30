/**
 * Unit tests for events/helpers.ts
 */

import { SearchEvent, JSONObject } from '../../events/models';
import { expandResults, groupEventsByStartDate } from '../../events/helpers';

// Mock intl for groupEventsByStartDate
const mockIntl = {
  locale: 'en',
  formatMessage: (msg: { id: string; defaultMessage?: string }) => msg.defaultMessage || msg.id,
  formatDate: (date: Date, options?: any) => {
    // Simple date formatting for tests
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    });
  },
  formatTime: (date: Date, options?: any) => {
    const d = new Date(date);
    return d.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    });
  },
} as any;

describe('expandResults', () => {
  const createSearchEvent = (overrides: Partial<JSONObject> = {}): JSONObject => ({
    id: 'event123',
    name: 'Test Event',
    slugged_name: 'test-event',
    start_time: '2024-06-15T20:00:00-07:00',
    venue: {
      name: 'Test Venue',
      address: {
        city: 'LA',
        state: 'CA',
        country: 'USA',
        countryCode: 'US',
      },
    },
    annotations: {
      categories: ['Dance'],
      keywords: [],
    },
    ...overrides,
  });

  it('should return events unchanged when no event_times', () => {
    const events = [
      new SearchEvent(createSearchEvent({ id: 'event1' })),
      new SearchEvent(createSearchEvent({ id: 'event2' })),
    ];
    const result = expandResults(events, SearchEvent);
    expect(result).toHaveLength(2);
    expect(result[0].id).toBe('event1');
    expect(result[1].id).toBe('event2');
  });

  it('should expand events with event_times', () => {
    const eventWithTimes = new SearchEvent(createSearchEvent({
      id: 'weekly-event',
      name: 'Weekly Dance Class',
      event_times: [
        { start_time: '2024-06-01T19:00:00', end_time: '2024-06-01T21:00:00' },
        { start_time: '2024-06-08T19:00:00', end_time: '2024-06-08T21:00:00' },
        { start_time: '2024-06-15T19:00:00', end_time: '2024-06-15T21:00:00' },
      ],
    }));
    const result = expandResults([eventWithTimes], SearchEvent);
    expect(result.length).toBe(3);
    expect(result[0].start_time).toBe('2024-06-01T19:00:00');
    expect(result[1].start_time).toBe('2024-06-08T19:00:00');
    expect(result[2].start_time).toBe('2024-06-15T19:00:00');
  });

  it('should mark expanded events with had_event_times', () => {
    const eventWithTimes = new SearchEvent(createSearchEvent({
      id: 'weekly-event',
      event_times: [
        { start_time: '2024-06-01T19:00:00', end_time: '2024-06-01T21:00:00' },
      ],
    }));
    const result = expandResults([eventWithTimes], SearchEvent);
    expect(result[0].had_event_times).toBe(true);
  });

  it('should handle empty array', () => {
    const result = expandResults([], SearchEvent);
    expect(result).toEqual([]);
  });

  it('should handle mixed events', () => {
    const regularEvent = new SearchEvent(createSearchEvent({ id: 'regular' }));
    const weeklyEvent = new SearchEvent(createSearchEvent({
      id: 'weekly',
      event_times: [
        { start_time: '2024-06-01T19:00:00', end_time: '2024-06-01T21:00:00' },
        { start_time: '2024-06-08T19:00:00', end_time: '2024-06-08T21:00:00' },
      ],
    }));
    const result = expandResults([regularEvent, weeklyEvent], SearchEvent);
    expect(result.length).toBe(3); // 1 regular + 2 expanded
  });
});

describe('groupEventsByStartDate', () => {
  const createSearchEvent = (id: string, startTime: string): SearchEvent => {
    return new SearchEvent({
      id,
      name: `Event ${id}`,
      slugged_name: `event-${id}`,
      start_time: startTime,
      venue: {
        name: 'Test',
        address: { city: 'LA', state: 'CA', country: 'USA', countryCode: 'US' },
      },
      annotations: { categories: [], keywords: [] },
    });
  };

  it('should group events by date', () => {
    const events = [
      createSearchEvent('1', '2024-06-15T10:00:00'),
      createSearchEvent('2', '2024-06-15T14:00:00'),
      createSearchEvent('3', '2024-06-16T18:00:00'),
    ];
    const groups = groupEventsByStartDate(mockIntl, events);
    expect(groups.length).toBe(2);
    expect(groups[0].events.length).toBe(2);
    expect(groups[1].events.length).toBe(1);
  });

  it('should return empty array for empty input', () => {
    const groups = groupEventsByStartDate(mockIntl, []);
    expect(groups).toEqual([]);
  });

  it('should handle single event', () => {
    const events = [createSearchEvent('1', '2024-06-15T10:00:00')];
    const groups = groupEventsByStartDate(mockIntl, events);
    expect(groups.length).toBe(1);
    expect(groups[0].events.length).toBe(1);
  });

  it('should preserve event order within groups', () => {
    const events = [
      createSearchEvent('morning', '2024-06-15T09:00:00'),
      createSearchEvent('afternoon', '2024-06-15T14:00:00'),
      createSearchEvent('evening', '2024-06-15T20:00:00'),
    ];
    const groups = groupEventsByStartDate(mockIntl, events);
    expect(groups[0].events[0].id).toBe('morning');
    expect(groups[0].events[1].id).toBe('afternoon');
    expect(groups[0].events[2].id).toBe('evening');
  });
});
