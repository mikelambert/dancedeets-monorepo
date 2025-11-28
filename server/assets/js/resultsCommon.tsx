/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import moment from 'moment';
import classNames from 'classnames';
import { injectIntl } from 'react-intl';
import Autocomplete from 'react-autocomplete';
import { DateRangePicker } from 'react-dates';
import { wantsWindowSizes } from './ui';
import type { WindowProps } from './ui';

// Keep in sync with results.scss's NarrowWindowSize
const NarrowWindowSize = 768;

export const CalendarRatio = 1.8;

export interface Query {
  location?: string;
  keywords?: string;
  start?: string;
  end?: string;
  deb?: string;
  min_worth?: number;
}

interface DatePickerProps {
  query: Query;
  focused: boolean;
  onFocus: () => void;
  onBlur: () => void;
  onComplete?: () => void;
  window: WindowProps;
}

interface DatePickerState {
  startDate: moment.Moment | null;
  endDate: moment.Moment | null;
  focusedInput: 'startDate' | 'endDate' | null;
}

class _DatePicker extends React.Component<DatePickerProps, DatePickerState> {
  static DateFormat = 'MMM Do';

  constructor(props: DatePickerProps) {
    super(props);
    this.state = {
      startDate: props.query.start ? moment(props.query.start) : null,
      endDate: props.query.end ? moment(props.query.end) : null,
      focusedInput: null,
    };
    this.onFocusClick = this.onFocusClick.bind(this);
    this.onDatesChange = this.onDatesChange.bind(this);
    this.onFocusChange = this.onFocusChange.bind(this);
  }

  componentDidUpdate(prevProps: DatePickerProps, prevState: DatePickerState): void {
    // Once the component has been updated, and re-rendered the <input>s with new values
    // Let's perform a search based off them
    if (prevState.focusedInput !== null && this.state.focusedInput === null) {
      if (this.props.onComplete) {
        this.props.onComplete();
      }
    }
  }

  onFocusClick(): void {
    this.props.onFocus();
    this.setState({ focusedInput: 'startDate' });
  }

  onDatesChange({ startDate, endDate }: { startDate: moment.Moment | null; endDate: moment.Moment | null }): void {
    this.setState({ startDate, endDate });
  }

  onFocusChange(focusedInput: 'startDate' | 'endDate' | null): void {
    this.setState({ focusedInput });
    this.props.onFocus();
  }

