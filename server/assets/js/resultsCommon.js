/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import moment from 'moment';
import classNames from 'classnames';
import { injectIntl, intlShape } from 'react-intl';
import Autocomplete from 'react-autocomplete';
import { DateRangePicker } from 'react-dates';
import { wantsWindowSizes } from './ui';
import type { windowProps } from './ui';

// Keep in sync with results.scss's NarrowWindowSize
const NarrowWindowSize = 768;

export const CalendarRatio = 1.8;

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
      if (this.props.onComplete) {
        this.props.onComplete();
      }
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
    const narrowScreen =
      !this.props.window || this.props.window.width < NarrowWindowSize;
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

function findNextTabStop(el) {
  const universe = global.window.document.querySelectorAll(
    'input, button, select, textarea, a[href]'
  );
  const list = Array.prototype.filter.call(
    universe,
    item => item.tabIndex >= '0'
  );
  const index = list.indexOf(el);
  return list[index + 1] || list[0];
}

function HandleSelection(event) {
  const target = event.target;
  const key = event.key;
  if (!this.isOpen() || this.state.highlightedIndex == null) {
    // menu is closed so there is no selection to accept -> do nothing
    this.setState({ isOpen: false }, () => {
      this.props.onSelect(target.value);
      if (key === 'Enter') {
        // Don't run this code for Tab, or it will double-Tab
        findNextTabStop(target).focus();
        // Only submit form on "Enter" on a form field without any menu item selected
        this.props.onSubmit();
      }
    });
  } else {
    // text entered + menu item has been highlighted + enter is hit -> update value to that of selected menu item, close the menu
    event.preventDefault();
    const item = this.getFilteredItems(this.props)[this.state.highlightedIndex];
    const value = this.props.getItemValue(item);
    this.setState(
      {
        isOpen: false,
        highlightedIndex: null,
      },
      () => {
        // this.refs.input.focus() // TODO: file issue
        this.refs.input.setSelectionRange(value.length, value.length);
        this.props.onSelect(value, item);
      }
    );
  }
}

function HandleArrowDown(event) {
  event.preventDefault();
  const itemsLength = this.getFilteredItems(this.props).length;
  if (!itemsLength) return;
  const { highlightedIndex } = this.state;
  let index;
  if (highlightedIndex === itemsLength - 1) {
    index = null;
  } else if (highlightedIndex === null) {
    index = 0;
  } else {
    index = highlightedIndex + 1;
  }
  this.setState({
    highlightedIndex: index,
    isOpen: true,
  });
}

function HandleArrowUp(event) {
  event.preventDefault();
  const itemsLength = this.getFilteredItems(this.props).length;
  if (!itemsLength) return;
  const { highlightedIndex } = this.state;
  let index;
  if (highlightedIndex === 0) {
    index = null;
  } else if (highlightedIndex === null) {
    index = itemsLength - 1;
  } else {
    index = highlightedIndex - 1;
  }
  this.setState({
    highlightedIndex: index,
    isOpen: true,
  });
}

// Make Tab button behave like Enter button
Autocomplete.keyDownHandlers.Tab = Autocomplete.keyDownHandlers.Enter = HandleSelection;
Autocomplete.keyDownHandlers.ArrowDown = HandleArrowDown;
Autocomplete.keyDownHandlers.ArrowUp = HandleArrowUp;

