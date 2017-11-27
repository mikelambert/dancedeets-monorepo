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
  year: 'numeric',
};
export const weekdayTime = { hour: 'numeric', minute: 'numeric' };

function dateIsNearby(date: moment, intl: intlShape) {
  const now = moment(intl.now());
  const diff = date.diff(now);
  return (
    diff > moment.duration(-3, 'months').asMilliseconds() &&
    diff < moment.duration(6, 'months').asMilliseconds()
  );
}

function formatDate(date: moment, intl: intlShape) {
  // Use a year for faraway dates
  const format = { ...weekdayDate };
  // I would like to only show the year on far-away dates
  // but unfortunately, the serverside Intl lacks a
  // year-less long-month-long-weekday formatter,
  // and ends up formatting it as a short-month-short-weekday.
  return upperFirst(intl.formatDate(date.toDate(), format));
}

function formatTime(date: moment, intl: intlShape) {
  return intl.formatTime(date);
}

export function formatDateTime(date: moment, intl: intlShape) {
  const format = { ...weekdayDate, ...weekdayTime };
  return upperFirst(intl.formatDate(date.toDate(), format));
}

export function formatStartDateOnly(start: moment, intl: intlShape) {
  return formatDate(start, intl);
}

export function formatStartTime(start: moment, intl: intlShape) {
  return formatTime(start, intl);
}

export function formatStartEnd(start: moment, end: ?moment, intl: intlShape) {
  if (end) {
    if (
      start.format('HH:mm:SS') === '00:00:00' &&
      end.format('HH:mm:SS') === '00:00:00'
    ) {
      if (end.diff(start)) {
        return {
          first: `${formatDate(start, intl)} -`,
          second: formatDate(end, intl),
        };
      } else {
        return {
          first: formatDate(start, intl),
        };
      }
    } else {
      const duration = end.diff(start);
      if (duration < moment.duration(1, 'days').asMilliseconds()) {
        const durationText = ` (${humanizeDuration(duration)})`;
        const startText = formatTime(start, intl);
        const endText = formatTime(end, intl);
        return {
          first: formatDate(start, intl),
          second: `${startText} - ${endText} ${durationText}`,
        };
      } else {
        return {
          first: `${formatDateTime(start, intl)} -`,
          second: formatDateTime(end, intl),
        };
      }
    }
  } else {
    return {
      first: formatDate(start, intl),
      second: formatTime(start, intl),
    };
  }
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