  getShortSummary(): string {
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

  render(): React.ReactElement {
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
          orientation: 'vertical' as const,
          withFullScreenPortal: true,
        }
      : { orientation: 'horizontal' as const };
    const datePicker = (
      <div key="date-picker">
        <DateRangePicker
          // orientation="vertical"
          startDateId="start"
          endDateId="end"
          isOutsideRange={() => false}
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
const DatePicker = wantsWindowSizes(_DatePicker);

function findNextTabStop(el: HTMLElement): HTMLElement {
  const universe = (global as unknown as { window: Window }).window.document.querySelectorAll(
    'input, button, select, textarea, a[href]'
  );
  const list = Array.prototype.filter.call(
    universe,
    (item: HTMLElement) => (item as HTMLInputElement).tabIndex >= 0
  );
  const index = list.indexOf(el);
  return list[index + 1] || list[0];
}

function HandleSelection(this: Autocomplete, event: React.KeyboardEvent<HTMLInputElement>): void {
  const { target } = event;
  const { key } = event;
  if (!this.isOpen() || (this.state as { highlightedIndex: number | null }).highlightedIndex == null) {
    // menu is closed so there is no selection to accept -> do nothing
    this.setState({ isOpen: false }, () => {
      (this.props as { onSelect: (value: string) => void }).onSelect((target as HTMLInputElement).value);
      if (key === 'Enter') {
        // Don't run this code for Tab, or it will double-Tab
        findNextTabStop(target as HTMLInputElement).focus();
        // Only submit form on "Enter" on a form field without any menu item selected
        (this.props as { onSubmit: () => void }).onSubmit();
      }
    });
  } else {
    // text entered + menu item has been highlighted + enter is hit -> update value to that of selected menu item, close the menu
    event.preventDefault();
    const item = (this as unknown as { getFilteredItems: (props: unknown) => Array<{ label: string }> }).getFilteredItems(this.props)[(this.state as { highlightedIndex: number }).highlightedIndex];
    const value = (this.props as { getItemValue: (item: { label: string }) => string }).getItemValue(item);
    this.setState(
      {
        isOpen: false,
        highlightedIndex: null,
      },
      () => {
        // this.refs.input.focus() // TODO: file issue
        ((this as unknown as { refs: { input: HTMLInputElement } }).refs.input as HTMLInputElement).setSelectionRange(value.length, value.length);
        (this.props as { onSelect: (value: string, item: unknown) => void }).onSelect(value, item);
      }
    );
  }
}

function HandleArrowDown(this: Autocomplete, event: React.KeyboardEvent<HTMLInputElement>): void {
  event.preventDefault();
  const itemsLength = (this as unknown as { getFilteredItems: (props: unknown) => unknown[] }).getFilteredItems(this.props).length;
  if (!itemsLength) return;
  const { highlightedIndex } = this.state as { highlightedIndex: number | null };
  let index: number | null;
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

function HandleArrowUp(this: Autocomplete, event: React.KeyboardEvent<HTMLInputElement>): void {
  event.preventDefault();
  const itemsLength = (this as unknown as { getFilteredItems: (props: unknown) => unknown[] }).getFilteredItems(this.props).length;
  if (!itemsLength) return;
  const { highlightedIndex } = this.state as { highlightedIndex: number | null };
  let index: number | null;
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
(Autocomplete as unknown as { keyDownHandlers: Record<string, unknown> }).keyDownHandlers.Tab = HandleSelection;
(Autocomplete as unknown as { keyDownHandlers: Record<string, unknown> }).keyDownHandlers.Enter = HandleSelection;
(Autocomplete as unknown as { keyDownHandlers: Record<string, unknown> }).keyDownHandlers.ArrowDown = HandleArrowDown;
(Autocomplete as unknown as { keyDownHandlers: Record<string, unknown> }).keyDownHandlers.ArrowUp = HandleArrowUp;

interface AutocompleteItem {
  label: string;
  main?: string;
  secondary?: string;
  initial?: boolean;
}

interface TextInputProps {
  id: string;
  placeholder: string;
  value: string;
  onFocus: (e: React.FocusEvent<HTMLInputElement>) => void;
  onBlur: (e: React.FocusEvent<HTMLInputElement>) => void;
  onSubmit: () => void | Promise<void>;
  shouldItemRender?: (item: AutocompleteItem, value: string) => boolean;
  autocomplete?: boolean;
  items?: AutocompleteItem[];
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, value: string) => void;
  getItemValue?: (item: AutocompleteItem) => string;
  onSelect?: (value: string, item?: AutocompleteItem) => void;
}

class TextInput extends React.Component<TextInputProps> {
  constructor(props: TextInputProps) {
    super(props);
    this.onFocus = this.onFocus.bind(this);
  }

  onFocus(e: React.FocusEvent<HTMLInputElement>): void {
    e.target.select();
    this.props.onFocus(e);
  }

  renderItem(item: AutocompleteItem, isHighlighted: boolean): React.ReactElement {
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

  renderMenu(items: React.ReactElement[]): React.ReactElement {
    return items.length ? (
      <div className="search-box-autocomplete-menu">{items}</div>
    ) : (
      <div />
    );
  }

  render(): React.ReactElement {
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
          wrapperStyle={undefined}
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

interface SearchBoxItemProps {
  iconName: string;
  renderItem: (args: {
    focused: boolean;
    onFocus: () => void;
    onBlur: () => void;
  }) => React.ReactElement;
}

interface SearchBoxItemState {
  focused: boolean;
}

class SearchBoxItem extends React.Component<SearchBoxItemProps, SearchBoxItemState> {
  constructor(props: SearchBoxItemProps) {
    super(props);
    this.state = { focused: false };
    this.onFocus = this.onFocus.bind(this);
    this.onBlur = this.onBlur.bind(this);
  }

  onFocus(): void {
    this.setState({ focused: true });
  }

  onBlur(): void {
    this.setState({ focused: false });
  }

  render(): React.ReactElement {
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

interface LocationSearchBoxProps {
  initialLocation: string;
  performSearch: () => Promise<void>;
}

interface LocationSearchBoxState {
  location: string;
  locationItems: AutocompleteItem[];
}

class LocationSearchBox extends React.Component<LocationSearchBoxProps, LocationSearchBoxState> {
  _autoCompleteService: google.maps.places.AutocompleteService | null = null;

  constructor(props: LocationSearchBoxProps) {
    super(props);
    this.state = {
      location: this.props.initialLocation,
      locationItems: [],
    };
    this.onLocationChange = this.onLocationChange.bind(this);
    this.onLocationLookup = this.onLocationLookup.bind(this);
    this.onLocationSelect = this.onLocationSelect.bind(this);
  }

  onLocationChange(_event: React.ChangeEvent<HTMLInputElement>, value: string): void {
    this.setState({ location: value });
    if (!value) {
      return;
    }
    // TODO: Cancel/ignore old prediction requests, in case they arrive out-of-order
    const autocompleteService = this.getAutocompleteService();
    if (autocompleteService) {
      autocompleteService.getPlacePredictions(
        {
          input: value,
          types: ['(regions)'],
        },
        this.onLocationLookup
      );
    }
  }

  onLocationLookup(predictions: google.maps.places.AutocompletePrediction[] | null, status: google.maps.places.PlacesServiceStatus): void {
    let items: AutocompleteItem[] = [];
    if (status === window.google.maps.places.PlacesServiceStatus.OK && predictions) {
      items = predictions.map(x => ({
        label: x.description,
        main: x.structured_formatting.main_text,
        secondary: x.structured_formatting.secondary_text,
      }));
    }
    this.setState({ locationItems: items });
  }

  async onLocationSelect(value: string): Promise<void> {
    await this.setState({ location: value });
  }

  getAutocompleteService(): google.maps.places.AutocompleteService | null {
    if (this._autoCompleteService) {
      return this._autoCompleteService;
    }
    // Try to construct it if possible, otherwise leave it alone
    // and let it try again next time, when the maps js may have downloaded
    if (window.google && window.google.maps && window.google.maps.places) {
      this._autoCompleteService = new window.google.maps.places
        .AutocompleteService();
    }
    return this._autoCompleteService;
  }

  getItemLabel(item: AutocompleteItem): string {
    return item.label;
  }

  render(): React.ReactElement {
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

interface KeywordSearchBoxProps {
  initialKeywords: string;
  performSearch: () => Promise<void>;
}

interface KeywordSearchBoxState {
  keywords: string;
}

class KeywordSearchBox extends React.Component<KeywordSearchBoxProps, KeywordSearchBoxState> {
  constructor(props: KeywordSearchBoxProps) {
    super(props);
    this.state = {
      keywords: this.props.initialKeywords,
    };
    this.onKeywordsChange = this.onKeywordsChange.bind(this);
    this.onKeywordsSelect = this.onKeywordsSelect.bind(this);
  }

  onKeywordsChange(_event: React.ChangeEvent<HTMLInputElement>, value: string): void {
    this.setState({ keywords: value });
  }

  async onKeywordsSelect(value: string): Promise<void> {
    await this.setState({ keywords: value });
  }

  getItemLabel(item: AutocompleteItem): string {
    return item.label;
  }

  shouldKeywordItemRender(item: AutocompleteItem, value: string): boolean {
    if (value.length) {
      return item.label.toLowerCase().indexOf(value.toLowerCase()) !== -1;
    } else {
      return !!item.initial;
    }
  }

  autocompleteKeywords(): AutocompleteItem[] {
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

  render(): React.ReactElement {
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

interface DateSearchBoxProps {
  query: Query;
  performSearch?: () => Promise<void>;
}

class DateSearchBox extends React.Component<DateSearchBoxProps> {
  render(): React.ReactElement {
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

interface SearchBoxProps {
  query: Query;
  onNewSearch: (form: Record<string, string>) => void;
}

class _SearchBox extends React.Component<SearchBoxProps> {
  _form: HTMLFormElement | null = null;

  constructor(props: SearchBoxProps) {
    super(props);
    this.performSearch = this.performSearch.bind(this);
    this.saveRef = this.saveRef.bind(this);
  }

  async performSearch(): Promise<void> {
    if (!this._form) {
      console.warn('Error, called performSearch before form has been setup');
      return;
    }
    const form: Record<string, string> = {};
    [...this._form.elements].forEach(field => {
      const inputField = field as HTMLInputElement;
      if (inputField.name !== '') {
        form[inputField.name] = inputField.value;
      }
    });
    this.props.onNewSearch(form);
  }

  saveRef(x: HTMLFormElement | null): void {
    this._form = x;
  }

  render(): React.ReactElement {
    const hiddenFields = (['deb', 'min_worth'] as const)
      .filter(x => (this.props.query as Record<string, unknown>)[x] != null)
      .map(x => (
        <input key={x} type="hidden" name={x} value={String((this.props.query as Record<string, unknown>)[x])} />
      ));

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
export const SearchBox = _SearchBox;

export function canonicalizeQuery(query: Query): Partial<Query> {
  const newQuery: Partial<Query> = {};
  console.log('old query', query);
  (['location', 'keywords', 'start', 'end'] as const).forEach(key => {
    if (query[key] && query[key].length) {
      newQuery[key] = query[key];
    }
  });
  if (query.min_worth) {
    newQuery.min_worth = query.min_worth;
  }
  console.log('canonicalized query', newQuery);
  return newQuery;
}

// Declare google namespace for TypeScript
declare global {
  interface Window {
    google?: {
      maps?: {
        places?: {
          AutocompleteService: new () => google.maps.places.AutocompleteService;
          PlacesServiceStatus: {
            OK: google.maps.places.PlacesServiceStatus;
          };
        };
      };
    };
  }
  namespace google {
    namespace maps {
      namespace places {
        interface AutocompleteService {
          getPlacePredictions(
            request: { input: string; types: string[] },
            callback: (predictions: AutocompletePrediction[] | null, status: PlacesServiceStatus) => void
          ): void;
        }
        interface AutocompletePrediction {
          description: string;
          structured_formatting: {
            main_text: string;
            secondary_text: string;
          };
        }
        type PlacesServiceStatus = string;
      }
    }
  }
}
