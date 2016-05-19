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

import { BlurView } from 'react-native-blur';
import { connect } from 'react-redux';
import {
  defaultFont,
  AutocompleteList
} from '../ui';

import {
  performSearch,
  updateLocation,
  updateKeywords
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
  {description: 'New York City, USA'},
  {description: 'Los Angeles, USA'},
  {description: 'Paris, France'},
  {description: 'London, UK'},
  {description: 'Tokyo, Japan'},
  {description: 'Osaka, Japan'},
  {description: 'Seoul, Korea'},
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
    this.props.onUpdateHeight(height);
  }

  render() {
    return <View style={{flex: 1,top:0, left:0, right:0,position: 'absolute'}}>
      <BlurView
        onLayout={this.onLayout}
        style={[{paddingTop: StatusBar.currentHeight}, styles.floatTop, styles.statusBar]}
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
          onSubmitEditing={() => this.props.performSearch(this.props.searchQuery)}
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

      </BlurView>
      <AutocompleteList
        ref="location_autocomplete"
        style={{top: this.state.height}}
        textValue={()=>this.props.searchQuery.location}
        onLocationSelected={(text) => {
          this.props.updateLocation(text);
          this.props.performSearch(this.props.searchQuery);
          this.refs.location.blur();
        }}
        predefinedPlaces={locations}
      />
    </View>;
  }
}

const mapStateToProps = (state) => {
  return {
    searchQuery: state.search.searchQuery,
  };
};
const mapDispatchToProps = (dispatch) => {
  return {
    updateLocation: (location) => {
      dispatch(updateLocation(location));
    },
    updateKeywords: (keywords) => {
      dispatch(updateKeywords(keywords));
    },
    performSearch: (searchQuery) => {
      dispatch(performSearch(searchQuery));
    },
  };
};
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SearchHeader);


const styles = StyleSheet.create({
  floatTop: {
    position: 'absolute',
    paddingTop: 15,
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
    height: 30,
    flex: 1,
    margin: 3,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  focusedField: {
    flex: 3,
  },
});
