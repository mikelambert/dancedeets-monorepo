/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import $ from 'jquery';
import 'fullcalendar/dist/fullcalendar.css';
import ExecutionEnvironment from 'exenv';
import { isOption } from './utils';

if (ExecutionEnvironment.canUseDOM) {
  // This has errors when imported on an uninitialized jquery
  // In particular, it wants to do $.fn.fullCalendar =
  // and it seems $.fn is undefined at the time it runs.
  // So let's conditionally require/import it at runtime, only on the client.
  require('fullcalendar'); // eslint-disable-line global-require
}

type Props = {
  options: Object,
  onDateChanged: (start: Date, end: Date) => void,
};

class FullCalendar extends React.Component<Props> {
  _fullcalendarContainer: ?HTMLDivElement;
  calendar: any;

  componentDidMount() {
    const { options, onDateChanged } = this.props;

    const extendCalendarOptions = calendarOptions => {
      const defaultOptions = {
        viewRender(view) {
          const { intervalStart, intervalEnd } = view;

          const toDate = momentDate => momentDate.toDate();

          if (onDateChanged && typeof onDateChanged === 'function') {
            onDateChanged(toDate(intervalStart), toDate(intervalEnd));
          }
        },
      };

      return Object.assign({}, defaultOptions, calendarOptions);
    };

    this.calendar = $(this._fullcalendarContainer);

    const calendarOptions = extendCalendarOptions(options);

    this.calendar.fullCalendar(calendarOptions);
  }

  componentWillReceiveProps(newProps: Props) {
    const { options: newOptions } = newProps;
    const { options } = this.props;

    Object.keys(newOptions).forEach(optionName => {
      // update options dynamically
      if (
        isOption(optionName) &&
        newOptions[optionName] !== options[optionName]
      ) {
        this.calendar.fullCalendar(
          'option',
          optionName,
          newOptions[optionName]
        );
      }
    });

    this.calendar.fullCalendar('refetchEvents');
    this.calendar.fullCalendar('changeView', newOptions.defaultView);
    this.calendar.fullCalendar('gotoDate', newOptions.defaultDate);
  }

  render() {
    return (
      <div
        ref={x => {
          this._fullcalendarContainer = x;
        }}
      />
    );
  }
}

export default FullCalendar;
