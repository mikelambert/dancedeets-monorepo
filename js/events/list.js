/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

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

import { EventRow } from './uicomponents';
import { Event } from './models';
import SearchHeader from './searchHeader';
import type { SearchResults } from './search';
import moment from 'moment';
import {
  detectedLocation,
  performSearch,
  updateLocation,
  updateKeywords,
} from '../actions';
import { linkColor, purpleColors, yellowColors } from '../Colors';
import Geocoder from '../api/geocoder';
import { auth } from '../api/dancedeets';
import type { Address } from './formatAddress';
import { format } from './formatAddress';
import {
  Button,
  normalize,
  semiNormalize,
  Text,
} from '../ui';
import { track } from '../store/track';
import { AdMobBanner } from 'react-native-admob';
import WebsiteUrl from '../websiteUrl';
import LinearGradient from 'react-native-linear-gradient';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';

import { weekdayDate } from '../formats';

const messages = defineMessages({
  addEvent: {
    id: 'addEvent.addEvent',
    defaultMessage: 'Add Event',
    description: 'Button to open the Add Event screen',
  },
  specialLinks: {
    id: 'onebox.specialLinks',
    defaultMessage: 'Special Links',
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
    return <LinearGradient
        start={[0.0, 0.0]} end={[0.0, 1]}
        colors={[purpleColors[4], purpleColors[1], purpleColors[1], purpleColors[4]]}
        locations={[0.0, 0.4, 0.6, 1.0]}
        style={styles.sectionHeader}>
      <Text style={styles.sectionHeaderText}>{this.props.title}</Text>
    </LinearGradient>;
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
    />;
  }
}
const AddEventButton = injectIntl(_AddEventButton);

class _EventListContainer extends React.Component {
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
      this.refs.list_view.scrollTo({x: 0, y: 0, animated: false});
    }
  }

  async setLocationAndSearch(formattedAddress: string) {
    await this.props.detectedLocation(formattedAddress);
    await this.props.performSearch();
  }

  fetchLocationAndSearch() {
    const highAccuracy = Platform.OS == 'ios';
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const newCoords = { lat: position.coords.latitude, lng: position.coords.longitude };
        const address: Address = await Geocoder.geocodePosition(newCoords);
        const formattedAddress = format(address[0]);
        // Trigger this search without waiting around
        auth({location: formattedAddress});
        // And likewise with our attempt to search
        this.setLocationAndSearch(formattedAddress);
      },
      (error) => console.warn('Error getting current position:', error),
      {enableHighAccuracy: highAccuracy, timeout: 10 * 1000, maximumAge: 10 * 60 * 1000}
    );
  }

  async initialize() {
    const url = await Linking.getInitialURL();
    const processedUrl = new WebsiteUrl(url);
    if (processedUrl.isEventUrl()) {
      const eventId = processedUrl.eventId();
      const event = await fetch(eventId);
      this.props.onEventSelected(event);
    } if (processedUrl.isSearchUrl()) {
      this.props.updateLocation(processedUrl.location());
      this.props.updateKeywords(processedUrl.keywords());
      this.props.performSearch();
    } else {
      this.fetchLocationAndSearch();
      // TODO: Tie this search in with some attempt to pull in a saved search query
      // this.props.performSearch();
    }
  }

  componentDidMount() {
    this.initialize();
  }

  _renderRow(row) {
    if ('id' in row) {
      return <EventRow
        event={row}
        onEventSelected={this.props.onEventSelected}
      />;
    } else {
      return <Onebox onebox={row}/>;
    }
  }

  bannerError(e) {
    console.log('didFailToReceiveAdWithError', e);
  }

  _renderHeader() {
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
    if (this.props.search.error) {
      return <Text>Error</Text>;
    }
    return (
      <ListView
        ref="list_view"
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
          <SectionHeader title={sectionID}/>
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
const EventListContainer = injectIntl(_EventListContainer);

export default connect(
  (state) => ({
    search: state.search,
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
  })
)(injectIntl(EventListContainer));


const styles = StyleSheet.create({
  listView: {
    flex: 1,
    top: 0,
  },
  container: {
    backgroundColor: '#000',
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
    backgroundColor: purpleColors[1],
  },
  sectionHeaderText: {
    color: 'white',
    fontWeight: 'bold',
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
