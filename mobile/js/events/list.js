/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Dimensions,
  Image,
  Linking,
  ListView,
  Platform,
  RefreshControl,
  StyleSheet,
  TouchableOpacity,
  TouchableHighlight,
  View,
} from 'react-native';
import { AdMobBanner } from 'react-native-admob';
import {
  injectIntl,
  intlShape,
  defineMessages,
} from 'react-intl';
import moment from 'moment';
import { connect } from 'react-redux';
import Carousel from 'react-native-carousel';
import Icon from 'react-native-vector-icons/Ionicons';
import upperFirst from 'lodash/upperFirst';
import { Event } from 'dancedeets-common/js/events/models';
import type {
  FeaturedInfo,
  Onebox,
  PeopleListing,
  SearchResponse,
} from 'dancedeets-common/js/events/search';
import Collapsible from 'react-native-collapsible';
import { EventRow } from './uicomponents';
import SearchHeader from './searchHeader';
import type {
  State,
} from '../reducers/search';
import {
  detectedLocation,
  performSearch,
  processUrl,
} from '../actions';
import type { User } from '../actions/types';
import {
  linkColor,
  purpleColors,
} from '../Colors';
import {
  auth,
  event,
  isAuthenticated,
} from '../api/dancedeets';
import {
  BottomFade,
  Button,
  CenterFade,
  HorizontalView,
  normalize,
  ProportionalImage,
  semiNormalize,
  Text,
} from '../ui';
import { track } from '../store/track';
import {
  getAddress,
  getPosition,
} from '../util/geo';
import { weekdayDate } from '../formats';
import { loadUserData } from '../actions/login';
import { canHandleUrl } from '../websiteUrl';
import {
  loadSavedAddress,
  storeSavedAddress,
} from './savedAddress';
import { openUserId } from '../util/fb';

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
    defaultMessage: 'Events with keywords "{keywords}"',
    description: 'Header to show with search results',
  },
  eventsWithLocationKeywords: {
    id: 'search.eventsWithLocationKeywords',
    defaultMessage: 'Events near {location} with keywords "{keywords}"',
    description: 'Header to show with search results',
  },
});

const CarouselDotIndicatorSize = 25;

class SectionHeader extends React.Component {
  props: {
    title: string,
  };

  render() {
    return (<View style={styles.sectionHeader}>
      <Text style={styles.sectionHeaderText}>{this.props.title}</Text>
    </View>);
  }
}

class FeaturedEvent extends React.Component {
  props: {
    event: Event;
  }

  render() {
    const imageProps = this.props.event.getResponsiveFlyers();
    if (!imageProps) {
      return null;
    }
    return <Image
      source={imageProps}
      style={{
        height: 200,
      }}
    />;
  }
}

class FeaturedEvents extends React.Component {
  props: {
    featured: Array<FeaturedInfo>;
    onEventSelected: (event: Event) => void;
  }

  renderPage(index: number) {
    const featuredInfo = this.props.featured[index];

    // No fade for single items
    let fadeOverlay = null;
    // But if there's multiple items, let's do a bottom-fade
    if (this.props.featured.length > 1) {
      fadeOverlay = <View style={{
          position: 'absolute',
          left: 0,
          bottom: 0,
          right: 0,
        }}>
          <BottomFade />
        </View>;
    }
    // And if there's a title, do an even larger fade that lets us stick the text in there
    if (featuredInfo.showTitle) {
      fadeOverlay = <View style={{
        position: 'absolute',
        left: 0,
        bottom: 0,
        right: 0,
      }}>
        <BottomFade height={150} />
        <Text
          numberOfLines={1}
          style={{
            position: 'absolute',
            bottom: CarouselDotIndicatorSize,
            textAlign: 'center',
            left: 0,
            right: 0,
            fontWeight: 'bold',
          }}
        >{featuredInfo.event.name}</Text>
      </View>;
    }
    return <View key={index} style={{
      width: Dimensions.get('window').width,
    }}>
      <TouchableOpacity onPress={() => this.props.onEventSelected(featuredInfo.event)} activeOpacity={0.5}>
        <FeaturedEvent event={featuredInfo.event} />
        {fadeOverlay}
      </TouchableOpacity>
    </View>;
  }

