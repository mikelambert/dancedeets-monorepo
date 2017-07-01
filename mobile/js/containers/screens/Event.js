/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Animated,
  AppState,
  Dimensions,
  Image,
  StyleSheet,
  Text as RealText,
  TouchableWithoutFeedback,
  View,
} from 'react-native';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationSceneRendererProps,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import {
  createNavigator,
  NavigationActions,
  StackNavigator,
} from 'react-navigation';
import HeaderTitle from 'react-navigation/src/views/HeaderTitle';
import { connect } from 'react-redux';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import TouchableItem from 'react-navigation/src/views/TouchableItem';
import Icon from 'react-native-vector-icons/Ionicons';
import { Event } from 'dancedeets-common/js/events/models';
import type { SearchQuery } from 'dancedeets-common/js/events/search';
import type { State } from '../../reducers/search';
import EventListContainer from '../../events/list';
import EventPager from '../../events/EventPager';
import {
  HorizontalView,
  semiNormalize,
  Text,
  TextInput,
  ZoomableImage,
} from '../../ui';
import {
  canGetValidLoginFor,
  performSearch,
  hideSearchForm,
  showSearchForm,
} from '../../actions';
import AddEvents from '../AddEvents';
import { track, trackWithEvent } from '../../store/track';
import PositionProvider from '../../providers/positionProvider';
import { FullEventView } from '../../events/uicomponents';
import MyNavigator from './Navigator';
import type { State as SearchHeaderState } from '../../ducks/searchHeader';
import ShareEventIcon from '../ShareEventIcon';

const messages = defineMessages({
  eventsTitle: {
    id: 'navigator.eventsTitle',
    defaultMessage: 'Events',
    description: 'Initial title bar for Events tab',
  },
  addEventTitle: {
    id: 'navigator.addEvent',
    defaultMessage: 'Add Event',
    description: 'Title Bar for Adding Event',
  },
  featureAddingEvents: {
    id: 'feature.addingEvents',
    defaultMessage: 'Adding Events',
    description:
      'The name of the Add Event feature when requesting permissions',
  },
  viewFlyer: {
    id: 'navigator.viewFlyer',
    defaultMessage: 'View Flyer',
    description: 'Title Bar for Viewing Flyer',
  },
});
class _SearchHeaderTitleSummary extends React.Component {
  props: {
    onPress: () => void,

    // Self-managed props
    searchHeader: any,
    query: SearchQuery,
  };

  render() {
    const searchQuery = this.props.query;
    const keywords = searchQuery.keywords
      ? <RealText numberOfLines={1}>
          {searchQuery.keywords}
        </RealText>
      : null;
    const spacer = searchQuery.location && searchQuery.keywords
      ? <View style={{ paddingRight: 5 }} />
      : null;
    const location = searchQuery.location
      ? <RealText
          style={{
            color: 'grey',
            fontSize: semiNormalize(12),
            lineHeight: semiNormalize(16),
          }}
          numberOfLines={1}
        >
          {searchQuery.location}
        </RealText>
      : null;
    const sideMargin = 40;
    return (
      <Animated.View
        style={{
          opacity: this.props.searchHeader.headerAnim.interpolate({
            inputRange: [0, 0.5],
            outputRange: [1, 0],
          }),
          transform: [
            {
              translateY: this.props.searchHeader.headerAnim.interpolate({
                inputRange: [0, 1],
                outputRange: [0, 50],
              }),
            },
            {
              scaleX: this.props.searchHeader.headerAnim.interpolate({
                inputRange: [0, 1],
                outputRange: [1, 2],
              }),
            },
          ],
        }}
      >
        <TouchableWithoutFeedback
          style={{
            maxWidth: Dimensions.get('window').width - sideMargin * 2,
          }}
          onPress={() => {
            this.props.onPress();
          }}
        >
          <HorizontalView
            style={{
              borderRadius: 5,
              backgroundColor: 'white',
              alignItems: 'center',
              paddingHorizontal: 5,
              overflow: 'hidden',
              marginHorizontal: 20,
              minWidth: 200,
              maxWidth: Dimensions.get('window').width - sideMargin * 2,
            }}
          >
            <Icon
              name="md-search"
              size={20}
              color="black"
              style={{ marginVertical: 2, width: 20 }}
            />
            {keywords}
            {spacer}
            {location}
          </HorizontalView>
        </TouchableWithoutFeedback>
      </Animated.View>
    );
  }
}
const SearchHeaderTitleSummary = connect(state => ({
  query: state.search.response
    ? state.search.response.query
    : state.searchQuery,
  searchHeader: state.searchHeader,
}))(_SearchHeaderTitleSummary);

