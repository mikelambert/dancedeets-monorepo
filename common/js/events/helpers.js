/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { intlShape } from 'react-intl';
import moment from 'moment';
import upperFirst from 'lodash/upperFirst';
import {
  weekdayDate,
} from '../dates';
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
      return intl.formatMessage(messages.attendingCount, { attendingCount: rsvp.attending_count });
    }
  }
  return null;
}

export function groupEventsByStartDate(intl: intlShape, events) {
  const results = [];
  let currentDate = null;
  events.forEach((event, index) => {
    const eventStart = moment(event.start_time);
    const eventStartDate = upperFirst(intl.formatDate(eventStart.toDate(), weekdayDate));
    if (eventStartDate !== currentDate) {
      results.push({header: eventStartDate, events: []});
      currentDate = eventStartDate;
    }
    results[results.length - 1].events.push(event);
  });
  return results;
}
