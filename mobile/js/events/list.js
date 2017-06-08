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
  SectionList,
  Platform,
  RefreshControl,
  StyleSheet,
  TouchableOpacity,
  TouchableHighlight,
  View,
} from 'react-native';
import { AdMobBanner } from 'react-native-admob';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import moment from 'moment';
import { connect } from 'react-redux';
import Carousel from 'react-native-carousel';
import upperFirst from 'lodash/upperFirst';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { Event } from 'dancedeets-common/js/events/models';
import type {
  FeaturedInfo,
  Onebox,
  SearchResponse,
  StylePersonLookup,
} from 'dancedeets-common/js/events/search';
import { formatStartDateOnly } from 'dancedeets-common/js/dates';
import { EventRow, RowHeight } from './listEvent';
import SearchHeader from './searchHeader';
import type { State } from '../reducers/search';
import {
  canGetValidLoginFor,
  detectedLocation,
  performSearch,
  processUrl,
} from '../actions';
import type { User } from '../actions/types';
import { linkColor, purpleColors } from '../Colors';
import { auth, isAuthenticated } from '../api/dancedeets';
import {
  BottomFade,
  Button,
  HorizontalView,
  normalize,
  ProportionalImage,
  semiNormalize,
  Text,
} from '../ui';
import { track, trackWithEvent } from '../store/track';
import { getAddress, getPosition } from '../util/geo';
import { loadUserData } from '../actions/login';
import { canHandleUrl } from '../websiteUrl';
import { loadSavedAddress, storeSavedAddress } from './savedAddress';
import PeopleView from './peopleList';

