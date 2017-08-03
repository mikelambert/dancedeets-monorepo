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
import { wantsWindowSizes } from './ui';
import type { windowProps } from './ui';

class _DatePicker extends React.Component {
  static DateFormat = 'MMM Do';

  props: {
    query: Object,
    focused: boolean,
    onFocus: () => void,
    onBlur: () => void,
    onComplete: () => void,

    // Self-managed props
    window: windowProps,
    // intl: intlShape,
  };

  state: {
    startDate: ?moment,
    endDate: ?moment,
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

  componentDidUpdate(prevProps, prevState) {
    // Once the component has been updated, and re-rendered the <input>s with new values
    // Let's perform a search based off them
    if (prevState.focusedInput !== null && this.state.focusedInput === null) {
      this.props.onComplete();
    }
  }

  getShortSummary() {
    const { startDate, endDate } = this.state;
    if (startDate && endDate) {
      if (
        startDate.year() === endDate.year() &&
        startDate.month() === endDate.month()
      ) {
        return `${startDate.format(_DatePicker.DateFormat)}—${endDate.format(
          'Do'
        )}`;
      } else {
        return `${startDate.format(_DatePicker.DateFormat)}—${endDate.format(
          _DatePicker.DateFormat
        )}`;
      }
    } else if (startDate) {
      return `After ${startDate.format(_DatePicker.DateFormat)}`;
    } else if (endDate) {
      return `Before ${endDate.format(_DatePicker.DateFormat)}`;
    } else {
      return 'Anytime';
    }
  }

  render() {
    const dateDisplay = (
      <div key="date-display">
        <button
          type="button"
          zIndex="-1"
          className="top-search"
          style={{
            fontSize: 18,
            lineHeight: '24px',
            fontWeight: 200,
            padding: 7,

            backgroundColor: 'transparent',
            border: 0,
            textAlign: 'left',
            width: '100%',
          }}
          onClick={() => {
            this.props.onFocus();
            this.setState({ focusedInput: 'startDate' });
          }}
        >
          {this.getShortSummary()}
        </button>
      </div>
    );
    const narrowScreen = this.props.window && this.props.window.width < 768;
    const orientationProps = narrowScreen
      ? {
          orientation: 'vertical',
          withFullScreenPortal: true,
        }
      : { orientation: 'horizontal' };
    const datePicker = (
      <div key="date-picker">
        <DateRangePicker
          // orientation="vertical"
          startDateId="start"
          endDateId="end"
          isOutsideRange={day => false}
          // Update internal state
          startDate={this.state.startDate}
          endDate={this.state.endDate}
          onDatesChange={({ startDate, endDate }) =>
            this.setState({ startDate, endDate })}
          focusedInput={this.state.focusedInput}
          onFocusChange={focusedInput => {
            this.setState({ focusedInput });
            this.props.onFocus();
          }}
          onClose={() => {
            this.props.onBlur();
          }}
          minimumNights={0}
          displayFormat={_DatePicker.DateFormat}
          hideKeyboardShortcutsPanel
          {...orientationProps}
        />
      </div>
    );
    const invisibleProps = {
      visibility: 'hidden',
      zIndex: -1,
    };
    const fullsizeProps = {
      position: 'absolute',
      top: 0,
      bottom: 0,
      left: 0,
      right: 0,
      backgroundColor: 'white',
    };

    return (
      <div style={{ position: 'relative' }}>
        <div key="picker">
          {datePicker}
        </div>
        <div
          key="display"
          style={
            this.props.focused
              ? { ...invisibleProps, ...fullsizeProps }
              : fullsizeProps
          }
        >
          {dateDisplay}
        </div>
      </div>
    );
  }
}
const DatePicker = wantsWindowSizes(injectIntl(_DatePicker));

// Make Tab button behave like Enter button
Autocomplete.keyDownHandlers.Tab = Autocomplete.keyDownHandlers.Enter;

class TextInput extends React.Component {
  props: {
    id: string,
    placeholder: string,
    value: string,
    onFocus: () => void,
    onBlur: () => void,

    autocomplete?: boolean,
  };

  render() {
    const { id, placeholder, value, ...otherProps } = this.props;

    const inputProps = {
      id: this.props.id,
      type: 'text',
      className: 'top-search',
      name: this.props.id,
      placeholder: this.props.placeholder,
      style: {
        border: 0,
        textOverflow: 'ellipsis',
        backgroundColor: 'transparent',
        padding: 7,
        fontSize: 18,
        lineHeight: '24px',
        width: '100%',
        fontWeight: 200,
      },
      onFocus: () => {
        this.props.onFocus();
      },
      onBlur: this.props.onBlur,
    };
    if (this.props.autocomplete) {
      const menuStyle = {
        marginTop: SearchBoxItem.underlineWidth,
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
          onFocus={this.props.onFocus}
          onBlur={this.props.onBlur}
        />
      );
    }
  }
}

class SearchBoxItem extends React.Component {
  static underlineWidth = 2;

