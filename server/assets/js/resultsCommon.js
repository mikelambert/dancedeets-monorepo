/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import moment from 'moment';
import classNames from 'classnames';
import { injectIntl } from 'react-intl';
import Autocomplete from 'react-autocomplete';
import { DateRangePicker } from 'react-dates';
import { wantsWindowSizes } from './ui';
import type { windowProps } from './ui';

// Keep in sync with results.scss's NarrowWindowSize
const NarrowWindowSize = 768;

export const CalendarRatio = 1.8;

type Query = Object;

class _DatePicker extends React.Component {
  static DateFormat = 'MMM Do';

  props: {
    query: Query,
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
    (this: any).onFocusClick = this.onFocusClick.bind(this);
    (this: any).onDatesChange = this.onDatesChange.bind(this);
    (this: any).onFocusChange = this.onFocusChange.bind(this);
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

  onFocusClick() {
    this.props.onFocus();
    this.setState({ focusedInput: 'startDate' });
  }

  onDatesChange({ startDate, endDate }) {
    this.setState({ startDate, endDate });
  }
  onFocusChange(focusedInput) {
    this.setState({ focusedInput });
    this.props.onFocus();
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
      <button
        type="button"
        className="top-search search-box-date-display"
        onClick={this.onFocusClick}
      >
        {this.getShortSummary()}
      </button>
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
          onDatesChange={this.onDatesChange}
          focusedInput={this.state.focusedInput}
          onFocusChange={this.onFocusChange}
          onClose={this.props.onBlur}
          minimumNights={0}
          displayFormat={_DatePicker.DateFormat}
          hideKeyboardShortcutsPanel
          {...orientationProps}
        />
      </div>
    );

    return (
      <div className="search-box-date-picker">
        <div key="picker">{datePicker}</div>
        <div
          key="display"
          className={classNames(
            'search-box-date-display-wrapper-fullsize',
            this.props.focused
              ? 'search-box-date-display-wrapper-invisible'
              : ''
          )}
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

  constructor(props) {
    super(props);
    (this: any).onFocus = this.onFocus.bind(this);
  }

  onFocus(e) {
    e.target.select();
    this.props.onFocus(e);
  }

  renderItem(item, isHighlighted) {
    return (
      <div
        key={item.label}
        className={classNames(
          'search-box-autocomplete-item',
          isHighlighted ? 'search-box-autocomplete-item-selected' : ''
        )}
      >
        {item.main ? (
          <div>
            <i className="fa fa-map-marker search-box-autocomplete-item-map-icon" />
            <strong>{item.main}</strong>{' '}
            <small className="search-box-autocomplete-item-text2">
              {item.secondary}
            </small>
          </div>
        ) : (
          item.label
        )}
      </div>
    );
  }

  renderMenu(items) {
    return items.length ? (
      <div className="search-box-autocomplete-menu">{items}</div>
    ) : (
      <div />
    );
  }

  render() {
    const { id, placeholder, value, ...otherProps } = this.props;

    const inputProps = {
      id: this.props.id,
      type: 'text',
      className: 'top-search search-box-text-input',
      name: this.props.id,
      placeholder: this.props.placeholder,
      onFocus: this.onFocus,
      onBlur: this.props.onBlur,
    };
    if (this.props.autocomplete) {
      return (
        <Autocomplete
          inputProps={inputProps}
          value={this.props.value}
          renderItem={this.renderItem}
          // Only show the menu if we have items to show
          renderMenu={this.renderMenu}
          onSubmit={this.props.onSubmit}
          // Avoid using the 'display: inline-block" wrapperStyle defaults,
          // since we want the Autocomplete to fill up its parent div container
          wrapperStyle={null}
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
    (this: any).onFocus = this.onFocus.bind(this);
    (this: any).onBlur = this.onBlur.bind(this);
  }

  onFocus() {
    this.setState({ focused: true });
  }

  onBlur() {
    this.setState({ focused: false });
  }

  render() {
    return (
      <div
        className={classNames(
          'search-box-item',
          this.state.focused
            ? 'media-query-search-focused search-box-item-focused'
            : 'media-query-search-not-focused'
        )}
      >
        <div
          className={classNames(
            'search-box-item-inner',
            this.state.focused ? 'search-box-item-inner-focused' : ''
          )}
        >
          <i
            className={`fa fa-fw fa-${this.props
              .iconName} search-box-item-icon`}
          />
          <div className="search-box-item-contents">
            {this.props.renderItem({
              focused: this.state.focused,
              onFocus: this.onFocus,
              onBlur: this.onBlur,
            })}
          </div>
        </div>
      </div>
    );
  }
}

class LocationSearchBox extends React.Component {
  props: {
    initialLocation: string,
    performSearch: () => Promise<void>,
  };

  state: {
    location: string,
    locationItems: Array<string>,
  };

  _autoCompleteService: Object;

  constructor(props) {
    super(props);
    this.state = {
      location: this.props.initialLocation,
      locationItems: [],
    };
    (this: any).onLocationChange = this.onLocationChange.bind(this);
    (this: any).onLocationLookup = this.onLocationLookup.bind(this);
    (this: any).onLocationSelect = this.onLocationSelect.bind(this);
  }

  onLocationChange(event, value) {
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
      this.onLocationLookup
    );
  }

  onLocationLookup(predictions, status) {
    let items = [];
    if (status === window.google.maps.places.PlacesServiceStatus.OK) {
      items = predictions.map(x => ({
        label: x.description,
        main: x.structured_formatting.main_text,
        secondary: x.structured_formatting.secondary_text,
      }));
    }
    this.setState({ locationItems: items });
  }

  async onLocationSelect(value, item) {
    await this.setState({ location: value });
  }

  getAutocompleteService() {
    if (this._autoCompleteService) {
      return this._autoCompleteService;
    }
    this._autoCompleteService = new window.google.maps.places
      .AutocompleteService();
    return this._autoCompleteService;
  }

  getItemLabel(item) {
    return item.label;
  }

  render() {
    return (
      <SearchBoxItem
        iconName="globe"
        renderItem={({ focused, onFocus, onBlur }) => (
          <TextInput
            autocomplete
            id="location"
            placeholder={focused ? 'City, Region, or Country' : 'Anywhere'}
            value={this.state.location}
            items={this.state.locationItems}
            onSubmit={this.props.performSearch}
            onChange={this.onLocationChange}
            getItemValue={this.getItemLabel}
            onSelect={this.onLocationSelect}
            onFocus={onFocus}
            onBlur={onBlur}
          />
        )}
      />
    );
  }
}

class KeywordSearchBox extends React.Component {
  props: {
    initialKeywords: string,
    performSearch: () => Promise<void>,
  };

  state: {
    keywords: string,
  };

  constructor(props) {
    super(props);
    this.state = {
      keywords: this.props.initialKeywords,
    };
    (this: any).onKeywordsChange = this.onKeywordsChange.bind(this);
    (this: any).onKeywordsSelect = this.onKeywordsSelect.bind(this);
  }

  onKeywordsChange(event, value) {
    this.setState({ keywords: value });
  }

  async onKeywordsSelect(value, item) {
    await this.setState({ keywords: value });
  }

  getItemLabel(item) {
    return item.label;
  }

  shouldKeywordItemRender(item, value) {
    if (value.length) {
      return item.label.toLowerCase().indexOf(value.toLowerCase()) !== -1;
    } else {
      return item.initial;
    }
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

  render() {
    return (
      <SearchBoxItem
        iconName="search"
        renderItem={({ focused, onFocus, onBlur }) => (
          <TextInput
            autocomplete
            id="keywords"
            placeholder={
              focused ? (
                'Dance style, event name, dancer name, etc'
              ) : (
                'Any style, event type, etc'
              )
            }
            value={this.state.keywords}
            onSubmit={this.props.performSearch}
            onChange={this.onKeywordsChange}
            onSelect={this.onKeywordsSelect}
            items={this.autocompleteKeywords()}
            getItemValue={this.getItemLabel}
            shouldItemRender={this.shouldKeywordItemRender}
            onFocus={onFocus}
            onBlur={onBlur}
          />
        )}
      />
    );
  }
}

class DateSearchBox extends React.Component {
  props: {
    query: Query,
  };
  render() {
    return (
      <SearchBoxItem
        iconName="clock-o"
        renderItem={({ focused, onFocus, onBlur }) => (
          <DatePicker
            query={this.props.query}
            focused={focused}
            onFocus={onFocus}
            onBlur={onBlur}
          />
        )}
      />
    );
  }
}

class _SearchBox extends React.Component {
  props: {
    query: Query,
    onNewSearch: (form: Object) => void,
    // Self-managed props
    // intl: intlShape,
  };

  _form: Object;

  constructor(props) {
    super(props);
    (this: any).performSearch = this.performSearch.bind(this);
    (this: any).saveRef = this.saveRef.bind(this);
  }

  async performSearch() {
    if (!this._form) {
      console.warn('Error, called performSearch before form has been setup');
      return;
    }
    const form = {};
    [...this._form.elements].forEach(field => {
      if (field.name !== '') {
        form[field.name] = field.value;
      }
    });
    this.props.onNewSearch(form);
  }

  saveRef(x) {
    this._form = x;
  }

  render() {
    const hiddenFields = this.props.query.deb ? (
      <input type="hidden" name="deb" value={this.props.query.deb} />
    ) : null;

    return (
      <div>
        <div className="search-box-outer">Find the Dance Scene:</div>
        <form
          id="search-form"
          ref={this.saveRef}
          role="search"
          className="form-inline"
          action="/"
          acceptCharset="UTF-8"
        >
          <div className="media-query-search-box search-box">
            <LocationSearchBox
              initialLocation={this.props.query.location}
              performSearch={this.performSearch}
            />
            <KeywordSearchBox
              initialKeywords={this.props.query.keywords}
              performSearch={this.performSearch}
            />
            <DateSearchBox
              query={this.props.query}
              performSearch={this.performSearch}
            />
            <div>
              <button
                className="btn btn-default media-query-search-button search-box-search-button"
                type="button"
                onClick={this.performSearch}
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

export function canonicalizeQuery(query) {
  const newQuery = {};
  ['location', 'keywords', 'start', 'end'].forEach(key => {
    if (query[key] && query[key].length) {
      newQuery[key] = query[key];
    }
  });
  return newQuery;
}
