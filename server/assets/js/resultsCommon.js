/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import moment from 'moment';
import { injectIntl, intlShape } from 'react-intl';
import { DateRangePicker } from 'react-dates';
import 'react-dates/lib/css/_datepicker.css';

class DatePicker extends React.Component {
  props: {
    query: Object,
  };

  state: {
    startDate: Moment,
    endDate: Moment,
    focusedInput: any,
  };

  constructor(props) {
    super(props);
    this.state = {
      startDate: props.query.start ? moment(props.query.start) : null,
      endDate: props.query.end ? moment(props.query.end) : null,
      focusedInput: null,
    };
    console.log(this.props.query, this.state);
  }

  render() {
    return (
      <DateRangePicker
        startDateId="start"
        endDateId="end"
        isOutsideRange={day => false}
        // Update internal state
        startDate={this.state.startDate}
        endDate={this.state.endDate}
        onDatesChange={({ startDate, endDate }) =>
          this.setState({ startDate, endDate })}
        focusedInput={this.state.focusedInput}
        onFocusChange={focusedInput => this.setState({ focusedInput })}
      />
    );
  }
}

class _SearchBox extends React.Component {
  props: {
    query: Object,

    // Self-managed props
    // intl: intlShape,
  };

  render() {
    const form = this.props.query;
    const hiddenFields = form.deb
      ? <input type="hidden" name="deb" value={form.deb} />
      : null;
    return (
      <div style={{ marginBottom: 25 }}>
        <table>
          <tbody>
            <tr>
              <td>
                <img
                  role="presentation"
                  className="hidden-xs"
                  id="penguin"
                  src="/images/full_penguin_240.png"
                  height="120"
                  width="120"
                />
              </td>
              <td>
                <form
                  id="search-form"
                  classNameName="form-inline"
                  role="search"
                  action="/"
                  acceptCharset="UTF-8"
                >
                  <div className="form-group">
                    <div style={{ fontWeight: 'bold' }}>
                      Where will you dance next?
                    </div>
                    <div className="input-group">
                      <span className="input-group-addon">
                        <i className="fa fa-globe fa-fw" />
                      </span>
                      <input
                        id="location_input"
                        type="text"
                        name="location"
                        placeholder="everywhere"
                        defaultValue={form.location}
                        className="form-control"
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <div style={{ fontWeight: 'bold' }}>
                      Looking for anything in particular?
                    </div>
                    <div style={{ fontStyle: 'italic', fontSize: '70%' }}>
                      You can enter a dance style, dancer, event name, or leave
                      it
                      blank!
                    </div>
                    <div className="input-group">
                      <span className="input-group-addon">
                        <i className="fa fa-search fa-fw" />
                      </span>
                      <input
                        id="keywords_input"
                        type="text"
                        name="keywords"
                        placeholder="all events"
                        defaultValue={form.keywords}
                        className="form-control"
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <div style={{ fontWeight: 'bold' }}>
                      When will you be there?
                    </div>
                    <DatePicker query={this.props.query} />
                  </div>
                  {hiddenFields}
                  <button
                    type="submit"
                    className="btn btn-default btn-block"
                    style={{ marginTop: '1em' }}
                  >
                    <i className="fa fa-search fa-fw" />
                    Search our Events
                  </button>

                </form>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }
}
export const SearchBox = injectIntl(_SearchBox);
