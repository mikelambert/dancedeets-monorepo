/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

// TODO: start sharing this code with dancedeets-react's _EventDateTime

import React, {createElement} from 'react';
import _ from 'lodash/string';
import {
  injectIntl,
} from 'react-intl';
import moment from 'moment';

export const weekdayDateTime = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric'};

class _StartEnd extends React.Component {
  render() {
    const textFields = [];
    const now = moment(this.props.intl.now());
    const start = moment(this.props.start, moment.ISO_8601);
    const formattedStart = _.upperFirst(this.props.intl.formatDate(start.toDate(), weekdayDateTime));
    if (this.props.end) {
      const end = moment(this.props.end, moment.ISO_8601);
      const duration = end.diff(start);
      if (duration > moment.duration(1, 'days')) {
        const formattedEnd = _.upperFirst(this.props.intl.formatDate(end, weekdayDateTime));
        textFields.push(formattedStart + ' - \n' + formattedEnd);
      } else {
        const formattedEndTime = this.props.intl.formatTime(end);
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
    const tagName = this.props.tagName;
    return createElement(tagName, null, textFields.join(''));
  }
}
export const StartEnd = injectIntl(_StartEnd);
