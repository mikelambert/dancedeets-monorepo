/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  ListView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { connect } from 'react-redux';

import { EventRow } from './uicomponents';
import { Event } from './models';
import SearchHeader from './searchHeader';

import {
  performSearch,
} from '../actions';

class EventListContainer extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };

  constructor(props) {
    super(props);
    var dataSource = new ListView.DataSource({rowHasChanged: (row1, row2) => row1 !== row2});
    this.state = {
      dataSource,
    };
    this.state = this._getNewState(this.props);
  }

  _getNewState(props) {
    const results = props.search.results;
    const state = {
      dataSource: this.state.dataSource.cloneWithRows(results ? results.results : []),
    };
    return state;
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this._getNewState(nextProps));
  }

  componentDidMount() {
    this.props.performSearch(this.props.search.searchQuery);
  }

  render() {
    return (
      <View style={styles.container}>
        {this.props.search.loading ? this.renderLoadingView() : this.renderListView()}
        <SearchHeader />
      </View>
    );
  }

  renderListView() {
    const onEventSelected = this.props.onEventSelected;
    return (
      <ListView
        dataSource={this.state.dataSource}
        renderRow={(e) =>
          <EventRow
            event={new Event(e)}
            onEventSelected={onEventSelected}
          />
        }
        initialListSize={10}
        pageSize={5}
        scrollRenderAheadDistance={10000}
        scrollsToTop={false}
      />
    );
  }

  renderLoadingView() {
    return (
      <Text style={styles.loading}>
        Loading events...
      </Text>
    );
  }
}
const mapStateToProps = (state) => {
  return {
    search: state.search,
  };
};
const mapDispatchToProps = (dispatch) => {
  return {
    performSearch: (searchQuery) => {
      dispatch(performSearch(searchQuery));
    },
  };
};
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(EventListContainer);


const styles = StyleSheet.create({
  container: {
    backgroundColor: '#000',
    flex: 1,
    justifyContent: 'center',
  },
  loading: {
    color: 'white',
    textAlign: 'center',
  }
});