const messages = defineMessages({
  fetchEventsError: {
    id: 'errors.fetchEventsError',
    defaultMessage: 'There was a problem fetching events.',
    description:
      'Error message shown when there is an error loading data over the network',
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
    description:
      'Header for all the links/blogs/wikis/etc relevant to this search',
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

const SectionHeight = semiNormalize(30);

class SectionHeader extends React.Component {
  props: {
    title: string,
  };

  render() {
    return (
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionHeaderText}>{this.props.title}</Text>
      </View>
    );
  }
}

class FeaturedEvent extends React.Component {
  props: {
    event: Event,
  };

  render() {
    const imageProps = this.props.event.getResponsiveFlyers();
    if (!imageProps) {
      return null;
    }
    return (
      <Image
        source={imageProps}
        style={{
          height: 200,
        }}
      />
    );
  }
}

class FeaturedEvents extends React.Component {
  props: {
    featured: Array<FeaturedInfo>,
    onEventSelected: (event: Event) => void,
  };

  shouldComponentUpdate(nextProps, nextState) {
    return this.props.featured !== nextProps.featured;
  }

  renderPage(index: number) {
    const featuredInfo = this.props.featured[index];

    // No fade for single items
    let fadeOverlay = null;
    // But if there's multiple items, let's do a bottom-fade
    if (this.props.featured.length > 1) {
      fadeOverlay = (
        <View
          style={{
            position: 'absolute',
            left: 0,
            bottom: 0,
            right: 0,
          }}
        >
          <BottomFade />
        </View>
      );
    }
    // And if there's a title, do an even larger fade that lets us stick the text in there
    if (featuredInfo.showTitle) {
      fadeOverlay = (
        <View
          style={{
            position: 'absolute',
            left: 0,
            bottom: 0,
            right: 0,
          }}
        >
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
          >
            {featuredInfo.event.name}
          </Text>
        </View>
      );
    }
    return (
      <View
        key={index}
        style={{
          width: Dimensions.get('window').width,
        }}
      >
        <TouchableOpacity
          onPress={() => this.props.onEventSelected(featuredInfo.event)}
          activeOpacity={0.5}
        >
          <FeaturedEvent event={featuredInfo.event} />
          {fadeOverlay}
        </TouchableOpacity>
      </View>
    );
  }

  render() {
    if (!this.props.featured || !this.props.featured.length) {
      return null;
    }
    let carousel = null;
    if (this.props.featured.length === 1) {
      carousel = this.renderPage(0);
    } else {
      carousel = (
        <Carousel
          indicatorOffset={0}
          indicatorColor="#FFFFFF"
          indicatorSize={CarouselDotIndicatorSize}
          indicatorSpace={15}
          animate
          loop
          delay={4000}
        >
          {this.props.featured.map((event, i) => this.renderPage(i))}
        </Carousel>
      );
    }
    return (
      <View style={{ height: 200 }}>
        {carousel}
      </View>
    );
  }
}

class OneboxView extends React.Component {
  props: {
    onebox: Onebox,
  };

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
    Linking.openURL(url).catch(err =>
      console.error('Error opening onebox url:', url, 'with Error:', err)
    );
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
    intl: intlShape,
    onPress: () => void,
  };

  render() {
    return (
      <Button
        icon={require('./images/add_calendar.png')}
        caption={this.props.intl.formatMessage(messages.addEvent)}
        color="green"
        textStyle={{ fontWeight: 'bold' }}
        style={styles.addEventButton}
        onPress={this.props.onPress}
        testID="addEvents"
      />
    );
  }
}
const AddEventButton = injectIntl(_AddEventButton);

class _EventListContainer extends React.Component {
  props: {
    onEventSelected: (event: Event) => void,
    onFeaturedEventSelected: (event: Event) => void,
    onAddEventClicked: (clickTarget: string) => void,

    // Self-managed props
    search: State,
    user: ?User,
    detectedLocation: (location: string) => Promise<void>,
    performSearch: () => Promise<void>,
    processUrl: (url: string) => Promise<void>,
    loadUserData: () => Promise<void>,
    intl: intlShape,
  };

  state: {
    sections: $ReadOnlyArray<{
      data: Array<any>,
      title: string,
    }>,
  };

  _listView: SectionList;

  constructor(props) {
    super(props);
    this.state = {
      sections: [],
    };
    this.state = this.getNewState(this.props);
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).setLocationAndSearch = this.setLocationAndSearch.bind(this);
    (this: any).renderItem = this.renderItem.bind(this);
  }

  componentDidMount() {
    this.initialize();
  }

  componentWillReceiveProps(nextProps) {
    // Only zoom to top, if there are existing state.sections being rendered
    if (
      nextProps.search.response !== this.props.search.response &&
      this.state.sections.length > 0
    ) {
      this._listView.scrollToLocation({
        animated: false,
        itemIndex: 0,
        sectionIndex: 0,
        // Ugly hack to get it to scroll the Header into view:
        // https://github.com/facebook/react-native/issues/14392
        viewPosition: 100,
      });
    }
    this.setState(this.getNewState(nextProps));
  }

  getNewState(props) {
    const sections = this.getData(props.search.response);
    const state = {
      ...this.state,
      sections,
    };
    return state;
  }

  async setLocationAndSearch(formattedAddress: string) {
    if (!formattedAddress) {
      return;
    }

    // Now do the actual search logic:
    await this.props.detectedLocation(formattedAddress);
    await this.props.performSearch();

    // If the user doesn't have a location, let's save one based on their search
    // Hopefully we'll have loaded the user data by now, after the search has completed...
    // But this isn't critical functionality, but just a best-effort attempt to save a location
    if (
      this.props.user &&
      this.props.user.ddUser &&
      !this.props.user.ddUser.location
    ) {
      await storeSavedAddress(formattedAddress);
    }
  }

  getData(response: ?SearchResponse) {
    const sections = [];
    const sectionHeaders = [];

    if (response) {
      if (response.onebox_links != null && response.onebox_links.length > 0) {
        const oneboxKey = this.props.intl.formatMessage(messages.specialLinks);
        sections.push({
          key: oneboxKey,
          title: oneboxKey,
          data: response.onebox_links.map(onebox => ({
            onebox,
            key: `Onebox: ${onebox.url}`,
          })),
        });
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
          const formattedStart = formatStartDateOnly(start, this.props.intl);
          let lastSection = sections[sections.length - 1];
          if (!lastSection || lastSection.title !== formattedStart) {
            sections.push({
              key: `Section: ${start}`,
              title: formattedStart,
              data: [],
            });
          }
          lastSection = sections[sections.length - 1];
          lastSection.data.push({ event: e, key: `Event: ${e.id}` });
        }
      }
    }
    return sections;
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
      console.log(
        'Failed to load GPS, falling back to last-searched address: ',
        address
      );
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

  bannerError(e) {
    console.log('didFailToReceiveAdWithError', e);
  }

  renderHeader() {
    if (this.props.search.error) {
      return this.renderErrorView();
    }
    return this.renderSummaryView();
  }

  renderItem(row) {
    if (row.item.event) {
      return (
        <EventRow
          event={row.item.event}
          onEventSelected={this.props.onEventSelected}
        />
      );
    } else {
      return <OneboxView onebox={row.item.onebox} />;
    }
  }

  renderErrorView() {
    return (
      <View style={styles.errorView}>
        <Text style={styles.errorText}>
          {this.props.intl.formatMessage(messages.fetchEventsError)}{' '}
          {this.props.intl.formatMessage(messages.networkRetry)}
        </Text>
      </View>
    );
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
        header = (
          <Text style={styles.listHeader}>
            {this.props.intl.formatMessage(message, {
              location: query.location,
              keywords: query.keywords,
            })}
          </Text>
        );
      }
    }
    return (
      <View>
        <FeaturedEvents
          featured={response.featuredInfos}
          onEventSelected={this.props.onFeaturedEventSelected}
        />
        <PeopleView
          people={response.people}
          headerStyle={styles.sectionHeader}
        />
        {header}
      </View>
    );
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
    return (
      <AdMobBanner
        bannerSize={'smartBannerPortrait'}
        adUnitID={adUnitID}
        didFailToReceiveAdWithError={this.bannerError}
      />
    );
  }

  renderListView() {
    return (
      <SectionList
        ref={x => {
          this._listView = x;
        }}
        style={[styles.listView]}
        ListHeaderComponent={this.renderHeader}
        // Refresher
        onRefresh={() => this.props.performSearch()}
        refreshing={this.props.search.loading}
        sections={this.state.sections}
        renderItem={this.renderItem}
        renderSectionHeader={({ section }) =>
          <SectionHeader title={upperFirst(section.title)} />}
        stickySectionHeadersEnabled
        initialNumToRender={5}
        maxToRenderPerBatch={5}
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
const EventListContainer = connect(
  state => ({
    search: state.search,
    user: state.user.userData,
  }),
  dispatch => ({
    detectedLocation: async location => {
      await dispatch(detectedLocation(location));
    },
    performSearch: async () => {
      await dispatch(performSearch());
    },
    processUrl: async url => {
      await dispatch(processUrl(url));
    },
    loadUserData: async () => {
      await loadUserData(dispatch);
    },
  })
)(injectIntl(_EventListContainer));

export default EventListContainer;

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
    height: SectionHeight,
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