class NavButton extends React.PureComponent {
  props: {
    onPress: () => void,
    imageSource?: number,
    text?: string,
    disabled?: boolean,
  };

  render() {
    let contents = [
      this.props.imageSource
        ? <Image key="image" source={this.props.imageSource} />
        : null,
      this.props.text
        ? <Text
            key="text"
            style={{
              fontSize: 17,
              color: this.props.disabled ? '#bbb' : 'white',
            }}
          >
            {this.props.text}
          </Text>
        : null,
    ];
    if (!this.props.disabled) {
      contents = (
        <TouchableItem onPress={() => this.props.onPress()}>
          <View>{contents}</View>
        </TouchableItem>
      );
    }
    return (
      <View style={{ marginLeft: 10, marginRight: 10 }}>
        {contents}
      </View>
    );
  }
}

class EventListScreen extends React.Component {
  static navigationOptions = ({ screenProps }) => {
    // These screens need to be okay runing without a searchHeader (or anything other than intl, really)
    // The outermost TabView computes navigationOptions to request some tabBar* properties
    // We don't override them at all, or ever, so safely returning null here works.
    // But we need to be careful in all our navigationOptions functions, that they never depend on too many things.
    // I described the issue in more detail here:
    // https://github.com/react-community/react-navigation/issues/1848
    if (!screenProps.searchHeader) {
      return null;
    }
    return {
      ...(screenProps.searchHeader.navbarTitleVisible
        ? {
            headerTitle: (
              <SearchHeaderTitleSummary onPress={screenProps.showSearchForm} />
            ),
          }
        : { headerTitle: '' }),
      ...(screenProps.searchHeader.searchFormVisible
        ? {
            headerLeft: (
              <NavButton onPress={screenProps.hideSearchForm} text="Cancel" />
            ),
            headerRight: (
              <NavButton
                onPress={screenProps.performSearch}
                text="Search"
                disabled={!screenProps.canSearch}
              />
            ),
          }
        : {
            headerRight: (
              <NavButton
                onPress={() => screenProps.onAddEventClicked('Search Header')}
                imageSource={require('../../events/images/add_calendar.png')}
              />
            ),
          }),
    };
  };

  props: {
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
    screenProps: Object,
  };

  constructor(props) {
    super(props);
    (this: any).onEventSelected = this.onEventSelected.bind(this);
    (this: any).onFeaturedEventSelected = this.onFeaturedEventSelected.bind(
      this
    );
  }

  onEventSelected(event) {
    trackWithEvent('View Event', event);
    this.props.navigation.navigate('EventView', { event });
  }

  onFeaturedEventSelected(event) {
    trackWithEvent('View Featured Event', event);
    this.props.navigation.navigate('FeaturedEventView', { event });
  }

  render() {
    return (
      <EventListContainer
        onEventSelected={this.onEventSelected}
        onFeaturedEventSelected={this.onFeaturedEventSelected}
      />
    );
  }
}

class FeaturedEventScreen extends React.Component {
  static navigationOptions = ({ navigation }) => ({
    title: navigation.state.params.event.name,
    headerRight: <ShareEventIcon event={navigation.state.params.event} />,
  });

  props: {
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
  };

  constructor(props) {
    super(props);
    (this: any).onFlyerSelected = this.onFlyerSelected.bind(this);
  }

  onFlyerSelected(event) {
    trackWithEvent('View Flyer', event);
    this.props.navigation.navigate('FlyerView', { event });
  }

  render() {
    const event = this.props.navigation.state.params.event;
    return (
      <PositionProvider
        renderWithPosition={position =>
          <FullEventView
            onFlyerSelected={this.onFlyerSelected}
            event={event}
            currentPosition={position}
          />}
      />
    );
  }
}