class TextInput extends React.Component {
  props: {
    id: string,
    placeholder: string,
    value: string,
    onFocus: (e: SyntheticEvent) => void,
    onBlur: (e: SyntheticEvent) => void,
    onSubmit: (e: SyntheticEvent) => void,

    shouldItemRender?: (item: Object, value: string) => boolean,
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
      onFocus: e => {
        e.target.select();
        this.props.onFocus(e);
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
          // Only show the menu if we have items to show
          renderMenu={items =>
            items.length ? <div style={menuStyle}>{items}</div> : <div />}
          onSubmit={this.props.onSubmit}
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
          verticalAlign: 'bottom',
          color: '#484848',

          transition: 'border 500ms ease-out, flex-grow 300ms ease-out',

          border: '1px solid #e4e4e4',
          borderBottomWidth: SearchBoxItem.underlineWidth,
          borderBottomStyle: 'solid',
          borderBottomColor: this.state.focused ? '#4C4D81' : 'transparent',
        }}
        className={
          this.state.focused
            ? 'media-query-search-focused'
            : 'media-query-search-not-focused'
        }
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
              paddingTop: 10,
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
    (this: any).performSearch = this.performSearch.bind(this);
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
      { label: 'Breaking', initial: true },
      { label: 'Bboying' },
      { label: 'Bgirling' },
      { label: 'Hiphop', initial: true },
      { label: 'House', initial: true },
      { label: 'Popping', initial: true },
      { label: 'Locking', initial: true },
      { label: 'Waacking', initial: true },
      { label: 'Whacking' },
      { label: 'Choreography', initial: true },
      { label: 'Dancehall', initial: true },
      { label: 'Vogue', initial: true },
      { label: 'Krump', initial: true },
      { label: 'All-Styles', initial: true },
      { label: 'Turfing' },
      { label: 'Litefeet' },
      { label: 'Flexing' },
      { label: 'Bebop' },
      { label: 'Kids' },
      // event types
      { label: 'Battle' },
      { label: 'Workshop' },
      { label: 'Performance' },
      { label: 'Competition' },
      { label: 'Class' },
    ];
  }

  async performSearch() {
    if (!this._form) {
      console.warn('Error, called performSearch before form has been setup');
      return;
    }
    const formData = new FormData(this._form);

    const form = {};
    [...this._form.elements].forEach(field => {
      if (field.name !== '') {
        form[field.name] = field.value;
      }
    });
    this.props.onNewSearch(form);
  }

  render() {
    const hiddenFields = this.props.query.deb
      ? <input type="hidden" name="deb" value={this.props.query.deb} />
      : null;

    return (
      <div>
        <div
          style={{
            fontWeight: 'bold',
            textTransform: 'uppercase',
            margin: 5,
          }}
        >
          Find the Dance Scene:
        </div>
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
              color: '#484848',
              borderRadius: 4,
              border: '1px solid #DBDBDB',
              borderRight: 0,
              boxShadow: '0 1px 3px 0px rgba(0, 0, 0, 0.08)',
              padding: 0,
              width: '100%',
              backgroundColor: 'white',
            }}
            className="media-query-search-box"
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
                  onSubmit={this.performSearch}
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
                  }}
                  onFocus={onFocus}
                  onBlur={onBlur}
                />}
            />
            <SearchBoxItem
              iconName="search"
              renderItem={({ focused, onFocus, onBlur }) =>
                <TextInput
                  autocomplete
                  id="keywords"
                  placeholder={
                    focused
                      ? 'Dance style, event name, dancer name, etc'
                      : 'Any style, event type, etc'
                  }
                  value={this.state.keywords}
                  onSubmit={this.performSearch}
                  onChange={(event, value) =>
                    this.setState({ keywords: value })}
                  onSelect={async (value, item) => {
                    await this.setState({ keywords: value });
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
                  onBlur={onBlur}
                />}
            />
            <SearchBoxItem
              iconName="clock-o"
              renderItem={({ focused, onFocus, onBlur }) =>
                <DatePicker
                  query={this.props.query}
                  focused={focused}
                  onFocus={onFocus}
                  onBlur={onBlur}
                />}
            />
            <div>
              <button
                className="btn btn-default"
                type="button"
                style={{ width: '100%', height: '100%' }}
                onClick={() => this.performSearch()}
              >
                Find My Dance
              </button>
            </div>
          </div>
          {hiddenFields}
        </form>
      </div>
    );
  }
}
export const SearchBox = injectIntl(_SearchBox);
