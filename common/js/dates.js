/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import _ from 'lodash/string';
import moment from 'moment';
import { intlShape } from 'react-intl';

// TODO: combine this with mobile's formats.js
export const weekdayDateTime = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' };

export function formatStartEnd(startString: string, endString: string, intl: intlShape) {
  const textFields = [];
  const now = moment(intl.now());
  const start = moment(startString, moment.ISO_8601);
  const formattedStart = _.upperFirst(intl.formatDate(start.toDate(), weekdayDateTime));
  if (endString) {
    const end = moment(endString, moment.ISO_8601);
    const duration = end.diff(start);
    if (duration > moment.duration(1, 'days')) {
      const formattedEnd = _.upperFirst(intl.formatDate(end, weekdayDateTime));
      textFields.push(`${formattedStart} - \n${formattedEnd}`);
    } else {
      const formattedEndTime = intl.formatTime(end);
      textFields.push(`${formattedStart} - ${formattedEndTime}`);
    }
    const relativeDuration = moment.duration(duration).humanize();
    textFields.push(` (${relativeDuration})`);
  } else {
    textFields.push(formattedStart);
  }
  // Ensure we do some sort of timer refresh update on this
  const relativeStart = start.diff(now);
  if (relativeStart > 0 && relativeStart < moment.duration(2, 'weeks')) {
    const relativeStartOffset = _.upperFirst(moment.duration(relativeStart).humanize(true));
    textFields.push('\n');
    textFields.push(relativeStartOffset);
  }
  return textFields.join('');
}
