/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { injectIntl, intlShape } from 'react-intl';
import querystring from 'querystring';
import ExecutionEnvironment from 'exenv';
import type { NewSearchResponse } from 'dancedeets-common/js/events/search';
import { intlWeb } from 'dancedeets-common/js/intl';
import FullCalendar from './FullCalendar';
import { Card, ImagePrefix } from './ui';
import { SearchBox } from './resultsCommon';

class CalendarPage extends React.Component {
  props: {
    query: Object,
  };

  render() {
    const query = querystring.stringify(this.props.query);
    const resultsUrl = `/events/relevant?${query}`;
    const eventUrl = `/calendar/feed?${query}`;
    const options = {
      aspectRatio: 1.8,
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
    return (
      <div className="col-md-9">
        <SearchBox query={this.props.query} />

        <div style={{ textAlign: 'right' }}>
          <a href={resultsUrl}>
            <ImagePrefix iconName="list-ul">View as List</ImagePrefix>
          </a>
        </div>
        {ExecutionEnvironment.canUseDOM
          ? <Card><FullCalendar options={options} /></Card>
          : null}
      </div>
    );
  }
}

export default intlWeb(CalendarPage);
