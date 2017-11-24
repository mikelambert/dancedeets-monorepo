/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { intlShape } from 'react-intl';
import { formatStartDateOnly } from '../dates';
import { BaseEvent } from './models';
import type { EventRsvpList } from './models';
import messages from './messages';

export function formatAttending(intl: intlShape, rsvp: EventRsvpList) {
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

export function groupEventsByStartDate<T: BaseEvent>(
  intl: intlShape,
  events: Array<T>
): Array<{ header: string, events: Array<T> }> {
  const results = [];
  let currentDate = null;
  events.forEach((event, index) => {
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

export function expandResults(events, EventClass) {
  const newEvents = [];
  for (const event of events) {
    if (event.event_times) {
      for (const eventTime of event.event_times) {
        const copiedEvent = new EventClass(event);
        copiedEvent.start_time = eventTime.start_time;
        copiedEvent.end_time = eventTime.end_time;
        copiedEvent.event_times = null;
        newEvents.push(copiedEvent);
      }
    } else {
      newEvents.push(event);
    }
  }
  return newEvents;
}