  shouldComponentUpdate(nextProps, nextState) {
    return this.props.featured != nextProps.featured;
  }

  render() {
    if (!this.props.featured || !this.props.featured.length) {
      return null;
    }
    let carousel = null;
    if (this.props.featured.length == 1) {
      carousel = this.renderPage(0);
    } else {
      carousel = <Carousel
        indicatorOffset={0}
        indicatorColor="#FFFFFF"
        indicatorSize={CarouselDotIndicatorSize}
        indicatorSpace={15}
        animate={true}
        loop={true}
        delay={4000}
      >
        {this.props.featured.map((event, i) => this.renderPage(i))}
      </Carousel>;
    }
    return (<View style={{ height: 200 }}>
      {carousel}
    </View>);
  }
}

class OneboxView extends React.Component {
  props: {
    onebox: Onebox;
  }

  constructor(props) {
    super(props);
    (this: any).oneboxClicked = this.oneboxClicked.bind(this);
  }

  oneboxClicked() {
    let url = this.props.onebox.url;
    // We want to track the pre-augmented URL
    track('Onebox', { URL: url });

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
  props: {
    intl: intlShape;
    onPress: () => void;
  }

  render() {
    return (<Button
      icon={require('./images/add_calendar.png')}
      caption={this.props.intl.formatMessage(messages.addEvent)}
      color="green"
      textStyle={{ fontWeight: 'bold' }}
      style={styles.addEventButton}
      onPress={this.props.onPress}
      testID="addEvents"
    />);
  }
}
const AddEventButton = injectIntl(_AddEventButton);

class PersonList extends React.Component {
  props: {
    title: String;
    subtitle: String;
    categoryOrder: Array<String>;
    people: StylePersonLookup;
  }

  state: {
    category: string;
  }

  constructor(props) {
    super(props);
    this.state = {
      category: '',
    };
  }


  renderLink(user) {
    return (<HorizontalView key={user.id}>
      <Text> – </Text>
      <TouchableOpacity
        key={user.id}
        onPress={() => openUserId(user.id)}
      ><Text style={[styles.rowLink]}>{user.name}</Text></TouchableOpacity>
    </HorizontalView>);
  }

  render() {
    const peopleList = this.props.people[this.state.category].slice(0, 10);
    //const categories = this.props.categoryOrder.filter(x => x === '' || this.props.people[x]);
    //{categories.map(x => <option key={x} value={x}>{x || 'Overall'}</option>)}

    return (<View>
      <Text style={{ fontStyle: 'italic' }}>{this.props.subtitle}:</Text>
      {peopleList.map(x => this.renderLink(x))}
    </View>);
  }
}

class HeaderCollapsible extends React.Component {
  props: {
    defaultCollapsed: Boolean;
    title: String;
    children: React.Element<*>;
  }

  state: {
    collapsed: boolean;
  }

  constructor(props) {
    super(props);
    this.state = { collapsed: !!props.defaultCollapsed };
    (this: any)._toggle = this._toggle.bind(this);
  }

  _toggle() {
    this.setState({ collapsed: !this.state.collapsed });
  }

  render() {
    const iconName = this.state.collapsed ? 'md-arrow-dropright' : 'md-arrow-dropdown';
    return <View>
      <TouchableHighlight onPress={this._toggle} underlayColor={this.props.underlayColor}>
        <View style={styles.sectionHeader}>
          <HorizontalView>
            <View style={{ width: 20, height: 20, alignItems: 'center', alignSelf: 'center' }}>
              <Icon name={iconName} size={15} color="#FFF" />
            </View>
            <Text>{this.props.title}</Text>
          </HorizontalView>
        </View>
      </TouchableHighlight>
      <Collapsible collapsed={this.state.collapsed}>
        {this.props.children}
      </Collapsible>
    </View>
  }
}

class _PeopleView extends React.Component {
  props: {
    people: PeopleListing;
  }

