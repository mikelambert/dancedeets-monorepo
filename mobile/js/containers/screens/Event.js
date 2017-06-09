/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { AppState, Image, StyleSheet, View } from 'react-native';
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
import { Event } from 'dancedeets-common/js/events/models';
import type { State } from '../../reducers/search';
import EventListContainer from '../../events/list';
import EventPager from '../../events/EventPager';
import { Text, ZoomableImage } from '../../ui';
import {
  canGetValidLoginFor,
  performSearch,
  setHeaderStatus,
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
    onClick: () => void,

    // Self-managed props
    search: State,
  };

  statusText() {
    const searchQuery = this.props.search.searchQuery;
    if (searchQuery.location && searchQuery.keywords) {
      return `${searchQuery.keywords}: ${searchQuery.location}`;
    } else if (searchQuery.location) {
      return searchQuery.location;
    } else if (searchQuery.keywords) {
      return searchQuery.keywords;
    } else {
      return 'Events';
    }
  }

  render() {
    return (
      <TouchableItem onPress={this.props.onClick}>
        <HeaderTitle style={{ color: 'white' }}>
          {this.statusText()}
        </HeaderTitle>
      </TouchableItem>
    );
  }
}
const SearchHeaderTitleSummary = connect(state => ({
  search: state.search,
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
    ...(screenProps.headerOpened
      ? {
          headerTitle: '',
          headerLeft: (
            <NavButton
              onPress={() => screenProps.setHeaderStatus(false)}
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
          headerTitle: (
            <SearchHeaderTitleSummary
              onClick={() => screenProps.setHeaderStatus(true)}
            />
          ),
          // onPress={this.props.onAddEvent}
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
    // TODO(navigation): Should we pass in an i18n'ed title?
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
    // TODO(navigation) : should this swap instead ofnavigate?
    this.props.navigation.setParams({ event });
  }

  onFlyerSelected(event) {
    trackWithEvent('View Flyer', event);
    // TODO(navigation): Should we pass in an i18n'ed title?
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
    setHeaderStatus: (status: boolean) => void,
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
          headerOpened: this.props.searchHeader.headerOpened,
          setHeaderStatus: this.props.setHeaderStatus,
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
    setHeaderStatus: (status: boolean) => dispatch(setHeaderStatus(status)),
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
