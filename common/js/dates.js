/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import upperFirst from 'lodash/upperFirst';
import moment from 'moment';
import { intlShape } from 'react-intl';

// TODO: combine this with mobile's formats.js
export const weekdayDate = {
  weekday: 'long',
  month: 'long',
  day: 'numeric',
};
export const weekdayDateWithYear = {
  year: 'numeric',
  weekday: 'long',
  month: 'long',
  day: 'numeric',
};
export const weekdayTime = { hour: 'numeric', minute: 'numeric' };
export const weekdayDateTime = {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  hour: 'numeric',
  minute: 'numeric',
};

export function formatStartDateOnly(startString: string, intl: intlShape) {
  const now = moment(intl.now());
  const start = moment(startString, moment.ISO_8601);
  const diff = start.diff(now);
  let format = weekdayDate;
  // Use a year for faraway dates
  if (diff < 0 || diff > moment.duration(6, 'months')) {
    format = weekdayDateWithYear;
  }
  return upperFirst(intl.formatDate(start.toDate(), format));
}

export function formatStartTime(startString: string, intl: intlShape) {
  const start = moment(startString, moment.ISO_8601);
  const formattedStartTime = intl.formatTime(start);
  return formattedStartTime;
}

export function formatStartEnd(
  startString: string,
  endString: ?string,
  intl: intlShape
) {
  const textFields = [];
  const now = moment(intl.now());
  const start = moment(startString, moment.ISO_8601);
  const formattedStart = upperFirst(
    intl.formatDate(start.toDate(), weekdayDateTime)
  );
  if (endString) {
    const end = moment(endString, moment.ISO_8601);
    const duration = end.diff(start);
    if (duration > moment.duration(1, 'days')) {
      const formattedEnd = upperFirst(intl.formatDate(end, weekdayDateTime));
      textFields.push(`${formattedStart} - \n${formattedEnd}`);
    } else {
      const formattedEndTime = intl.formatTime(end);
      textFields.push(`${formattedStart} - ${formattedEndTime}`);
    }
    const relativeDuration = humanizeDuration(duration);
    textFields.push(` (${relativeDuration})`);
  } else {
    textFields.push(formattedStart);
  }
  // Ensure we do some sort of timer refresh update on this
  const relativeStart = start.diff(now);
  if (relativeStart > 0 && relativeStart < moment.duration(2, 'weeks')) {
    const relativeStartOffset = upperFirst(
      moment.duration(relativeStart).humanize(true)
    );
    textFields.push('\n');
    textFields.push(relativeStartOffset);
  }
  return textFields.join('');
}

function humanizeExactly(unitCount, unitName) {
  const locale = moment.localeData();
  const withoutSuffix = true;
  const isFuture = true;
  let possiblyPluralizedUnitName = unitName;
  if (unitCount > 1) {
    possiblyPluralizedUnitName = unitName + unitName; // double it up
  }
  return locale.relativeTime(
    unitCount,
    withoutSuffix,
    possiblyPluralizedUnitName,
    isFuture
  );
}

function humanizeDuration(eventDuration) {
  // We don't use .humanize(), because 90 minutes => "2 hours"
  // We also don't use piecemeal humanize() strings concatenation,
  // because moment.duration(50, 'minutes').humanize() => "an hour"
  // So instead we call the locale formatting functions directly, piecemeal.
  const eventMDuration = moment.duration(eventDuration);
  const eventDurationBits = [];
  if (eventMDuration.days() > 0) {
    eventDurationBits.push(humanizeExactly(eventMDuration.days(), 'd'));
  }
  if (eventMDuration.hours() > 0) {
    eventDurationBits.push(humanizeExactly(eventMDuration.hours(), 'h'));
  }
  if (eventMDuration.minutes() > 0) {
    eventDurationBits.push(humanizeExactly(eventMDuration.minutes(), 'm'));
  }

  return eventDurationBits.join(' ');
}