  render() {
    // Keep in sync with web?
    const defaultCollapsed = !(this.props.search.response.results.length < 10);
    return <View>
      <HeaderCollapsible
        title="Nearby Promoters"
        defaultCollapsed={defaultCollapsed}
        >
        <PersonList
          title="Promoters"
          subtitle="If you want to organize an event, work with these folks"
          people={this.props.people.ADMIN}
          />
      </HeaderCollapsible>
      <HeaderCollapsible
        title="Nearby Dancers"
        defaultCollapsed={defaultCollapsed}
        >
        <PersonList
          title="Dancers"
          subtitle="If you want to connect with the dance scene, hit these folks up"
          people={this.props.people.ATTENDEE}
          defaultCollapsed={defaultCollapsed}
          />
      </HeaderCollapsible>
    </View>;
  }
}
const PeopleView = connect(
  state => ({
    search: state.search,
  }),
)(_PeopleView);

class _EventListContainer extends React.Component {
  props: {
    intl: intlShape;
    onEventSelected: (event: Event) => void;
    onFeaturedEventSelected: (event: Event) => void;
    onAddEventClicked: (clickTarget: string) => void;

    // Self-managed props
    search: State,
    user: ?User,
    detectedLocation: (location: string) => Promise<void>;
    performSearch: () => Promise<void>;
    processUrl: (url: string) => Promise<void>;
    loadUserData: () => Promise<void>;
  }

  state: {
    position: ?Object,
    dataSource: ListView.DataSource,
  };

  _listView: ListView;

