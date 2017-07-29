/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import moment from 'moment';
import { injectIntl, intlShape } from 'react-intl';
import Autocomplete from 'react-autocomplete';
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

class TextInput extends React.Component {
  static underlineWidth = 2;

  props: {
    iconName: string,
    id: string,
    placeholder: string,
    focused_placeholder: string,
    defaultValue: string,
    style?: object,

    autocomplete?: boolean,
  };

  state: {
    focused: boolean,
    value: string,
  };

  constructor(props) {
    super(props);
    this.state = { focused: false, value: this.props.defaultValue };
  }

  autocompleteItems() {
    return [
      { label: 'breaking', initial: true },
      { label: 'bboying' },
      { label: 'bgirling' },
      { label: 'b-boying' },
      { label: 'b-girling' },
      { label: 'hiphop' },
      { label: 'hip-hop', initial: true },
      { label: 'house', initial: true },
      { label: 'popping', initial: true },
      { label: 'locking', initial: true },
      { label: 'waacking', initial: true },
      { label: 'whacking' },
      { label: 'dancehall', initial: true },
      { label: 'vogue', initial: true },
      { label: 'krump', initial: true },
      { label: 'turfing' },
      { label: 'litefeet' },
      { label: 'flexing' },
      { label: 'bebop' },
      { label: 'all-styles', initial: true },
      { label: 'kids' },
      // event types
      { label: 'battle' },
      { label: 'workshop' },
      { label: 'performance' },
      { label: 'competition' },
      { label: 'class' },
    ];
  }

  renderInput() {
    const inputProps = {
      id: this.props.id,
      type: 'text',
      className: 'top-search',
      name: this.props.id,
      placeholder: this.state.focused
        ? this.props.focused_placeholder
        : this.props.placeholder,
      style: {
        border: 0,
        textOverflow: 'ellipsis',
        backgroundColor: 'transparent',
        padding: 7,
        fontSize: 15,
        lineHeight: '18px',
        width: '100%',
      },
      onFocus: () => this.setState({ focused: true }),
      onBlur: () => this.setState({ focused: false }),
    };
    if (this.props.autocomplete) {
      const menuStyle = {
        marginTop: TextInput.underlineWidth,
        borderRadius: '3px',
        boxShadow: '0 2px 12px rgba(0, 0, 0, 0.1)',
        background: 'rgba(255, 255, 255, 0.9)',
        padding: '2px 0',
        fontSize: '90%',
        position: 'absolute',
        width: '100%',
      };
      return (
        <Autocomplete
          wrapperStyle={{}}
          inputProps={inputProps}
          value={this.state.value}
          onChange={e => this.setState({ value: e.target.value })}
          onSelect={(value, item) => this.setState({ value })}
          getItemValue={item => item.label}
          items={this.autocompleteItems()}
          renderItem={(item, isHighlighted) =>
            <div
              key={item.label}
              style={{ background: isHighlighted ? '#C0C0E8' : 'white' }}
            >
              {item.label}
            </div>}
          renderMenu={(items, value, style) =>
            <div style={menuStyle}>{items}</div>}
          shouldItemRender={(item, value) => {
            if (value.length) {
              return (
                item.label.toLowerCase().indexOf(value.toLowerCase()) !== -1
              );
            } else {
              return item.initial;
            }
          }}
        />
      );
    } else {
      return (
        <input
          {...inputProps}
          value={this.state.value}
          onChange={e => this.setState({ value: e.target.value })}
          onFocus={() => this.setState({ focused: true })}
          onBlur={() => this.setState({ focused: false })}
        />
      );
    }
  }

  render() {
    return (
      <div
        style={{
          display: 'table-cell',
          color: '#484848',

          transition: 'border 500ms ease-out, width 300ms ease-out',

          borderBottomWidth: TextInput.underlineWidth,
          borderBottomStyle: 'solid',
          borderBottomColor: this.state.focused ? '#4C4D81' : 'transparent',

          width: this.state.focused ? '200%' : '100%',
          ...this.props.style,
        }}
      >
        <div style={{ display: 'flex' }}>
          <i
            className={`fa fa-fw fa-${this.props.iconName}`}
            style={{
              verticalAlign: 'top',
              paddingLeft: 7,
              paddingTop: 7,
            }}
          />
          <div style={{ position: 'relative', flexGrow: 1 }}>
            {this.renderInput()}
          </div>
        </div>
      </div>
    );
  }
}

class _SearchBox extends React.Component {
  props: {
    query: Object,

    // Self-managed props
    // intl: intlShape,
  };

  render2() {
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
                        id="location"
                        type="text"
                        name="location"
                        placeholder="Anywhere"
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
                        id="keywords"
                        type="text"
                        name="keywords"
                        placeholder="Any Style"
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

  render() {
    const form = this.props.query;
    return (
      <div>
        <form
          id="search-form"
          classNameName="form-inline"
          role="search"
          action="/"
          acceptCharset="UTF-8"
        >
          <div
            style={{
              fontSize: 19,
              lineHeight: '24px',
              letterSpacing: null,
              paddingTop: 0,
              paddingBottom: 0,
              color: '#484848',
              borderRadius: 4,
              border: '1px solid #DBDBDB',
              boxShadow: '0 1px 3px 0px rgba(0, 0, 0, 0.08)',
              padding: 0,
              display: 'table',
              tableLayout: 'fixed',
              width: '100%',
              position: 'relative',
              backgroundColor: 'white',
            }}
          >
            <TextInput
              iconName="globe"
              id="location"
              placeholder="Anywhere"
              focused_placeholder="City, Region, or Country"
              defaultValue={form.location}
            />
            <TextInput
              autocomplete
              iconName="search"
              id="keywords"
              placeholder="Any style"
              focused_placeholder="Dance style, event name, etc"
              defaultValue={form.keywords}
              style={{
                borderLeft: '1px solid #e4e4e4',
                borderRight: '1px solid #e4e4e4',
              }}
            />
            <TextInput
              iconName="clock-o"
              id="dates"
              placeholder="Anytime"
              defaultValue={''}
            />
          </div>
        </form>
      </div>
    );
  }
}
export const SearchBox = injectIntl(_SearchBox);
