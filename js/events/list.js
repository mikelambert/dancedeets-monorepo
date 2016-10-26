/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Linking,
  ListView,
  Platform,
  RefreshControl,
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';

import { connect } from 'react-redux';
import _ from 'lodash/string';
import { EventRow } from './uicomponents';
import SearchHeader from './searchHeader';
import type { SearchResults } from './search';
import moment from 'moment';
import {
  detectedLocation,
  performSearch,
  processUrl,
  updateLocation,
  updateKeywords,
} from '../actions';
import {
  linkColor,
  purpleColors,
} from '../Colors';
import {
  auth,
  event,
} from '../api/dancedeets';
import {
  Button,
  normalize,
  semiNormalize,
  Text,
} from '../ui';
import { track } from '../store/track';
import { AdMobBanner } from 'react-native-admob';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import {
  getAddress,
  getPosition,
} from '../util/geo';
import { weekdayDate } from '../formats';
import { loadUserData } from '../actions/login';
import { canHandleUrl } from '../websiteUrl';

const messages = defineMessages({
  fetchEventsError: {
    id: 'errors.fetchEventsError',
    defaultMessage: 'There was a problem fetching events.',
    description: 'Error message shown when there is an error loading data over the network',
  },
  networkRetry: {
    id: 'errors.networkRetry',
    defaultMessage: 'Check your network connection and try again.',
    description: 'Message shown when the user should attempt a reload',
  },
  addEvent: {
    id: 'addEvent.addEvent',
    defaultMessage: 'Add Event',
    description: 'Button to open the Add Event screen',
  },
  specialLinks: {
    id: 'onebox.specialLinks',
    defaultMessage: 'Additional Links',
    description: 'Header for all the links/blogs/wikis/etc relevant to this search',
  },
  eventsWithLocation: {
    id: 'search.eventsWithLocation',
    defaultMessage: 'Events near {location}',
    description: 'Header to show with search results',
  },
  eventsWithKeywords: {
    id: 'search.eventsWithKeywords',
    defaultMessage: 'Events near %1$s with keywords "{keywords}"',
    description: 'Header to show with search results',
  },
  eventsWithLocationKeywords: {
    id: 'search.eventsWithLocationKeywords',
    defaultMessage: 'Events near {location} with keywords "{keywords}"',
    description: 'Header to show with search results',
  },
});

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
    let url = this.props.onebox.url;
    // We want to track the pre-augmented URL
    track('Onebox', {URL: url});

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

class _AddEventButton extends React.Component {
  render() {
    return <Button
      caption={this.props.intl.formatMessage(messages.addEvent)}
      color="red"
      textStyle={{fontWeight: 'bold'}}
      style={styles.addEventButton}
      onPress={this.props.onPress}
      testID="addEvents"
    />;
  }
}
const AddEventButton = injectIntl(_AddEventButton);

class _EventListContainer extends React.Component {
  state: {
    position: ?Object,
    dataSource: ListView.DataSource,
  };

  list_view: ReactElement<ListView>;

