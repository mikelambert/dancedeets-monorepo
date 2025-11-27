/**
 * Copyright 2016 DanceDeets.
 */

import { formatStartDateOnly } from '../dates';
import { BaseEvent, EventRsvpList, JSONObject } from './models';
import messages from './messages';

// Simple type for react-intl's intl object - using 'unknown' for formatTime to be compatible with react-intl
interface IntlShape {
  now(): number;
  formatMessage(
    descriptor: { id: string; defaultMessage: string },
    values?: Record<string, string | number>
  ): string;
  formatDate(date: Date, options?: Intl.DateTimeFormatOptions): string;
  formatTime(date: unknown): string;
}

export function formatAttending(
  intl: IntlShape,
  rsvp: EventRsvpList
): string | null {
  if (rsvp.attending_count) {
    if (rsvp.maybe_count) {
      return intl.formatMessage(messages.attendingMaybeCount, {
        attendingCount: rsvp.attending_count,
        maybeCount: rsvp.maybe_count,
      });
    } else {
      return intl.formatMessage(messages.attendingCount, {
        attendingCount: rsvp.attending_count,
      });
    }
  }
  return null;
}

export function groupEventsByStartDate<T extends BaseEvent>(
  intl: IntlShape,
  events: Array<T>
): Array<{ header: string; events: Array<T> }> {
  const results: Array<{ header: string; events: Array<T> }> = [];
  let currentDate: string | null = null;
  events.forEach(event => {
    const eventStartDate = formatStartDateOnly(
      event.getListDateMoment({ timezone: false }),
      intl
    );
    if (eventStartDate !== currentDate) {
      results.push({ header: eventStartDate, events: [] });
      currentDate = eventStartDate;
    }
    results[results.length - 1].events.push(event);
  });
  return results;
}

type BaseEventConstructor = new (data: JSONObject) => BaseEvent;

export function expandResults(
  events: Array<BaseEvent>,
  EventClass: BaseEventConstructor
): Array<BaseEvent> {
  const newEvents: Array<BaseEvent> = [];
  for (const event of events) {
    if (event.event_times) {
      for (const eventTime of event.event_times) {
        const copiedEvent = new EventClass(event as unknown as JSONObject);
        copiedEvent.start_time = eventTime.start_time;
        copiedEvent.end_time = eventTime.end_time;
        copiedEvent.event_times = null;
        copiedEvent.had_event_times = true;
        newEvents.push(copiedEvent);
      }
    } else {
      newEvents.push(event);
    }
  }
  return newEvents;
}
