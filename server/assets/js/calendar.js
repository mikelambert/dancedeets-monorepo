/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import querystring from 'querystring';
import { intlWeb } from 'dancedeets-common/js/intl';
import FullCalendar from './FullCalendar';

class CalendarPage extends React.Component<{
  query: Object,
}> {
  render() {
    const queryString = querystring.stringify(this.props.query);
    const eventUrl = `/calendar/feed?${queryString}`;
    const options = {
      height: 'auto',
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,basicWeek,basicDay',
      },
      views: {
        month: {
          eventLimit: 4,
          eventLimitClick: 'day',
        },
        week: {
          eventLimit: 8,
          eventLimitClick: 'day',
        },
      },
      ignoreTimezone: true,
      allDayDefault: false,
      defaultView: 'basicWeek',
      events: eventUrl,
    };
    return <FullCalendar key={queryString} options={options} />;
  }
}

export default intlWeb(CalendarPage);
