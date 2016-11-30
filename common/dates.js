/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React, {createElement} from 'react';
import _ from 'lodash/string';
import {
  injectIntl,
} from 'react-intl';
import moment from 'moment';

export const weekdayDateTime = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric'};

export function formatStartEnd(startString, endString, intl) {
  const textFields = [];
  const now = moment(intl.now());
  const start = moment(startString, moment.ISO_8601);
  const formattedStart = _.upperFirst(intl.formatDate(start.toDate(), weekdayDateTime));
  if (endString) {
    const end = moment(endString, moment.ISO_8601);
    const duration = end.diff(start);
    if (duration > moment.duration(1, 'days')) {
      const formattedEnd = _.upperFirst(intl.formatDate(end, weekdayDateTime));
      textFields.push(formattedStart + ' - \n' + formattedEnd);
    } else {
      const formattedEndTime = intl.formatTime(end);
      textFields.push(formattedStart + ' - ' + formattedEndTime);
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
