/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  StatusBar,
  StyleSheet,
  TextInput,
} from 'react-native';

import { BlurView } from 'react-native-blur';
import { connect } from 'react-redux';
import { defaultFont } from '../ui';

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
      style={[style, styles.searchField, defaultFont]}
      placeholderTextColor="rgba(255, 255, 255, 0.5)"
      backgroundColor="rgba(255, 255, 255, 0.2)"
      keyboardAppearance="dark"
      selectTextOnFocus={true}
      autoCorrect={false}
      autoCapitalize="none"
    />;
  }

  focus() {
    this.refs.textInput.focus();
  }
}

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
    return <BlurView
      onLayout={this.onLayout}
      style={[{paddingTop: StatusBar.currentHeight}, styles.floatTop, styles.statusBar]}
      blurType="dark"
    >
      <SearchInput
        ref="location"
        placeholder="Location"
        returnKeyType="search"
        onChangeText={(text) => this.props.updateLocation(text)}
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
    </BlurView>;
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
    backgroundColor: 'rgba(255, 255, 255, 0.5)',
  },
});
