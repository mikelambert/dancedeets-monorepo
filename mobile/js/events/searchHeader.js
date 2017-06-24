/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Animated, StyleSheet, TextInput, View } from 'react-native';
import SyntheticEvent from 'react-native/Libraries/Renderer/src/renderers/shared/shared/event/SyntheticEvent';
import Locale from 'react-native-locale';
import { connect } from 'react-redux';
import { defineMessages, injectIntl, intlShape } from 'react-intl';
import Icon from 'react-native-vector-icons/Ionicons';
import { Event } from 'dancedeets-common/js/events/models';
import type { SearchQuery } from 'dancedeets-common/js/events/search';
import { AutocompleteList, Button, defaultFont, HorizontalView } from '../ui';
import { performSearch, updateLocation, updateKeywords } from '../actions';
import { gradientBottom, gradientTop, lightPurpleColors } from '../Colors';
import type { State as SearchHeaderState } from '../ducks/searchHeader';

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

class SearchInput extends React.Component {
  props: {
    onFocus?: () => void,
    onBlur?: () => void,
    onSubmitEditing: () => void | Promise<void>,
    iconName: string,
  };
  state: {
    focused: boolean,
  };

  _textInput: TextInput;

  constructor(props) {
    super(props);
    (this: any).focus = this.focus.bind(this);
    (this: any).blur = this.blur.bind(this);
    (this: any).animatedRelayout = this.animatedRelayout.bind(this);

    this.state = {
      focused: false,
    };
  }

  animatedRelayout() {
    this.setState({ focused: this._textInput.isFocused() });
  }

  blur() {
    this._textInput.blur();
  }

  focus() {
    this._textInput.focus();
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
            this._textInput.blur();
          }}
        />
      </HorizontalView>
    );
  }
}

class _SearchHeader extends React.Component {
  props: {
    children: Array<React.Element<*>>,

    // Self-managed props
    intl: intlShape,
    searchQuery: SearchQuery,
    searchHeader: SearchHeaderState,
    updateLocation: (location: string) => void,
    updateKeywords: (keywords: string) => void,
    performSearch: () => Promise<void>,
  };

  state: {
    height: number,
  };

  _location: SearchInput;
  _keywords: SearchInput;
  _locationAutocomplete: AutocompleteList;

  constructor(props) {
    super(props);
    this.state = {
      height: 0,
    };
    (this: any).onLayout = this.onLayout.bind(this);
  }

  onLayout(e: SyntheticEvent) {
    const nativeEvent: any = e.nativeEvent;
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
            this._keywords = x;
          }}
          iconName={'md-search'}
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
          autoFocus
        />
        <SearchInput
          ref={x => {
            this._location = x;
          }}
          iconName={'md-locate'}
          style={{ marginTop: 5 }}
          placeholder={this.props.intl.formatMessage(messages.location)}
          returnKeyType="search"
          onChangeText={text => {
            if (this.props.searchQuery.location !== text) {
              this.props.updateLocation(text);
              this._locationAutocomplete.onTextInputChangeText(text);
            }
          }}
          onFocus={() => {
            this._locationAutocomplete.onTextInputFocus();
          }}
          onBlur={() => {
            this._locationAutocomplete.onTextInputBlur();
          }}
          onSubmitEditing={() => {
            this._locationAutocomplete.onTextInputBlur();
            this.props.performSearch();
          }}
          value={this.props.searchQuery.location}
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
          this._location.blur();
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
        {this.props.searchHeader.searchFormVisible
          ? this.renderAutoComplete()
          : null}
      </View>
    );
  }
}
const SearchHeader = connect(
  state => ({
    searchQuery: state.searchQuery,
    searchHeader: state.searchHeader,
  }),
  dispatch => ({
    updateLocation: async location => {
      await dispatch(updateLocation(location));
    },
    updateKeywords: async keywords => {
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
