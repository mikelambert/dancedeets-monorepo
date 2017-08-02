/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { injectIntl, intlShape } from 'react-intl';
import querystring from 'querystring';
import ExecutionEnvironment from 'exenv';
import createBrowserHistory from 'history/createBrowserHistory';
import type { NewSearchResponse } from 'dancedeets-common/js/events/search';
import { intlWeb } from 'dancedeets-common/js/intl';
import FullCalendar from './FullCalendar';
import { Card, ImagePrefix } from './ui';
import { SearchBox } from './resultsCommon';

class CalendarPage extends React.Component {
  props: {
    query: Object,
  };

  state: {
    queryString: string,
  };

  constructor(props) {
    super(props);
    const queryString = querystring.stringify(this.props.query);
    this.state = { queryString };
    (this: any).onNewSearch = this.onNewSearch.bind(this);
  }

  async onNewSearch(form) {
    const newForm = Object.assign({}, form, {
      calendar: '1',
    });
    const newQueryString = querystring.stringify(newForm);
    const history = createBrowserHistory();
    history.replace(`/?${newQueryString}`);

    const calendarForm = form;
    delete calendarForm.start;
    delete calendarForm.end;
    const queryString = querystring.stringify(form);
    this.setState({ queryString });
  }

  render() {
    const queryString = this.state.queryString;
    const resultsUrl = `/events/relevant?${queryString}`;
    const eventUrl = `/calendar/feed?${queryString}`;
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
      <div className="col-xs-12">
        <SearchBox query={this.props.query} onNewSearch={this.onNewSearch} />

        <div style={{ textAlign: 'right' }}>
          <a href={resultsUrl}>
            <ImagePrefix iconName="list-ul">View as List</ImagePrefix>
          </a>
        </div>
        {ExecutionEnvironment.canUseDOM
          ? <Card>
              <FullCalendar key={queryString} options={options} />
            </Card>
          : null}
      </div>
    );
  }
}

export default intlWeb(CalendarPage);