class EventScreen extends React.Component {
  static navigationOptions = ({ navigation }) => ({
    title: navigation.state.params.event.name,
    headerRight: <ShareEventIcon event={navigation.state.params.event} />,
  });

  props: {
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
  };

  constructor(props) {
    super(props);
    (this: any).onEventNavigated = this.onEventNavigated.bind(this);
    (this: any).onFlyerSelected = this.onFlyerSelected.bind(this);
  }

  onEventNavigated(event) {
    trackWithEvent('View Event', event);
    this.props.navigation.setParams({ event });
  }

  onFlyerSelected(event) {
    trackWithEvent('View Flyer', event);
    this.props.navigation.navigate('FlyerView', { event });
  }

  render() {
    const event = this.props.navigation.state.params.event;
    return (
      <EventPager
        selectedEvent={event}
        onFlyerSelected={this.onFlyerSelected}
        onEventNavigated={this.onEventNavigated}
      />
    );
  }
}

class FlyerScreen extends React.Component {
  static navigationOptions = ({ screenProps }) => ({
    title: screenProps.intl.formatMessage(messages.viewFlyer),
  });

  props: {
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
  };

  render() {
    const event: any = this.props.navigation.state.params.event;
    return (
      <ZoomableImage
        url={event.picture.source}
        width={event.picture.width}
        height={event.picture.height}
      />
    );
  }
}

class AddEventsScreen extends React.Component {
  static navigationOptions = ({ screenProps }) => ({
    title: screenProps.intl.formatMessage(messages.addEventTitle),
  });

  render() {
    return <AddEvents />;
  }
}

const RealEventScreensNavigator = MyNavigator('events', {
  EventList: { screen: EventListScreen },
  FeaturedEventView: { screen: FeaturedEventScreen },
  EventView: { screen: EventScreen },
  FlyerView: { screen: FlyerScreen },
  AddEvents: { screen: AddEventsScreen },
});

class _EventScreensNavigator extends React.Component {
  props: {
    navRef?: (nav: StackNavigator) => void,

    // Self-managed props
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
    intl: intlShape,
    canOpenAddEvent: (props: any) => Promise<boolean>,
    search: State,
    canSearch: boolean,
    searchHeader: SearchHeaderState,
    showSearchForm: () => void,
    hideSearchForm: () => void,
    performSearch: () => Promise<void>,
  };

  _nav: StackNavigator;

  constructor(props) {
    super(props);
    (this: any).onAddEventClicked = this.onAddEventClicked.bind(this);
  }

  async onAddEventClicked(source) {
    console.log(this, source);
    track('Add Event', { source });
    if (await this.props.canOpenAddEvent(this.props)) {
      this.props.navigation.navigate('AddEvents');
    }
  }

  render() {
    return (
      <RealEventScreensNavigator
        ref={nav => {
          this._nav = nav;
          if (this.props.navRef != null) {
            this.props.navRef(nav);
          }
        }}
        screenProps={{
          intl: this.props.intl,

          // For the Event List Screen
          search: this.props.search,
          searchHeader: this.props.searchHeader,
          showSearchForm: this.props.showSearchForm,
          hideSearchForm: this.props.hideSearchForm,
          performSearch: this.props.performSearch,
          onAddEventClicked: this.onAddEventClicked,
          canSearch: this.props.canSearch,
        }}
        navigation={this.props.navigation}
      />
    );
  }
}
export const EventScreensNavigator = connect(
  state => ({
    search: state.search,
    canSearch: state.searchQuery.location || state.searchQuery.keywords,
    isLoggedIn: state.user.isLoggedIn,
    searchHeader: state.searchHeader,
  }),
  dispatch => ({
    performSearch: async () => {
      await dispatch(performSearch());
    },
    showSearchForm: (status: boolean) => dispatch(showSearchForm()),
    hideSearchForm: (status: boolean) => dispatch(hideSearchForm()),
    canOpenAddEvent: async props => {
      if (
        !props.isLoggedIn &&
        !await canGetValidLoginFor(
          props.intl.formatMessage(messages.featureAddingEvents),
          props.intl,
          dispatch
        )
      ) {
        return false;
      }
      return true;
    },
  })
)(injectIntl(_EventScreensNavigator));
EventScreensNavigator.router = RealEventScreensNavigator.router;
