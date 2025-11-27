/**
 * Copyright 2016 DanceDeets.
 */

import upperFirst from 'lodash/upperFirst';
import moment, { Moment } from 'moment';

// Simple type for react-intl's intl object
interface IntlShape {
  now(): number;
  formatDate(date: Date, options?: Intl.DateTimeFormatOptions): string;
  formatTime(date: Date | Moment): string;
}

// TODO: combine this with mobile's formats.js
export const weekdayDate: Intl.DateTimeFormatOptions = {
  weekday: 'long',
  month: 'long',
  day: 'numeric',
  year: 'numeric',
};
export const weekdayTime: Intl.DateTimeFormatOptions = {
  hour: 'numeric',
  minute: 'numeric',
};

// eslint-disable-next-line no-unused-vars
function dateIsNearby(date: Moment, intl: IntlShape): boolean {
  const now = moment(intl.now());
  const diff = date.diff(now);
  return (
    diff > moment.duration(-3, 'months').asMilliseconds() &&
    diff < moment.duration(6, 'months').asMilliseconds()
  );
}

function formatDate(date: Moment, intl: IntlShape): string {
  // Use a year for faraway dates
  const format = { ...weekdayDate };
  // I would like to only show the year on far-away dates
  // but unfortunately, the serverside Intl lacks a
  // year-less long-month-long-weekday formatter,
  // and ends up formatting it as a short-month-short-weekday.
  return upperFirst(intl.formatDate(date.toDate(), format));
}

function formatTime(date: Moment, intl: IntlShape): string {
  return intl.formatTime(date);
}

export function formatDateTime(date: Moment, intl: IntlShape): string {
  const format = { ...weekdayDate, ...weekdayTime };
  return upperFirst(intl.formatDate(date.toDate(), format));
}

export function formatStartDateOnly(start: Moment, intl: IntlShape): string {
  return formatDate(start, intl);
}

export function formatStartTime(start: Moment, intl: IntlShape): string {
  return formatTime(start, intl);
}

interface FormattedStartEnd {
  first: string;
  second?: string;
}

export function formatStartEnd(
  start: Moment,
  end: Moment | null | undefined,
  intl: IntlShape
): FormattedStartEnd {
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

function humanizeExactly(unitCount: number, unitName: string): string {
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
    possiblyPluralizedUnitName as moment.RelativeTimeKey,
    isFuture
  );
}

function humanizeDuration(eventDuration: number): string {
  // We don't use .humanize(), because 90 minutes => "2 hours"
  // We also don't use piecemeal humanize() strings concatenation,
  // because moment.duration(50, 'minutes').humanize() => "an hour"
  // So instead we call the locale formatting functions directly, piecemeal.
  const eventMDuration = moment.duration(eventDuration);
  const eventDurationBits: string[] = [];
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
