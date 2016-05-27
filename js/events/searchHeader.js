/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  UIManager,
  LayoutAnimation,
  StatusBar,
  StyleSheet,
  TextInput,
  View,
} from 'react-native';

import { connect } from 'react-redux';
import {
  Button,
  defaultFont,
  AutocompleteList
} from '../ui';

import {
  performSearch,
  toggleLayout,
  updateLocation,
  updateKeywords,
} from '../actions';


class SearchInput extends React.Component {
  state: {
    focused: boolean,
  };

  constructor(props) {
    super(props);
    (this: any).focus = this.focus.bind(this);
    (this: any).blur = this.blur.bind(this);
    (this: any).animatedRelayout = this.animatedRelayout.bind(this);
    UIManager.setLayoutAnimationEnabledExperimental && UIManager.setLayoutAnimationEnabledExperimental(true);
    this.state = {
      focused: false,
    };
  }

  animatedRelayout() {
    this.setState({focused: this.refs.textInput.isFocused()});
    LayoutAnimation.easeInEaseOut();
  }

  render() {
    const { style, ...otherProps } = { style: {}, ...this.props };
    return <TextInput {...otherProps}
      ref="textInput"
      style={[style, styles.searchField, this.state.focused ? styles.focusedField : {}, defaultFont]}
      placeholderTextColor="rgba(255, 255, 255, 0.5)"
      //backgroundColor="rgba(255, 255, 255, 0.2)"
      keyboardAppearance="dark"
      selectTextOnFocus={true}
      autoCorrect={false}
      autoCapitalize="none"
      clearButtonMode="while-editing"
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
      }}
    />;
  }

  blur() {
    this.refs.textInput.blur();
  }

  focus() {
    this.refs.textInput.focus();
  }
}

const locations = [
  {description: 'New York City, United States'},
  {description: 'Los Angeles, United States'},
  {description: 'Paris, France'},
  {description: 'London, United Kingdom'},
  {description: 'Tokyo, Japan'},
  {description: 'Osaka, Japan'},
  {description: 'Seoul, South Korea'},
  {description: 'Taipei, Taiwan'},
];


class SearchHeader extends React.Component {
  state: {
    height: number;
  };
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
    this.setState({height});
  }

  render() {
    return <View style={{flex: 1}}>
      <View
        onLayout={this.onLayout}
        style={[{paddingTop: StatusBar.currentHeight || 15}, styles.floatTop, styles.statusBar]}
        blurType="dark"
      >
        <SearchInput
          ref="location"
          placeholder="Location"
          returnKeyType="search"
          onChangeText={(text) => {
            this.props.updateLocation(text);
            this.refs.location_autocomplete.onTextInputChangeText(text);
          }}
          onFocus={() => {
            this.refs.location_autocomplete.onTextInputFocus();
          }}
          onBlur={() => {
            this.refs.location_autocomplete.onTextInputBlur();
          }}
          onSubmitEditing={() => {
            this.refs.location_autocomplete.onTextInputBlur();
            this.props.performSearch(this.props.searchQuery);
          }}
          value={this.props.searchQuery.location}
        />
        <SearchInput
          ref="keywords"
          placeholder="Keywords"
          returnKeyType="search"
          onChangeText={(text) => this.props.updateKeywords(text)}
          onSubmitEditing={() => this.props.performSearch(this.props.searchQuery)}
          value={this.props.searchQuery.keywords}
        />
        <Button
          size="small"
          icon={this.props.listLayout ? require('./search-images/large-flyer.png') : require('./search-images/small-flyer.png')}
          onPress={this.props.toggleLayout}
          />
      </View>
      {this.props.children}
      <AutocompleteList
        ref="location_autocomplete"
        style={{top: this.state.height}}
        textValue={()=>this.props.searchQuery.location}
        onLocationSelected={async (text) => {
          await this.props.updateLocation(text);
          this.refs.location.blur();
          await this.props.performSearch(this.props.searchQuery);
        }}
        predefinedPlaces={locations}
      />
    </View>;
  }
}

const mapStateToProps = (state) => {
  return {
    listLayout: state.search.listLayout,
    searchQuery: state.search.searchQuery,
  };
};
const mapDispatchToProps = (dispatch) => {
  return {
    updateLocation: async (location) => {
      await dispatch(updateLocation(location));
    },
    updateKeywords: async (keywords) => {
      await dispatch(updateKeywords(keywords));
    },
    performSearch: async (searchQuery) => {
      await dispatch(performSearch(searchQuery));
    },
    toggleLayout: async () => {
      await dispatch(toggleLayout());
    },
  };
};
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SearchHeader);


const styles = StyleSheet.create({
  floatTop: {
    top: 0,
    left: 0,
    right: 0,
  },
  statusBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
  },
  searchField: {
    color: 'white',
    borderRadius: 5,
    flex: 1,
    marginLeft: 3,
    marginRight: 3,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  focusedField: {
    flex: 3,
  },
});
