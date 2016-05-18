/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
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
  constructor(props) {
    super(props);
    (this: any).focus = this.focus.bind(this);
  }

  render() {
    const { style, ...otherProps } = { style: {}, ...this.props };
    return <TextInput {...otherProps}
      ref="textInput"
      style={[style, styles.searchField, this.refs.textInput && this.refs.textInput.isFocused() ? styles.focusedField : {}, defaultFont]}
      placeholderTextColor="rgba(255, 255, 255, 0.5)"
      //backgroundColor="rgba(255, 255, 255, 0.2)"
      keyboardAppearance="dark"
      selectTextOnFocus={true}
      autoCorrect={false}
      autoCapitalize="none"
      clearButtonMode="while-editing"
      onFocus={()=>{this.forceUpdate();}}
      onBlur={()=>{this.forceUpdate();}}
    />;
  }

  focus() {
    this.refs.textInput.focus();
  }
}

const locations = [
  {description: 'New York City', geometry: { location: { lat: 40.7058254, lng: -74.1180861 } }},
  {description: 'Los Angeles', geometry: { location: { lat: 34.0207504, lng: -118.691914 } }},
  {description: 'Paris', geometry: { location: { lat: 48.8589101, lng: 2.3125376 } }},
  {description: 'Tokyo', geometry: { location: { lat: 35.6735408, lng: 139.5703049 } }},
  {description: 'Osaka', geometry: { location: { lat: 34.678434, lng: 135.4776404 } }},
  {description: 'Taipei', geometry: { location: { lat: 25.0855451, lng: 121.4932093 } }},
];


class SearchHeader extends React.Component {
  constructor(props) {
    super(props);
    (this: any).onLayout = this.onLayout.bind(this);
  }

  onLayout(e: SyntheticEvent) {
    const nativeEvent: any = e.nativeEvent;
    const layout = nativeEvent.layout;
    this.props.onUpdateHeight(layout.height);
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
        textValue={()=>this.props.searchQuery.location}
        onLocationSelected={(text)=> {
          this.props.updateLocation(text);
          this.props.performSearch(this.props.searchQuery);
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