  props: {
    iconName: string,
    style?: Object,
    renderItem: ({
      focused: boolean,
      onFocus: () => void,
      onBlur: () => void,
    }) => React.Element<*>,
  };

  state: {
    focused: boolean,
  };

  constructor(props) {
    super(props);
    this.state = { focused: false };
  }

  render() {
    return (
      <div
        style={{
          display: 'table-cell',
          verticalAlign: 'bottom',
          color: '#484848',

          transition: 'border 500ms ease-out, width 300ms ease-out',

          borderBottomWidth: SearchBoxItem.underlineWidth,
          borderBottomStyle: 'solid',
          borderBottomColor: this.state.focused ? '#4C4D81' : 'transparent',

          width: this.state.focused ? '200%' : '100%',
          ...this.props.style,
        }}
      >
        <div
          style={{
            display: 'flex',
            height: 38,
            overflow: this.state.focused ? 'inherit' : 'hidden',
          }}
        >
          <i
            className={`fa fa-fw fa-${this.props.iconName}`}
            style={{
              verticalAlign: 'top',
              paddingLeft: 7,
              paddingTop: 7,
            }}
          />
          <div style={{ position: 'relative', flexGrow: 1 }}>
            {this.props.renderItem({
              focused: this.state.focused,
              onFocus: () => this.setState({ focused: true }),
              onBlur: () => this.setState({ focused: false }),
            })}
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
    onNewSearch: (form: Object) => void,
    // Self-managed props
    // intl: intlShape,
  };

  state: {
    location: string,
    keywords: string,
    locationItems: Array<string>,
  };

  _autoCompleteService: Object;

  _form: Object;

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

  async performSearch() {
    if (!this._form) {
      console.warn('Error, called performSearch before form has been setup');
      return;
    }
    const formData = new FormData(this._form);

    const form = {};
    [...formData.entries()].forEach(kv => {
      form[kv[0]] = kv[1];
    });
    this.props.onNewSearch(form);
  }

  render() {
    const hiddenFields = this.props.query.deb
      ? <input type="hidden" name="deb" value={this.props.query.deb} />
      : null;

    return (
      <div>
        <form
          id="search-form"
          ref={x => {
            this._form = x;
          }}
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
            <SearchBoxItem
              iconName="globe"
              renderItem={({ focused, onFocus, onBlur }) =>
                <TextInput
                  autocomplete
                  id="location"
                  placeholder={
                    focused ? 'City, Region, or Country' : 'Anywhere'
                  }
                  value={this.state.location}
                  items={this.state.locationItems}
                  onChange={(event, value) => {
                    this.setState({ location: value });
                    if (!value) {
                      return;
                    }
                    // TODO: Cancel/ignore old prediction requests, in case they arrive out-of-order
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
                  onSelect={async (value, item) => {
                    await this.setState({ location: value });
                    this.performSearch();
                  }}
                  onFocus={onFocus}
                  onBlur={() => {
                    onBlur();
                    this.performSearch();
                  }}
                />}
            />
            <SearchBoxItem
              iconName="search"
              style={{
                borderLeft: '1px solid #e4e4e4',
                borderRight: '1px solid #e4e4e4',
              }}
              renderItem={({ focused, onFocus, onBlur }) =>
                <TextInput
                  autocomplete
                  id="keywords"
                  placeholder={
                    focused ? 'Dance style, event name, etc' : 'Any style'
                  }
                  value={this.state.keywords}
                  onChange={(event, value) =>
                    this.setState({ keywords: value })}
                  onSelect={async (value, item) => {
                    await this.setState({ keywords: value });
                    this.performSearch();
                  }}
                  items={this.autocompleteKeywords()}
                  getItemValue={item => item.label}
                  shouldItemRender={(item, value) => {
                    if (value.length) {
                      return (
                        item.label
                          .toLowerCase()
                          .indexOf(value.toLowerCase()) !== -1
                      );
                    } else {
                      return item.initial;
                    }
                  }}
                  onFocus={onFocus}
                  onBlur={() => {
                    onBlur();
                    this.performSearch();
                  }}
                />}
            />
            <SearchBoxItem
              iconName="clock-o"
              style={{
                borderLeft: '1px solid #e4e4e4',
                borderRight: '1px solid #e4e4e4',
              }}
              renderItem={({ focused, onFocus, onBlur }) =>
                <DatePicker
                  query={this.props.query}
                  focused={focused}
                  onFocus={onFocus}
                  onBlur={onBlur}
                  onComplete={() => this.performSearch()}
                />}
            />

          </div>
          {hiddenFields}
        </form>
      </div>
    );
  }
}
export const SearchBox = injectIntl(_SearchBox);
