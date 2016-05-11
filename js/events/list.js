/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  Linking,
  ListView,
  Platform,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import { connect } from 'react-redux';

import { EventRow } from './uicomponents';
import { Event } from './models';
import SearchHeader from './searchHeader';
import type { SearchResults } from './search';
import moment from 'moment';
import {
  performSearch,
} from '../actions';
import { linkColor } from '../Colors';
import Geocoder from 'react-native-geocoder';
const {
  Globalize,
} = require('react-native-globalize');
import { auth } from '../api';
import type { Address } from './formatAddress';
import { format } from './formatAddress';

var en = new Globalize('en');


class SectionHeader extends React.Component {
  props: {
    title: string,
  };

  render() {
    return <View style={styles.sectionHeader}>
      <Text style={styles.sectionHeaderText}>{this.props.title}</Text>
    </View>;
  }
}

class Onebox extends React.Component {
  constructor(props) {
    super(props);
    (this: any).oneboxClicked = this.oneboxClicked.bind(this);
  }

  oneboxClicked() {
    var url = this.props.onebox.url;
    // TOOD: Set up and use a webview to keep things "in-app" ?
    if (url.indexOf('?') > -1) {
      url += '&webview=1';
    } else {
      url += '?webview=1';
    }
    Linking.openURL(url).catch(err => console.error('Error opening onebox url:', url, 'with Error:', err));
  }

  render() {
    return (
      <TouchableOpacity
        style={styles.onebox}
        onPress={this.oneboxClicked}
        activeOpacity={0.5}
      >
        <Text style={styles.oneboxText}>{this.props.onebox.title}</Text>
      </TouchableOpacity>
    );
  }
}

class EventListContainer extends React.Component {
  state: {
    dataSource: ListView.DataSource,
    headerHeight: number,
  };

  constructor(props) {
    super(props);
    var dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
      sectionHeaderHasChanged: (s1, s2) => s1 !== s2,
    });
    this.state = {
      headerHeight: 0,
      dataSource,
    };
    this.state = this._getNewState(this.props);
    (this: any).onUpdateHeaderHeight = this.onUpdateHeaderHeight.bind(this);
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  _buidDataBlobAndHeaders(results: SearchResults) {
    const dateFormatter = en.getDateFormatter({skeleton: 'yMMMd'});
    var dataBlob = {};
    var sectionHeaders = [];

    if (results) {
      if (results.onebox_links) {
        const oneboxKey = 'Special Links';
        dataBlob[oneboxKey] = results.onebox_links.map((x) => x);
        sectionHeaders.push(oneboxKey);
      }
      if (results.results) {
        for (var e of results.results) {
          var start = moment(e.start_time, moment.ISO_8601);
          var formattedStart = dateFormatter(start.toDate());
          if (!(formattedStart in dataBlob)) {
            dataBlob[formattedStart] = [];
          }
          dataBlob[formattedStart].push(e);
          if (!sectionHeaders || sectionHeaders[sectionHeaders.length - 1] !== formattedStart) {
            sectionHeaders.push(formattedStart);
          }
        }
      }
    }
    return {
      dataBlob,
      sectionHeaders
    };
  }

  _getNewState(props) {
    const { dataBlob, sectionHeaders } = this._buidDataBlobAndHeaders(props.search.results);
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRowsAndSections(dataBlob, sectionHeaders),
    };
    return state;
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this._getNewState(nextProps));
  }

  componentDidMount() {
    const highAccuracy = Platform.OS == 'ios';
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const address: Address = await Geocoder.reverseGeocodeLocation(position.coords);
        auth(null, {location: format(address[0])});
        // TODO: Set up location in search query
        //this.setState({initialPosition});
      },
      (error) => console.error('Error getting current position:', error.message),
      {enableHighAccuracy: highAccuracy, timeout: 5 * 1000, maximumAge: 60 * 1000}
    );
    this.props.performSearch(this.props.search.searchQuery);
  }

  onUpdateHeaderHeight(headerHeight: number) {
    this.setState({
      ...this.state,
      headerHeight,
    });
  }

  render() {
    return (
      <View style={styles.container}>
        {this.props.search.loading ? this.renderLoadingView() : this.renderListView()}
        <SearchHeader onUpdateHeight={this.onUpdateHeaderHeight}/>
      </View>
    );
  }

  _renderRow(row) {
    if ('id' in row) {
      return <EventRow
        event={new Event(row)}
        onEventSelected={this.props.onEventSelected}
      />;
    } else {
      return <Onebox onebox={row}/>;
    }
  }

  renderListView() {
    return (
      <ListView
        style={{marginTop: this.state.headerHeight}}
        dataSource={this.state.dataSource}
        renderRow={this._renderRow}
        renderSectionHeader={(data, sectionID) =>
          <SectionHeader title={sectionID}/>
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
  },
  sectionHeader: {
    height: 30,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#222',
  },
  sectionHeaderText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 15,
  },
  onebox: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 50,
  },
  oneboxText: {
    color: linkColor,
    marginLeft: 10,
    fontSize: 18,
  },
});
