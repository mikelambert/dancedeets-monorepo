/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Image,
  RefreshControl,
  ListView,
  PixelRatio,
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import type { AddEventData } from '../addEventsModels';
import type { State } from '../reducers/addEvents';
import {
  addEvent,
  reloadAddEvents,
} from '../actions';
import {
  HorizontalView,
  ProgressSpinner,
  Text,
} from '../ui';

class FilterHeader extends React.Component {
  render() {
    return <View />;
  }
}


class AddEventRow extends React.Component {
  props: {
    onEventSelected: (event: AddEventData) => void,
    event: AddEventData,
  };

  render() {
    //TODO: use event.loaded and event.pending to grey things out and disable touching
    const width = 75;
    const pixelWidth = width * PixelRatio.get();
    const imageUrl = 'https://graph.facebook.com/' + this.props.event.id + '/picture?type=large&width=' + pixelWidth + '&height=' + pixelWidth;
    const spinner = (this.props.event.pending ?
      <View style={{position: 'absolute', top: 20, left: 0}}>
        <ProgressSpinner/>
      </View>
    : null);
    const row = (
      <HorizontalView>
        <Image
          source={{uri: imageUrl}}
          style={{width: width, height: width}}
        />
        <View style={{flex: 1, marginLeft: 5}}>
          <Text
            numberOfLines={2}
            >{this.props.event.name}</Text>
          <Text>{this.props.event.start_time}</Text>
          <Text>loaded: {this.props.event.loaded ? 'Yes' : 'No'}</Text>
          {spinner}
        </View>
      </HorizontalView>
    );
    if (this.props.event.loaded || this.props.event.pending) {
      return (
        <View style={styles.row}>
          {row}
        </View>
      );
    } else {
      return (
        <View style={[styles.row, {backgroundColor: '#333'}]}>
          <TouchableOpacity onPress={() => this.props.onEventSelected(this.props.event)} activeOpacity={0.5}>
            {row}
          </TouchableOpacity>
        </View>
      );
    }
  }
}

class _AddEventList extends React.Component {
  props: {
    addEvent: (eventId: string) => void;
    addEvents: State;
    reloadAddEvents: () => void;
  };
  state: {
    dataSource: ListView.DataSource,
  };

  constructor(props) {
    super(props);
    var dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
      sectionHeaderHasChanged: (s1, s2) => s1 !== s2,
    });
    this.state = {
      dataSource,
    };
    this.state = this._getNewState(this.props);
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  _getNewState(props) {
    console.log(props);
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(props.addEvents.results || []),
    };
    console.log(state);
    return state;
  }

  componentDidMount() {
    //this.props.reloadAddEvents();
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this._getNewState(nextProps));
  }

  _renderRow(row: AddEventData) {
    return <AddEventRow
      event={row}
      onEventSelected={(event: AddEventData) => {this.props.addEvent(event.id);}}
    />;
  }

  render() {
    return <ListView
      style={[styles.listView]}
      dataSource={this.state.dataSource}
      refreshControl={
        <RefreshControl
          refreshing={this.props.addEvents.loading}
          onRefresh={() => this.props.reloadAddEvents()}
        />
      }
      renderRow={this._renderRow}
      initialListSize={10}
      pageSize={5}
      scrollRenderAheadDistance={10000}
      scrollsToTop={false}
      indicatorStyle="white"
     />;
  }
}
const AddEventList = connect(
  state => ({
    addEvents: state.addEvents,
  }),
  dispatch => ({
    addEvent: (eventId: string) => dispatch(addEvent(eventId)),
    reloadAddEvents: () => dispatch(reloadAddEvents()),
  }),
)(_AddEventList);

export default class AddEvents extends React.Component {
  render() {
    return <View style={styles.container}>
    <FilterHeader />
    <AddEventList />
    </View>;
  }
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  listView: {
    flex: 1,
  },
  row: {
    flex: 1,
    marginLeft: 5,
    marginRight: 5,
    marginBottom: 20,
    // http://stackoverflow.com/questions/36605906/what-is-the-row-container-for-a-listview-component
    overflow: 'hidden',
  },
});
