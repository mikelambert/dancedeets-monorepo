/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { intlShape } from 'react-intl';
import type { EventRsvpList } from './models';
import { messages } from './messages';

export function formatAttending(intl: intlShape, rsvp: EventRsvpList) {
  if (rsvp.attending_count) {
    if (rsvp.maybe_count) {
      return intl.formatMessage(messages.attendingMaybeCount, {
        attendingCount: rsvp.attending_count,
        maybeCount: rsvp.maybe_count,
      });
    } else {
      return intl.formatMessage(messages.attendingCount, { attendingCount: rsvp.maybe_count });
    }
  }
  return null;
}