  constructor(props) {
    super(props);
    var dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
      sectionHeaderHasChanged: (s1, s2) => s1 !== s2,
    });
    this.state = {
      position: null,
      dataSource,
    };
    this.state = this._getNewState(this.props);
    (this: any)._renderHeader = this._renderHeader.bind(this);
    (this: any)._renderRow = this._renderRow.bind(this);
    (this: any).setLocationAndSearch = this.setLocationAndSearch.bind(this);
  }

  _buildDataBlobAndHeaders(results: SearchResults) {
    const dataBlob = {};
    const sectionHeaders = [];

    if (results) {
      if (results.onebox_links != null && results.onebox_links.length > 0) {
        const oneboxKey = this.props.intl.formatMessage(messages.specialLinks);
        dataBlob[oneboxKey] = results.onebox_links.map((x) => x);
        sectionHeaders.push(oneboxKey);
      }
      if (results.results != null && results.results.length > 0) {
        for (var e of results.results) {
          const start = moment(e.start_time, moment.ISO_8601);
          const formattedStart = this.props.intl.formatDate(start.toDate(), weekdayDate);
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
    const { dataBlob, sectionHeaders } = this._buildDataBlobAndHeaders(props.search.results);
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRowsAndSections(dataBlob, sectionHeaders),
    };
    return state;
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this._getNewState(nextProps));
    if (nextProps.search.results !== this.props.search.results) {
      this.list_view.scrollTo({x: 0, y: 0, animated: false});
    }
  }

  async setLocationAndSearch(formattedAddress: string) {
    // Reload our current location, just in case we haven't loaded it before.
    // This could happen if we don't have a location at load time (no permissions)
    // But the user gives us permissions, we do a search, and now we need to reload it here,
    // ideally before the user's search results come back
    this.loadLocation();
    // Now do the actual search logic:
    await this.props.detectedLocation(formattedAddress);
    await this.props.performSearch();
  }

  async authAndReloadProfile(address) {
    if (!this.props.user) {
      return;
    }
    await auth({location: address});
    // After sending an auth to update the user's address,
    // we should reload our local user's data too.
    this.props.loadUserData();
  }

  async fetchLocationAndSearch() {
    const address = await getAddress();
    // Trigger this search without waiting around
    this.authAndReloadProfile(address);
    // And likewise with our attempt to search
    this.setLocationAndSearch(address);
  }

  async initialize() {
    const url: ?string = await Linking.getInitialURL();
    if (canHandleUrl(url)) {
      this.props.processUrl(url);
    } else {
      this.fetchLocationAndSearch();
      // TODO: Tie this search in with some attempt to pull in a saved search query
      // this.props.performSearch();
    }
  }

  async loadLocation() {
    try {
      const position = await getPosition();
      this.setState({position});
    } catch (e) {
      console.log('Error fetching user location for finding distance-to-event: ' + e);
    }
  }

  componentWillMount() {
    this.loadLocation();
  }

  componentDidMount() {
    this.initialize();
  }

  _renderRow(row) {
    if ('id' in row) {
      return <EventRow
        event={row}
        onEventSelected={this.props.onEventSelected}
        currentPosition={this.state.position}
      />;
    } else {
      return <Onebox onebox={row}/>;
    }
  }

  bannerError(e) {
    console.log('didFailToReceiveAdWithError', e);
  }

  _renderHeader() {
    if (this.props.search.error) {
      return this.renderErrorView();
    }
    return this.renderSummaryView();
  }

  renderErrorView() {
    return <View style={styles.errorView}>
      <Text style={styles.errorText}>
        {this.props.intl.formatMessage(messages.fetchEventsError)}{' '}
        {this.props.intl.formatMessage(messages.networkRetry)}
      </Text>
    </View>;
  }

  renderSummaryView() {
    let message = null;
    const query = this.props.search.results && this.props.search.results.query;
    if (!query) {
      return;
    }
    if (query.location && query.keywords) {
      message = messages.eventsWithLocationKeywords;
    } else if (query.location) {
      message = messages.eventsWithLocation;
    } else if (query.keywords) {
      message = messages.eventsWithKeywords;
    } else {
      // Don't show any header for non-existent search queries/results
      return null;
    }
    const header = this.props.intl.formatMessage(message, {location: query.location, keywords: query.keywords});
    return <Text style={styles.listHeader}>{header}</Text>;
  }

  renderAd() {
    // This is dead code. Hide our ads for now, until/unless we decide we have data we really care about.
    let adUnitID = null;
    if (__DEV__) {
      adUnitID = 'ca-app-pub-3940256099942544/6300978111';
    } else if (Platform.OS === 'ios') {
      adUnitID = 'ca-app-pub-9162736050652644/3634975775';
    } else if (Platform.OS === 'android') {
      adUnitID = 'ca-app-pub-9162736050652644/9681509378';
    } else {
      return null;
    }
    return <AdMobBanner
      bannerSize={"smartBannerPortrait"}
      adUnitID={adUnitID}
      didFailToReceiveAdWithError={this.bannerError}
    />;
  }

  renderListView() {
    return (
      <ListView
        ref={(x) => {this.list_view = x;}}
        style={[styles.listView]}
        dataSource={this.state.dataSource}
        renderHeader={this._renderHeader}
        refreshControl={
          <RefreshControl
            refreshing={this.props.search.loading}
            onRefresh={() => this.props.performSearch()}
          />
        }
        renderRow={this._renderRow}
        renderSectionHeader={(data, sectionID) =>
          <SectionHeader title={_.upperFirst(sectionID)}/>
        }
        initialListSize={5}
        pageSize={1}
        scrollRenderAheadDistance={5000}
        scrollsToTop={false}
        indicatorStyle="white"
      />
    );
  }

  render() {
    return (
      <View style={styles.container}>
        <SearchHeader onAddEvent={() => {
          this.props.onAddEventClicked('Search Header');
        }} >
          {this.renderListView()}
        </SearchHeader>
        <AddEventButton onPress={() => {
          this.props.onAddEventClicked('Floating Button');
        }} />
      </View>
    );
  }
}
export default connect(
  (state) => ({
    search: state.search,
    user: state.user.userData,
  }),
  (dispatch) => ({
    detectedLocation: async (location) => {
      await dispatch(detectedLocation(location));
    },
    performSearch: async () => {
      await dispatch(performSearch());
    },
    updateLocation: async (location) => {
      await dispatch(updateLocation(location));
    },
    updateKeywords: async (keywords) => {
      await dispatch(updateKeywords(keywords));
    },
    processUrl: async (url) => {
      await dispatch(processUrl(url));
    },
    loadUserData: async () => {
      await loadUserData(dispatch);
    },
  })
)(injectIntl(_EventListContainer));


const styles = StyleSheet.create({
  listView: {
    flex: 1,
    top: 0,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
  },
  loading: {
    color: 'white',
    textAlign: 'center',
    marginBottom: 50,
  },
  sectionHeader: {
    height: semiNormalize(30),
    alignItems: 'flex-start', // left align
    justifyContent: 'center', // vertically center
    backgroundColor: purpleColors[2],
  },
  sectionHeaderText: {
    color: 'white',
    fontWeight: 'bold',
  },
  errorView: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    top: 200,
  },
  errorText: {
    fontSize: semiNormalize(20),
    lineHeight: semiNormalize(24),
    textAlign: 'center',
    marginHorizontal: 30,
  },
  onebox: {
    alignItems: 'flex-start', // left align
    justifyContent: 'center', // vertically center
    height: semiNormalize(50),
  },
  oneboxText: {
    color: linkColor,
    marginLeft: 10,
    fontSize: semiNormalize(18),
  },
  addEventButton: {
    position: 'absolute',
    right: normalize(10),
    bottom: normalize(20),
  },
  listHeader: {
    fontWeight: 'bold',
    fontSize: semiNormalize(18),
    lineHeight: semiNormalize(24),
  },
});
