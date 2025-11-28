/**
 * Copyright 2016 DanceDeets.
 */

import { FormattedMessage } from 'react-intl';
import messages from './messages';

type MessageDescriptor = FormattedMessage.MessageDescriptor;

type FormatMessageFn = (
  message: MessageDescriptor,
  values?: Record<string, string | number>
) => string;

export function formatDuration(
  formatMessage: FormatMessageFn,
  durationSeconds: number
): string {
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
