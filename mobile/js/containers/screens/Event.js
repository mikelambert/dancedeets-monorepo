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
import { connect } from 'react-redux';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import { Event } from 'dancedeets-common/js/events/models';
import EventListContainer from '../../events/list';
import EventPager from '../../events/EventPager';
import { ZoomableImage } from '../../ui';
import { canGetValidLoginFor } from '../../actions';
import AddEvents from '../AddEvents';
import { track, trackWithEvent } from '../../store/track';
import PositionProvider from '../../providers/positionProvider';
import { FullEventView } from '../../events/uicomponents';

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
    description: 'The name of the Add Event feature when requesting permissions',
  },
  viewFlyer: {
    id: 'navigator.viewFlyer',
    defaultMessage: 'View Flyer',
    description: 'Title Bar for Viewing Flyer',
  },
});

class EventListScreen extends React.Component {
  static navigationOptions = ({ screenProps }) => ({
    title: screenProps.intl.formatMessage(messages.eventsTitle),
  });

  props: {
    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
    screenProps: Object,
  };

  constructor(props) {
    super(props);
    (this: any).onEventSelected = this.onEventSelected.bind(this);
    (this: any).onAddEventClicked = this.onAddEventClicked.bind(this);
    (this: any).onFeaturedEventSelected = this.onFeaturedEventSelected.bind(
      this
    );
  }

  onEventSelected(event) {
    trackWithEvent('View Event', event);
    this.props.navigation.navigate('EventView', { event });
  }

  async onAddEventClicked(source) {
    track('Add Event', { source });
    if (await this.props.screenProps.canOpenAddEvent(this.props)) {
      this.props.navigation.navigate('AddEvents');
    }
  }

  onFeaturedEventSelected(event) {
    trackWithEvent('View Featured Event', event);
    this.props.navigation.navigate('FeaturedEventView', { event });
  }

  render() {
    return (
      <EventListContainer
        onEventSelected={this.onEventSelected}
        onAddEventClicked={this.onAddEventClicked}
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
        renderWithPosition={position => (
          <FullEventView
            onFlyerSelected={this.onFlyerSelected}
            event={event}
            currentPosition={position}
          />
        )}
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
    return <EventPager
      selectedEvent={event}
      onFlyerSelected={this.onFlyerSelected}
      onEventNavigated={this.onEventNavigated}
    />;
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

const EventScreens = StackNavigator({
  EventList: { screen: EventListScreen },
  FeaturedEventView: { screen: FeaturedEventScreen },
  EventView: { screen: EventScreen },
  FlyerView: { screen: FlyerScreen },
  AddEvents: { screen: AddEventsScreen },
});

class _EventScreensView extends React.Component {
  props: {
    intl: intlShape,
    canOpenAddEvent: (props: any) => void,
  };

  render() {
    return (
      <EventScreens
        screenProps={{
          intl: this.props.intl,
          canOpenAddEvent: async () =>
            await this.props.canOpenAddEvent(this.props),
        }}
      />
    );
  }
}

const EventScreensView = connect(
  state => ({
    search: state.search,
    user: state.user.userData,
  }),
  dispatch => ({
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
