/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Animated, StyleSheet, TextInput, View } from 'react-native';
import Locale from 'react-native-locale';
import { connect } from 'react-redux';
import { defineMessages, injectIntl, IntlShape } from 'react-intl';
import Icon from 'react-native-vector-icons/Ionicons';
import { Event } from 'dancedeets-common/js/events/models';
import { SearchQuery } from 'dancedeets-common/js/events/search';
import { AutocompleteList, Button, defaultFont, HorizontalView } from '../ui';
import { performSearch, updateLocation, updateKeywords } from '../actions';
import { gradientTop, lightPurpleColors } from '../Colors';
import { State as SearchHeaderState } from '../ducks/searchHeader';

const messages = defineMessages({
  location: {
    id: 'search.locationPlaceholder',
    defaultMessage: 'Location',
    description:
      'The placeholder for the text field where you enter the location',
  },
  keywords: {
    id: 'search.keywordsPlaceholder',
    defaultMessage: 'Keywords',
    description:
      'The placeholder for the text field where you enter the keywords',
  },
  locations: {
    id: 'search.autocompleteLocations',
    defaultMessage:
      'New York City, United States\nLos Angeles, United States\nSan Francisco, United States\nWashington DC, United States\nLondon, United Kingdom\nParis, France\nTokyo, Japan\nTaipei, Taiwan\nSeoul, South Korea',
    description: 'A list of locations that we should show in our autocomplete',
  },
  currentLocation: {
    id: 'search.autocompleteCurrentLocation',
    defaultMessage: 'Current Location',
    description:
      'The autocomplete item that will ask the GPS for the current location to perform a search with',
  },
});

interface SearchInputProps {
  onFocus?: () => void;
  onBlur?: () => void;
  onSubmitEditing: () => void | Promise<void>;
  iconName: string;
  style?: any;
  placeholder?: string;
  returnKeyType?: 'done' | 'go' | 'next' | 'search' | 'send' | 'default';
  onChangeText?: (text: string) => void;
  value?: string;
  autoFocus?: boolean;
}

interface SearchInputState {
  focused: boolean;
}

class SearchInput extends React.Component<SearchInputProps, SearchInputState> {
  _textInput: TextInput | null = null;

  constructor(props: SearchInputProps) {
    super(props);
    this.focus = this.focus.bind(this);
    this.blur = this.blur.bind(this);
    this.animatedRelayout = this.animatedRelayout.bind(this);

    this.state = {
      focused: false,
    };
  }

  animatedRelayout() {
    if (this._textInput) {
      this.setState({ focused: this._textInput.isFocused() });
    }
  }

  blur() {
    if (this._textInput) {
      this._textInput.blur();
    }
  }

  focus() {
    if (this._textInput) {
      this._textInput.focus();
    }
  }

  render() {
    const { style, iconName, ...otherProps } = { ...this.props };
    return (
      <HorizontalView>
        <Icon
          name={iconName}
          size={20}
          color="#FFF"
          style={{ marginTop: 10, width: 20, marginLeft: 10 }}
        />
        <TextInput
          {...otherProps}
          ref={x => {
            this._textInput = x;
          }}
          style={[defaultFont, styles.searchField, style, { flex: 1 }]}
          placeholderTextColor="rgba(255, 255, 255, 0.5)"
          keyboardAppearance="dark"
          selectTextOnFocus
          autoCorrect={false}
          autoCapitalize="none"
          clearButtonMode="always"
          underlineColorAndroid={lightPurpleColors[2]}
          onFocus={() => {
            this.animatedRelayout();
            if (this.props.onFocus) {
              this.props.onFocus();
            }
          }}
          onBlur={() => {
            this.animatedRelayout();
            if (this.props.onBlur) {
              this.props.onBlur();
            }
          }}
          onEndEditing={() => {
            this.animatedRelayout();
            if (this.props.onBlur) {
              this.props.onBlur();
            }
          }}
          onSubmitEditing={() => {
            this.animatedRelayout();
            if (this.props.onSubmitEditing) {
              this.props.onSubmitEditing();
            }
            if (this._textInput) {
              this._textInput.blur();
            }
          }}
        />
      </HorizontalView>
    );
  }
}

interface SearchHeaderProps {
  children: React.ReactNode;

  // Self-managed props
  intl: IntlShape;
  searchQuery: SearchQuery;
  searchHeader: SearchHeaderState;
  updateLocation: (location: string) => void;
  updateKeywords: (keywords: string) => void;
  performSearch: () => Promise<void>;
}

