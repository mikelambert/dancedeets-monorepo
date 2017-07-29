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
    focusedPlaceholder: string,
    value: string,
    style?: object,

    autocomplete?: boolean,
  };

  state: {
    focused: boolean,
  };

  constructor(props) {
    super(props);
    this.state = { focused: false };
  }

  renderInput() {
    const {
      iconName,
      id,
      placeholder,
      focusedPlaceholder,
      value,
      style,
      ...otherProps
    } = this.props;

    const inputProps = {
      id: this.props.id,
      type: 'text',
      className: 'top-search',
      name: this.props.id,
      placeholder: this.state.focused
        ? this.props.focusedPlaceholder
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
        zIndex: 10,
      };
      return (
        <Autocomplete
          wrapperStyle={{}}
          inputProps={inputProps}
          value={this.props.value}
          renderItem={(item, isHighlighted) =>
            <div
              key={item.label}
              style={{
                background: isHighlighted ? '#C0C0E8' : 'white',
                padding: 12,
              }}
            >
              {item.main
                ? <div>
                    <i
                      className="fa fa-map-marker"
                      style={{ paddingRight: 12 }}
                    />
                    <strong>{item.main}</strong>{' '}
                    <small style={{ color: 'grey' }}>
                      {item.secondary}
                    </small>
                  </div>
                : item.label}
            </div>}
          renderMenu={items => <div style={menuStyle}>{items}</div>}
          {...otherProps}
        />
      );
    } else {
      return (
        <input
          {...inputProps}
          value={this.props.value}
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

function performLocationLookup(value, itemsCallback) {}

class _SearchBox extends React.Component {
  props: {
    query: Object,

    // Self-managed props
    // intl: intlShape,
  };

  state: {
    location: string,
    keywords: string,
    locationItems: Array<string>,
  };

  _autoCompleteService: object;

  constructor(props) {
    super(props);
    this.state = {
      keywords: this.props.query.keywords,
      location: this.props.query.location,
      locationItems: [],
    };
  }

  getAutocompleteService() {
    if (this._autoCompleteService) {
      return this._autoCompleteService;
    }
    this._autoCompleteService = new window.google.maps.places
      .AutocompleteService();
    return this._autoCompleteService;
  }

  autocompleteKeywords() {
    return [
      { label: 'breaking', initial: true },
      { label: 'bboying' },
      { label: 'bgirling' },
      { label: 'b-boying' },
      { label: 'b-girling' },
      { label: 'hip-hop', initial: true },
      { label: 'hiphop' },
      { label: 'house', initial: true },
      { label: 'popping', initial: true },
      { label: 'locking', initial: true },
      { label: 'waacking', initial: true },
      { label: 'whacking' },
      { label: 'dancehall', initial: true },
      { label: 'vogue', initial: true },
      { label: 'krump', initial: true },
      { label: 'all-styles', initial: true },
      { label: 'turfing' },
      { label: 'litefeet' },
      { label: 'flexing' },
      { label: 'bebop' },
      { label: 'kids' },
      // event types
      { label: 'battle' },
      { label: 'workshop' },
      { label: 'performance' },
      { label: 'competition' },
      { label: 'class' },
    ];
  }

  render() {
    const form = this.props.query;

    const hiddenFields = form.deb
      ? <input type="hidden" name="deb" value={form.deb} />
      : null;

    return (
      <div>
        <form
          id="search-form"
          role="search"
          className="form-inline"
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
              autocomplete
              iconName="globe"
              id="location"
              placeholder="Anywhere"
              focusedPlaceholder="City, Region, or Country"
              value={this.state.location}
              items={this.state.locationItems}
              onChange={(event, value) => {
                this.setState({ location: value });
                if (!value) {
                  return;
                }
                clearTimeout(this.requestTimer);
                this.getAutocompleteService().getPlacePredictions(
                  {
                    input: value,
                    types: ['(regions)'],
                  },
                  (predictions, status) => {
                    let items = [];
                    if (
                      status ===
                      window.google.maps.places.PlacesServiceStatus.OK
                    ) {
                      items = predictions.map(x => ({
                        label: x.description,
                        main: x.structured_formatting.main_text,
                        secondary: x.structured_formatting.secondary_text,
                      }));
                    }
                    this.setState({ locationItems: items });
                  }
                );
              }}
              getItemValue={item => item.label}
              onSelect={(value, item) => {
                this.setState({ location: value });
              }}
            />
            <TextInput
              autocomplete
              iconName="search"
              id="keywords"
              placeholder="Any style"
              focusedPlaceholder="Dance style, event name, etc"
              style={{
                borderLeft: '1px solid #e4e4e4',
                borderRight: '1px solid #e4e4e4',
              }}
              value={this.state.keywords}
              onChange={(event, value) => this.setState({ keywords: value })}
              onSelect={(value, item) => this.setState({ keywords: value })}
              items={this.autocompleteKeywords()}
              getItemValue={item => item.label}
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
            <TextInput
              iconName="clock-o"
              id="dates"
              placeholder="Anytime"
              value={''}
            />
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
      </div>
    );
  }
}
export const SearchBox = injectIntl(_SearchBox);
