/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import messages from './messages';

export function formatDuration(formatMessage: (message: Object, timeData: Object) => string, durationSeconds: number) {
  const hours = Math.floor(durationSeconds / 60 / 60);
  const minutes = Math.floor(durationSeconds / 60) % 60;
  if (durationSeconds > 60 * 60) {
    return formatMessage(messages.timeHoursMinutes, { hours, minutes });
  } else if (durationSeconds > 60) {
    return formatMessage(messages.timeMinutes, { minutes });
  } else {
    const seconds = durationSeconds;
    return formatMessage(messages.timeSeconds, { seconds });
  }
}