interface SearchHeaderComponentState {
  height: number;
}

class _SearchHeader extends React.Component<
  SearchHeaderProps,
  SearchHeaderComponentState
> {
  _location: SearchInput | null = null;
  _keywords: SearchInput | null = null;
  _locationAutocomplete: AutocompleteList | null = null;

  constructor(props: SearchHeaderProps) {
    super(props);
    this.state = {
      height: 0,
    };
    this.onLayout = this.onLayout.bind(this);
  }

  onLayout(e: any) {
    const { nativeEvent } = e;
    const height = nativeEvent.layout.height;
    this.setState({ height });
  }

  renderHeader() {
    return (
      <Animated.View
        onLayout={this.onLayout}
        style={[
          styles.floatTop,
          styles.statusBar,
          {
            transform: [
              {
                translateY: this.props.searchHeader.headerAnim.interpolate({
                  inputRange: [0, 1],
                  outputRange: [-200, 0],
                }),
              },
            ],
          },
        ]}
      >
        <SearchInput
          ref={x => {
            this._location = x;
          }}
          iconName="md-locate"
          style={{ marginTop: 5 }}
          placeholder={this.props.intl.formatMessage(messages.location)}
          returnKeyType="search"
          onChangeText={text => {
            if (this.props.searchQuery.location !== text) {
              this.props.updateLocation(text);
              if (this._locationAutocomplete) {
                this._locationAutocomplete.onTextInputChangeText(text);
              }
            }
          }}
          onFocus={() => {
            if (this._locationAutocomplete) {
              this._locationAutocomplete.onTextInputFocus();
            }
          }}
          onBlur={() => {
            if (this._locationAutocomplete) {
              this._locationAutocomplete.onTextInputBlur();
            }
          }}
          onSubmitEditing={() => {
            if (this._locationAutocomplete) {
              this._locationAutocomplete.onTextInputBlur();
            }
            this.props.performSearch();
          }}
          value={this.props.searchQuery.location}
          autoFocus
        />
        <SearchInput
          ref={x => {
            this._keywords = x;
          }}
          iconName="md-search"
          style={{ marginTop: 5 }}
          placeholder={this.props.intl.formatMessage(messages.keywords)}
          returnKeyType="search"
          onChangeText={text => {
            if (this.props.searchQuery.keywords !== text) {
              this.props.updateKeywords(text);
            }
          }}
          onSubmitEditing={() => this.props.performSearch()}
          value={this.props.searchQuery.keywords}
        />
      </Animated.View>
    );
  }

  renderAutoComplete() {
    return (
      <AutocompleteList
        ref={x => {
          this._locationAutocomplete = x;
        }}
        style={{ top: this.state.height }}
        textValue={() => this.props.searchQuery.location}
        queryLanguage={Locale.constants().localeIdentifier}
        currentLocationLabel={this.props.intl.formatMessage(
          messages.currentLocation
        )}
        onLocationSelected={async text => {
          await this.props.updateLocation(text);
          if (this._location) {
            this._location.blur();
          }
          await this.props.performSearch();
        }}
        predefinedPlaces={this.props.intl
          .formatMessage(messages.locations)
          .split('\n')
          .map(x => ({ description: x }))}
      />
    );
  }

  render() {
    return (
      <View style={{ flex: 1 }}>
        {this.props.searchHeader.searchFormVisible ? this.renderHeader() : null}
        {this.props.children}
        {this.props.searchHeader.searchFormVisible ? (
          this.renderAutoComplete()
        ) : null}
      </View>
    );
  }
}

const SearchHeader = connect(
  (state: any) => ({
    searchQuery: state.searchQuery,
    searchHeader: state.searchHeader,
  }),
  (dispatch: any) => ({
    updateLocation: async (location: string) => {
      await dispatch(updateLocation(location));
    },
    updateKeywords: async (keywords: string) => {
      await dispatch(updateKeywords(keywords));
    },
    performSearch: async () => {
      await dispatch(performSearch());
    },
  })
)(injectIntl(_SearchHeader));

export default SearchHeader;

const styles = StyleSheet.create({
  floatTop: {
    top: 0,
    left: 0,
    right: 0,
  },
  statusBar: {
    justifyContent: 'space-between',
    backgroundColor: gradientTop,
    paddingBottom: 4,
  },
  searchField: {
    height: 30,
    padding: 4,
    color: 'white',
    borderRadius: 5,
    marginHorizontal: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
});
