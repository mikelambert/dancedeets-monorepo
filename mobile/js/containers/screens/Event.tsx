/**
 * Copyright 2016 DanceDeets.
 *
 * React Navigation v6 Event screens
 */

import * as React from 'react';
import {
  Animated,
  Dimensions,
  Image,
  Text as RealText,
  TouchableOpacity,
  TouchableWithoutFeedback,
  View,
} from 'react-native';
import { createStackNavigator, StackScreenProps } from '@react-navigation/stack';
import { connect } from 'react-redux';
import { useIntl, defineMessages, IntlShape } from 'react-intl';
import Icon from 'react-native-vector-icons/Ionicons';
import type { SearchQuery } from 'dancedeets-common/js/events/search';
import type { State } from '../../reducers/search';
import EventListContainer from '../../events/list';
import EventPager from '../../events/EventPager';
import { HorizontalView, semiNormalize, Text, ZoomableImage } from '../../ui';
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
import type { State as SearchHeaderState } from '../../ducks/searchHeader';
import ShareEventIcon from '../ShareEventIcon';
import { gradientTop } from '../../Colors';

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
  cancelButton: {
    id: 'buttons.cancel',
    defaultMessage: 'Cancel',
    description: 'Cancel button',
  },
  searchButton: {
    id: 'buttons.search',
    defaultMessage: 'Search',
    description: 'Button to do the search',
  },
});

// Type definitions for navigation
type EventStackParamList = {
  EventList: undefined;
  FeaturedEventView: { event: any };
  EventView: { event: any };
  FlyerView: { event: any };
  AddEvents: undefined;
};

const Stack = createStackNavigator<EventStackParamList>();

// Search Header Title Summary Component
interface SearchHeaderTitleSummaryProps {
  onPress: () => void;
  searchHeader: any;
  query: SearchQuery;
}

class _SearchHeaderTitleSummary extends React.Component<SearchHeaderTitleSummaryProps> {
  render() {
    const searchQuery = this.props.query;
    const keywords = searchQuery.keywords ? (
      <RealText numberOfLines={1}>{searchQuery.keywords}</RealText>
    ) : null;
    const spacer =
      searchQuery.location && searchQuery.keywords ? (
        <View style={{ paddingRight: 5 }} />
      ) : null;
    const location = searchQuery.location ? (
      <RealText
        style={{
          color: 'grey',
          fontSize: semiNormalize(12),
          lineHeight: semiNormalize(16),
        }}
        numberOfLines={1}
      >
        {searchQuery.location}
      </RealText>
    ) : null;
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
const SearchHeaderTitleSummary = connect((state: any) => ({
  query: state.search.response
    ? state.search.response.query
    : state.searchQuery,
  searchHeader: state.searchHeader,
}))(_SearchHeaderTitleSummary);

// NavButton Component
interface NavButtonProps {
  onPress: () => void;
  imageSource?: number;
  text?: string;
  disabled?: boolean;
}

function NavButton({ onPress, imageSource, text, disabled }: NavButtonProps) {
  const contents: React.ReactNode[] = [];
  if (imageSource) {
    contents.push(<Image key="image" source={imageSource} />);
  }
  if (text) {
    contents.push(
      <Text
        key="text"
        style={{
          fontSize: 17,
          color: disabled ? '#bbb' : 'white',
        }}
      >
        {text}
      </Text>
    );
  }
  return (
    <TouchableOpacity onPress={onPress} style={{ marginLeft: 10, marginRight: 10 }}>
      <View>{contents}</View>
    </TouchableOpacity>
  );
}

// Event List Screen
interface EventListScreenProps extends StackScreenProps<EventStackParamList, 'EventList'> {}

function EventListScreen({ navigation }: EventListScreenProps) {
  const onEventSelected = (event: any) => {
    trackWithEvent('View Event', event);
    navigation.navigate('EventView', { event });
  };

  const onFeaturedEventSelected = (event: any) => {
    trackWithEvent('View Featured Event', event);
    navigation.navigate('FeaturedEventView', { event });
  };

  return (
    <EventListContainer
      onEventSelected={onEventSelected}
      onFeaturedEventSelected={onFeaturedEventSelected}
    />
  );
}

// Featured Event Screen
interface FeaturedEventScreenProps extends StackScreenProps<EventStackParamList, 'FeaturedEventView'> {}

function FeaturedEventScreen({ navigation, route }: FeaturedEventScreenProps) {
  const { event } = route.params;

  const onFlyerSelected = (evt: any) => {
    trackWithEvent('View Flyer', evt);
    navigation.navigate('FlyerView', { event: evt });
  };

  return (
    <PositionProvider
      renderWithPosition={(position: any) => (
        <FullEventView
          onFlyerSelected={onFlyerSelected}
          event={event}
          currentPosition={position}
        />
      )}
    />
  );
}

// Event Screen
interface EventScreenProps extends StackScreenProps<EventStackParamList, 'EventView'> {}

function EventScreen({ navigation, route }: EventScreenProps) {
  const { event } = route.params;

  const onEventNavigated = (evt: any) => {
    trackWithEvent('View Event', evt);
    navigation.setParams({ event: evt });
  };

  const onFlyerSelected = (evt: any) => {
    trackWithEvent('View Flyer', evt);
    navigation.navigate('FlyerView', { event: evt });
  };

  return (
    <EventPager
      selectedEvent={event}
      onFlyerSelected={onFlyerSelected}
      onEventNavigated={onEventNavigated}
    />
  );
}

// Flyer Screen
interface FlyerScreenProps extends StackScreenProps<EventStackParamList, 'FlyerView'> {}

function FlyerScreen({ route }: FlyerScreenProps) {
  const { event } = route.params;
  return (
    <ZoomableImage
      url={event.picture.source}
      width={event.picture.width}
      height={event.picture.height}
    />
  );
}

// Add Events Screen
function AddEventsScreen() {
  return <AddEvents />;
}

// Main Event Screens Navigator
export function EventScreensNavigator() {
  const intl = useIntl();

  return (
    <Stack.Navigator
      screenOptions={{
        headerTintColor: 'white',
        headerStyle: {
          backgroundColor: gradientTop,
        },
        cardStyle: {
          backgroundColor: 'black',
        },
      }}
    >
      <Stack.Screen
        name="EventList"
        component={EventListScreen}
        options={{
          title: intl.formatMessage(messages.eventsTitle),
        }}
      />
      <Stack.Screen
        name="FeaturedEventView"
        component={FeaturedEventScreen}
        options={({ route }) => ({
          title: route.params.event.name,
          headerRight: () => <ShareEventIcon event={route.params.event} />,
        })}
      />
      <Stack.Screen
        name="EventView"
        component={EventScreen}
        options={({ route }) => ({
          title: route.params.event.name,
          headerRight: () => <ShareEventIcon event={route.params.event} />,
        })}
      />
      <Stack.Screen
        name="FlyerView"
        component={FlyerScreen}
        options={{
          title: intl.formatMessage(messages.viewFlyer),
        }}
      />
      <Stack.Screen
        name="AddEvents"
        component={AddEventsScreen}
        options={{
          title: intl.formatMessage(messages.addEventTitle),
        }}
      />
    </Stack.Navigator>
  );
}
