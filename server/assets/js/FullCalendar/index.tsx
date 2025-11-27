/**
 * Copyright 2016 DanceDeets.
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

interface Props {
  options: Record<string, unknown>;
  onDateChanged?: (start: Date, end: Date) => void;
}

class FullCalendar extends React.Component<Props> {
  _calendar: JQuery<HTMLElement> | null = null;
  _fullcalendarContainer: HTMLDivElement | null = null;

  componentDidMount(): void {
    const { options, onDateChanged } = this.props;

    const extendCalendarOptions = (calendarOptions: Record<string, unknown>) => {
      const defaultOptions = {
        viewRender(view: { intervalStart: { toDate: () => Date }; intervalEnd: { toDate: () => Date } }) {
          const { intervalStart, intervalEnd } = view;

          const toDate = (momentDate: { toDate: () => Date }) => momentDate.toDate();

          if (onDateChanged && typeof onDateChanged === 'function') {
            onDateChanged(toDate(intervalStart), toDate(intervalEnd));
          }
        },
      };

      return Object.assign({}, defaultOptions, calendarOptions);
    };

    this._calendar = $(this._fullcalendarContainer as HTMLDivElement);

    const calendarOptions = extendCalendarOptions(options);

    (this._calendar as unknown as { fullCalendar: (options: Record<string, unknown>) => void }).fullCalendar(calendarOptions);
  }

  componentWillReceiveProps(newProps: Props): void {
    const { options: newOptions } = newProps;
    const { options } = this.props;

    Object.keys(newOptions).forEach(optionName => {
      // update options dynamically
      if (
        isOption(optionName) &&
        newOptions[optionName] !== options[optionName]
      ) {
        (this._calendar as unknown as { fullCalendar: (...args: unknown[]) => void }).fullCalendar(
          'option',
          optionName,
          newOptions[optionName]
        );
      }
    });

    const calendar = this._calendar as unknown as { fullCalendar: (...args: unknown[]) => void };
    calendar.fullCalendar('refetchEvents');
    calendar.fullCalendar('changeView', newOptions.defaultView);
    calendar.fullCalendar('gotoDate', newOptions.defaultDate);
  }

  render(): React.ReactElement {
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
