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
import TabNavigator from 'react-native-tab-navigator';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationSceneRendererProps,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { NavigationActions, StackNavigator } from 'react-navigation';
import HeaderTitle from 'react-navigation/src/views/HeaderTitle';
import { connect } from 'react-redux';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import TouchableItem from 'react-navigation/src/views/TouchableItem';
import Icon from 'react-native-vector-icons/Ionicons';
import { Event } from 'dancedeets-common/js/events/models';
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
    search: State,
  };

  render() {
    const searchQuery = this.props.search.response
      ? this.props.search.response.query
      : this.props.search.searchQuery;
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
              maxWidth: Dimensions.get('window').width - sideMargin * 2,
            }}
          >
            <Icon
              name="md-search"
              size={20}
              style={{ marginTop: 4, width: 20 }}
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
  search: state.search,
  searchHeader: state.searchHeader,
}))(_SearchHeaderTitleSummary);

class NavButton extends React.PureComponent {
  props: {
    onPress: () => void,
    imageSource?: number,
    text?: string,
  };

  render() {
    return (
      <View style={{ marginLeft: 10, marginRight: 10 }}>
        <TouchableItem onPress={() => this.props.onPress()}>
          {this.props.imageSource
            ? <Image source={this.props.imageSource} />
            : null}
          {this.props.text
            ? <Text style={{ fontSize: 17 }}>
                {this.props.text}
              </Text>
            : null}
        </TouchableItem>
      </View>
    );
  }
}

class EventListScreen extends React.Component {
  static navigationOptions = ({ screenProps }) => ({
    title: screenProps.intl.formatMessage(messages.eventsTitle),
    ...(screenProps.searchHeader.navbarTitleVisible
      ? {
          headerTitle: (
            <SearchHeaderTitleSummary
              onPress={() => screenProps.showSearchForm()}
            />
          ),
        }
      : { headerTitle: '' }),
    ...(screenProps.searchHeader.searchFormVisible
      ? {
          headerLeft: (
            <NavButton
              onPress={() => screenProps.hideSearchForm()}
              text="Cancel"
            />
          ),
          headerRight: (
            <NavButton
              onPress={() => screenProps.performSearch()}
              text="Search"
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
  });

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
        onAddEventClicked={this.props.screenProps.onAddEventClicked}
        onFeaturedEventSelected={this.onFeaturedEventSelected}
      />
    );
  }
}

class FeaturedEventScreen extends React.Component {
  static navigationOptions = ({ navigation }) => ({
    title: navigation.state.params.event.name,
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
    console.log(event);
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

const EventScreens = MyNavigator({
  EventList: { screen: EventListScreen },
  FeaturedEventView: { screen: FeaturedEventScreen },
  EventView: { screen: EventScreen },
  FlyerView: { screen: FlyerScreen },
  AddEvents: { screen: AddEventsScreen },
});

class _EventScreensView extends React.Component {
  props: {
    navRef: (nav: StackNavigator) => void,

    // Self-managed props
    intl: intlShape,
    canOpenAddEvent: (props: any) => Promise<boolean>,
    search: State,
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
    track('Add Event', { source });
    console.log(this._nav);
    if (await this.props.canOpenAddEvent(this.props)) {
      this._nav._navigation.navigate('AddEvents');
    }
  }

  render() {
    return (
      <EventScreens
        ref={nav => {
          this._nav = nav;
          this.props.navRef(nav);
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
        }}
      />
    );
  }
}
const EventScreensView = connect(
  state => ({
    search: state.search,
    user: state.user.userData,
    searchHeader: state.searchHeader,
  }),
  dispatch => ({
    performSearch: async () => {
      await dispatch(performSearch());
    },
    showSearchForm: (status: boolean) => dispatch(showSearchForm(status)),
    hideSearchForm: (status: boolean) => dispatch(hideSearchForm(status)),
    canOpenAddEvent: async props => {
      if (
        !props.user &&
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
)(injectIntl(_EventScreensView));

export default EventScreensView;
