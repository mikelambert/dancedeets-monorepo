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
  clickEvent,
  reloadAddEvents,
  setOnlyUnadded,
  setSortOrder,
} from '../actions';
import { purpleColors } from '../Colors';
import {
  Button,
  HorizontalView,
  ProgressSpinner,
  SegmentedControl,
  Text,
} from '../ui';

import moment from 'moment';
const {
  Globalize,
} = require('react-native-globalize');
const en = new Globalize('en');

class _FilterHeader extends React.Component {
  render() {
    return <View style={styles.header}>

    <Text style={styles.headerRow}>DanceDeets works when users add their events.{'\n'}Should we add any of your events below?</Text>

    <HorizontalView style={styles.headerRow}>
      <Text style={styles.headerText}>Show events:</Text>
      <SegmentedControl
        values={['All', 'Not-yet-added only']}
        style={{flex: 1}}
        defaultIndex={this.props.displayOptions.onlyUnadded ? 1 : 0}
        tintColor={purpleColors[0]}
        tryOnChange={(index)=>{this.props.setOnlyUnadded(index == 1);}}
      />
    </HorizontalView>

    <HorizontalView style={styles.headerRow}>
      <Text style={styles.headerText}>Sort:</Text>
      <SegmentedControl
        values={['By Start Date', 'By Name']}
        style={{flex: 1}}
        tintColor={purpleColors[0]}
        defaultIndex={this.props.displayOptions.sortOrder === 'ByName' ? 1 : 0}
        tryOnChange={(index)=>{this.props.setSortOrder(index == 1 ? 'ByName' : 'ByDate');}}
      />
    </HorizontalView>
    </View>;
  }
}
const FilterHeader = connect(
  state => ({
    displayOptions: state.addEvents.displayOptions,
  }),
  dispatch => ({
    setOnlyUnadded: (x) => dispatch(setOnlyUnadded(x)),
    setSortOrder: (x) => dispatch(setSortOrder(x)),
  }),
)(_FilterHeader);

class AddEventRow extends React.Component {
  props: {
    onEventClicked: (event: AddEventData) => void,
    onEventAdded: (event: AddEventData) => void,
    event: AddEventData,
  };

  render() {
    const width = 75;
    const pixelWidth = width * PixelRatio.get();
    const imageUrl = 'https://graph.facebook.com/' + this.props.event.id + '/picture?type=large&width=' + pixelWidth + '&height=' + pixelWidth;
    let tempOverlay = null;
    if (this.props.event.clickedConfirming) {
      tempOverlay = <View style={{position: 'absolute', top: 20, left: 0}}>
        <Button size="small" caption="Add Event" onPress={()=>{this.props.onEventAdded(this.props.event);}} />
      </View>;
    } else if (this.props.event.pending) {
      tempOverlay = <View style={{position: 'absolute', top: 20, left: 0}}>
        <ProgressSpinner/>
      </View>;
    }
    const addedBanner = (this.props.event.loaded ?
      <View style={styles.disabledOverlay}>
        <View style={[styles.redRibbon, {top: width / 2 - 10}]}>
          <Text style={styles.redRibbonText}>
          ADDED
          </Text>
        </View>
      </View> : null);
    const textColor = (this.props.event.loaded || tempOverlay) ? '#888' : 'white';

    const dateFormatter = en.getDateFormatter({skeleton: 'yMMMdhm'});
    const start = moment(this.props.event.start_time, moment.ISO_8601);
    const formattedStart = dateFormatter(start.toDate());


    const row = (
      <HorizontalView>
        <View style={styles.leftEventImage}>
          <View style={{width: width, overflow: 'hidden'}}>
            <Image
              source={{uri: imageUrl}}
              style={{width: width, height: width}}
            />
            {addedBanner}
          </View>
        </View>
        <View style={styles.rightTextDescription}>
          <Text style={{color: textColor}} numberOfLines={2}>{this.props.event.name}</Text>
          <Text style={{color: textColor}}>{formattedStart}</Text>
          {tempOverlay}
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
        <View style={styles.row}>
          <TouchableOpacity onPress={() => this.props.onEventClicked(this.props.event)} activeOpacity={0.5}>
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
    clickEvent: (eventId: string) => void;
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

  applyFilterSorts(props, results) {
    if (props.addEvents.displayOptions.onlyUnadded) {
      results = results.filter((x) => !x.loaded);
    }
    if (props.addEvents.displayOptions.sortOrder === 'ByName') {
      results = results.slice().sort((a, b) => a.name.localeCompare(b.name));
    } else if (props.addEvents.displayOptions.sortOrder === 'ByDate') {
      results = results.slice().sort((a, b) => a.start_time.localeCompare(b.start_time));
    }
    return results;
  }

  _getNewState(props) {
    const results = this.applyFilterSorts(props, props.addEvents.results || []);
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(results),
    };
    return state;
  }

  componentDidMount() {
    if (!this.props.addEvents.results) {
      this.props.reloadAddEvents();
    }
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this._getNewState(nextProps));
  }

  _renderRow(row: AddEventData) {
    return <AddEventRow
      event={row}
      onEventClicked={(event: AddEventData) => {this.props.clickEvent(event.id);}}
      onEventAdded={(event: AddEventData) => {this.props.addEvent(event.id);}}
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
    clickEvent: (eventId: string) => dispatch(clickEvent(eventId)),
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
  disabledOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#00000088',
  },
  redRibbon: {
    position: 'absolute',
    transform: [{rotate: '-30deg'}],
    backgroundColor: '#c00',
    borderColor: 'black',
    borderWidth: 0.5,
    left: -100,
    right: -100,

    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  redRibbonText: {
    fontSize: 18,
  },
  leftEventImage: {
    flex: 0.3,
  },
  rightTextDescription: {
    flex: 1,
    marginLeft: 5,
  },
  header: {
    backgroundColor: purpleColors[2],
  },
  headerRow: {
    alignItems: 'center',
    margin: 5,
  },
  headerText: {
    marginRight: 5,
  },
});
