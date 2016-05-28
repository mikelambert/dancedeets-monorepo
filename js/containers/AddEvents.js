/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  RefreshControl,
  ListView,
  StyleSheet,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import type { AddEventData } from '../addEventsModels';
import { AddEventRow } from '../events/uicomponents';
import type { State } from '../reducers/addEvents';
import {
  addEvent,
  reloadAddEvents,
} from '../actions';

class FilterHeader extends React.Component {
  render() {
    return <View />;
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
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(props.addEvents.results),
    };
    return state;
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
    alignItems: 'center'
  },
  listView: {
    flex: 1,
  }
});