  constructor(props) {
    super(props);
    const dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
      sectionHeaderHasChanged: (s1, s2) => s1 !== s2,
    });
    this.state = {
      position: null,
      dataSource,
    };
    this.state = this.getNewState(this.props);
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).setLocationAndSearch = this.setLocationAndSearch.bind(this);
  }

  componentWillMount() {
    this.loadLocation();
  }

  componentDidMount() {
    this.initialize();
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this.getNewState(nextProps));
    if (nextProps.search.response !== this.props.search.response) {
      this._listView.scrollTo({ x: 0, y: 0, animated: false });
    }
  }

  getNewState(props) {
    const { dataBlob, sectionHeaders } = this.buildDataBlobAndHeaders(props.search.response);
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRowsAndSections(dataBlob, sectionHeaders),
    };
    return state;
  }

  async setLocationAndSearch(formattedAddress: string) {
    if (!formattedAddress) {
      return;
    }

    // Reload our current location for "N miles away" info, in case we haven't loaded it yet.
    // This could happen if we don't have a location at load time (no permissions),
    // then the user gives us permissions for a search, and now we need to reload it here,
    // ideally before the user's search results come back.
    this.loadLocation();

    // Now do the actual search logic:
    await this.props.detectedLocation(formattedAddress);
    await this.props.performSearch();

    // If the user doesn't have a location, let's save one based on their search
    // Hopefully we'll have loaded the user data by now, after the search has completed...
    // But this isn't critical functionality, but just a best-effort attempt to save a location
    if (this.props.user && this.props.user.ddUser && !this.props.user.ddUser.location) {
      await storeSavedAddress(formattedAddress);
    }
  }

  buildDataBlobAndHeaders(response: ?SearchResponse) {
    const dataBlob = {};
    const sectionHeaders = [];

    if (response) {
      if (response.onebox_links != null && response.onebox_links.length > 0) {
        const oneboxKey = this.props.intl.formatMessage(messages.specialLinks);
        dataBlob[oneboxKey] = response.onebox_links.map(x => x);
        sectionHeaders.push(oneboxKey);
      }
      const now = moment();
      if (response.results != null && response.results.length > 0) {
        for (const e of response.results) {
          // TODO: Due to some ancient bad design decisions,
          // it's surprisingly difficult to to do
          // time-zone-aware date manipulation on the server,
          // so instead let's filter out those events here.
          let end = moment(e.end_time, moment.ISO_8601);
          // If it's an endtime-less event, compute a fallback endtime here.
          if (!end.isValid()) {
            end = moment(e.start_time, moment.ISO_8601).add(2, 'hours');
          }
          if (end.isBefore(now)) {
            continue;
          }
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
      sectionHeaders,
    };
  }

  async authAndReloadProfile(address) {
    if (!isAuthenticated()) {
      return;
    }
    if (!address) {
      return;
    }
    await auth({ location: address });
    // After sending an auth to update the user's address,
    // we should reload our local user's data too.
    this.props.loadUserData();
  }

  async fetchLocationAndSearch() {
    // Get the address from GPS
    let address = await getAddress();
    // Save this location in the user's profile
    this.authAndReloadProfile(address);

    // Otherwise, fall back to the last-searched address
    if (!address) {
      address = await loadSavedAddress();
      console.log('Failed to load GPS, falling back to last-searched address: ', address);
    }

    // And if we have a location from either place, do a search
    this.setLocationAndSearch(address);
  }

  async initialize() {
    const url: ?string = await Linking.getInitialURL();
    if (url != null && canHandleUrl(url)) {
      this.props.processUrl(url);
    } else {
      this.fetchLocationAndSearch();
    }
  }

  async loadLocation() {
    try {
      const position = await getPosition();
      this.setState({ position });
    } catch (e) {
      console.log('Error fetching user location for finding distance-to-event:', e);
    }
  }

  bannerError(e) {
    console.log('didFailToReceiveAdWithError', e);
  }

  renderHeader() {
    if (this.props.search.error) {
      return this.renderErrorView();
    }
    return this.renderSummaryView();
  }

  renderRow(row) {
    if ('id' in row) {
      return (<EventRow
        event={row}
        onEventSelected={this.props.onEventSelected}
        currentPosition={this.state.position}
      />);
    } else {
      return <OneboxView onebox={row} />;
    }
  }

  renderErrorView() {
    return (<View style={styles.errorView}>
      <Text style={styles.errorText}>
        {this.props.intl.formatMessage(messages.fetchEventsError)}{' '}
        {this.props.intl.formatMessage(messages.networkRetry)}
      </Text>
    </View>);
  }

  renderSummaryView() {
    const response = this.props.search.response;
    if (!response) {
      return null;
    }
    const query = response.query;
    let header = null;
    if (query) {
      let message = null;
      if (query.location && query.keywords) {
        message = messages.eventsWithLocationKeywords;
      } else if (query.location) {
        message = messages.eventsWithLocation;
      } else if (query.keywords) {
        message = messages.eventsWithKeywords;
      } else {
        // Don't show any header for non-existent search queries/results
      }
      if (message) {
        header = <Text style={styles.listHeader}>
          {this.props.intl.formatMessage(message, { location: query.location, keywords: query.keywords })}
        </Text>;
      }
    }
    return <View>
      <FeaturedEvents
        featured={response.featuredInfos}
        onEventSelected={this.props.onFeaturedEventSelected}
        />
      <PeopleView people={response.people} />
      {header}
    </View>;
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
    return (<AdMobBanner
      bannerSize={'smartBannerPortrait'}
      adUnitID={adUnitID}
      didFailToReceiveAdWithError={this.bannerError}
    />);
  }

  renderListView() {
    return (
      <ListView
        // TODO: removeClippedSubviews is disabled until
        // https://github.com/facebook/react-native/issues/8088 is fixed.
        removeClippedSubviews={false}
        ref={(x) => { this._listView = x; }}
        style={[styles.listView]}
        dataSource={this.state.dataSource}
        renderHeader={this.renderHeader}
        refreshControl={
          <RefreshControl
            refreshing={this.props.search.loading}
            onRefresh={() => this.props.performSearch()}
          />
        }
        renderRow={this.renderRow}
        renderSectionHeader={(data, sectionID) =>
          <SectionHeader title={upperFirst(sectionID)} />
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
        <SearchHeader
          onAddEvent={() => {
            this.props.onAddEventClicked('Search Header');
          }}
        >
          {this.renderListView()}
        </SearchHeader>
        <AddEventButton
          onPress={() => {
            this.props.onAddEventClicked('Floating Button');
          }}
        />
      </View>
    );
  }
}
export default connect(
  state => ({
    search: state.search,
    user: state.user.userData,
  }),
  dispatch => ({
    detectedLocation: async (location) => {
      await dispatch(detectedLocation(location));
    },
    performSearch: async () => {
      await dispatch(performSearch());
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
  rowLink: {
    color: linkColor,
  },
  loading: {
    color: 'white',
    textAlign: 'center',
    marginBottom: 50,
  },
  sectionHeader: {
    borderTopWidth: 1,
    borderTopColor: purpleColors[1],
    height: semiNormalize(30),
    alignItems: 'flex-start', // left align
    justifyContent: 'center', // vertically center
    backgroundColor: purpleColors[2],
  },
  sectionHeaderText: {
    color: 'white',
    alignSelf: 'center',
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
