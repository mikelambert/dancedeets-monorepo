/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import {
  ActivityIndicator,
  FlatList,
  Image,
  PixelRatio,
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';
import { AccessToken } from 'react-native-fbsdk';
import { connect } from 'react-redux';
import moment from 'moment';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import type { AddEventData } from '../addEventsModels';
import type { DisplayOptions, State } from '../reducers/addEvents';
import { track } from '../store/track';
import {
  addEvent,
  clickEvent,
  reloadAddEvents,
  setOnlyUnadded,
  setSortOrder,
} from '../actions';
import { yellowColors, gradientTop } from '../Colors';
import {
  Button,
  HorizontalView,
  normalize,
  RibbonBanner,
  SegmentedControl,
  semiNormalize,
  Text,
} from '../ui';
import { weekdayDateTime } from '../formats';

const messages = defineMessages({
  introText: {
    id: 'addEvents.introText',
    defaultMessage:
      'DanceDeets works best when dancers like you, share the dance events you know about.',
    description:
      'At the top of the Add Event panel, explaining how things work.',
  },
  showEvents: {
    id: 'addEvents.showEvents',
    defaultMessage: 'Show events:',
    description:
      'The filter setting before offering All and Not-yet-added-only filters.',
  },
  showEventsAll: {
    id: 'addEvents.showEvents.all',
    defaultMessage: 'All',
    description: 'Show all events, already-added and not-yet-added',
  },
  showEventsNotYetAdded: {
    id: 'addEvents.showEvents.notYetAdded',
    defaultMessage: 'Not-yet-added only',
    description: 'Show only not-yet-added events',
  },
  sort: {
    id: 'addEvents.sort',
    defaultMessage: 'Sort:',
    description:
      'The filter setting before offering All and Not-yet-added-only filters.',
  },
  sortByStartDate: {
    id: 'addEvents.sort.byStartDate',
    defaultMessage: 'By Start Date',
    description: 'Sort events by start date',
  },
  sortByName: {
    id: 'addEvents.sort.byName',
    defaultMessage: 'By Name',
    description: 'Sort events by name',
  },
  addEventButton: {
    id: 'addEvents.button',
    defaultMessage: 'Add Event',
    description: 'Add Event Button',
  },
  addedBanner: {
    id: 'addEvents.banner',
    defaultMessage: 'Added',
    description: 'Red Banner over the event photo',
  },
});

class _FilterHeader extends React.Component {
  props: {
    intl: intlShape,
    displayOptions: DisplayOptions,
    setOnlyUnadded: (onlyUnadded: boolean) => void,
    setSortOrder: (x: string) => void,
  };

  render() {
    return (
      <View style={styles.header}>
        <Text style={styles.headerRow}>
          {this.props.intl.formatMessage(messages.introText)}
        </Text>

        <HorizontalView style={styles.headerRow}>
          <Text style={styles.headerText}>
            {this.props.intl.formatMessage(messages.showEvents)}
          </Text>
          <SegmentedControl
            values={[
              this.props.intl.formatMessage(messages.showEventsAll),
              this.props.intl.formatMessage(messages.showEventsNotYetAdded),
            ]}
            style={{ flex: 1 }}
            defaultIndex={this.props.displayOptions.onlyUnadded ? 1 : 0}
            tintColor={yellowColors[1]}
            tryOnChange={index => this.props.setOnlyUnadded(index === 1)}
          />
        </HorizontalView>

        <HorizontalView style={styles.headerRow}>
          <Text style={styles.headerText}>
            {this.props.intl.formatMessage(messages.sort)}
          </Text>
          <SegmentedControl
            values={[
              this.props.intl.formatMessage(messages.sortByStartDate),
              this.props.intl.formatMessage(messages.sortByName),
            ]}
            style={{ flex: 1 }}
            tintColor={yellowColors[1]}
            defaultIndex={
              this.props.displayOptions.sortOrder === 'ByName' ? 1 : 0
            }
            tryOnChange={index =>
              this.props.setSortOrder(index === 1 ? 'ByName' : 'ByDate')}
          />
        </HorizontalView>
      </View>
    );
  }
}
const FilterHeader = connect(
  state => ({
    displayOptions: state.addEvents.displayOptions,
  }),
  dispatch => ({
    setOnlyUnadded: (x): Promise<void> => dispatch(setOnlyUnadded(x)),
    setSortOrder: x => dispatch(setSortOrder(x)),
  })
)(injectIntl(_FilterHeader));

class _AddEventRow extends React.Component {
  props: {
    token: AccessToken,
    onEventClicked: (event: AddEventData) => void,
    onEventAdded: (event: AddEventData) => void,
    event: AddEventData,
    intl: intlShape.isRequired,
  };

  render() {
    const width = semiNormalize(75);
    const imageUrl = `https://graph.facebook.com/${this.props.event
      .id}/picture?type=large&access_token=${this.props.token.accessToken}`;
    let tempOverlay = null;
    if (this.props.event.clickedConfirming) {
      tempOverlay = (
        <View style={{ position: 'absolute', top: 20, left: 0 }}>
          <Button
            color="purple"
            size="small"
            caption={this.props.intl.formatMessage(messages.addEventButton)}
            onPress={() => {
              this.props.onEventAdded(this.props.event);
            }}
          />
        </View>
      );
    } else if (this.props.event.pending) {
      tempOverlay = (
        <View style={{ position: 'absolute', top: 20, left: 0 }}>
          <ActivityIndicator color="white" size="large" />
        </View>
      );
    }
    const bannerText = this.props.intl
      .formatMessage(messages.addedBanner)
      .toUpperCase();
    const addedBanner = this.props.event.loaded ? (
      <RibbonBanner text={bannerText} width={width} />
    ) : null;
    const textColor = this.props.event.loaded || tempOverlay ? '#888' : 'white';

    const start = moment.parseZone(this.props.event.start_time);
    const formattedStart = this.props.intl.formatDate(
      start.toDate(),
      weekdayDateTime
    );

    const row = (
      <HorizontalView>
        <View style={styles.leftEventImage}>
          <View style={{ borderRadius: 10, width }}>
            <Image
              source={{ uri: imageUrl }}
              style={{ width, height: width }}
            />
            {addedBanner}
          </View>
        </View>
        <View style={styles.rightTextDescription}>
          <Text style={[styles.title, { color: textColor }]} numberOfLines={2}>
            {this.props.event.name}
          </Text>
          <Text style={[styles.title, { color: textColor }]}>
            {formattedStart}
          </Text>
          {tempOverlay}
        </View>
      </HorizontalView>
    );
    if (this.props.event.loaded || this.props.event.pending) {
      return <View style={styles.row}>{row}</View>;
    } else {
      return (
        <View style={styles.row}>
          <TouchableOpacity
            onPress={() => this.props.onEventClicked(this.props.event)}
            activeOpacity={0.5}
          >
            {row}
          </TouchableOpacity>
        </View>
      );
    }
  }
}
const AddEventRow = injectIntl(_AddEventRow);

class _AddEventList extends React.Component {
  static applyFilterSorts(props, results) {
    let finalResults = results;
    if (props.addEvents.displayOptions.onlyUnadded) {
      finalResults = finalResults.filter(x => !x.loaded);
    }
    if (props.addEvents.displayOptions.sortOrder === 'ByName') {
      finalResults = finalResults
        .slice()
        .sort((a, b) => a.name.localeCompare(b.name));
    } else if (props.addEvents.displayOptions.sortOrder === 'ByDate') {
      finalResults = finalResults
        .slice()
        .sort((a, b) => a.start_time.localeCompare(b.start_time));
    }
    return finalResults;
  }

  props: {
    addEvent: (eventId: string) => void,
    clickEvent: (eventId: string) => void,
    addEvents: State,
    reloadAddEvents: () => void,
  };

  state: {
    token: ?AccessToken,
  };

  constructor(props) {
    super(props);
    this.state = {
      token: null,
    };
    this.loadToken();
    (this: any).renderRow = this.renderRow.bind(this);
  }

  componentDidMount() {
    if (!this.props.addEvents.results) {
      this.props.reloadAddEvents();
    }
  }

  async loadToken() {
    const token = await AccessToken.getCurrentAccessToken();
    this.setState({
      token,
    });
  }

  renderRow(row) {
    const item = row.item;
    return (
      <AddEventRow
        event={item}
        token={this.state.token}
        onEventClicked={(event: AddEventData) =>
          this.props.clickEvent(event.id)}
        onEventAdded={(event: AddEventData) => {
          track('Add Event To Site', { 'Event ID': event.id });
          this.props.addEvent(event.id);
        }}
      />
    );
  }

  render() {
    if (!this.state.token) {
      return null;
    }
    const results = AddEventList.applyFilterSorts(
      this.props,
      this.props.addEvents.results || []
    );
    return (
      <FlatList
        style={[styles.listView]}
        data={results}
        refreshing={this.props.addEvents.loading}
        onRefresh={() => this.props.reloadAddEvents()}
        renderItem={this.renderRow}
        scrollsToTop={false}
        indicatorStyle="white"
      />
    );
  }
}
const AddEventList = connect(
  state => ({
    addEvents: state.addEvents,
  }),
  dispatch => ({
    clickEvent: (eventId: string) => dispatch(clickEvent(eventId)),
    addEvent: (eventId: string) => dispatch(addEvent(eventId)),
    reloadAddEvents: () => dispatch(reloadAddEvents()),
  })
)(_AddEventList);

export default class AddEvents extends React.Component {
  render() {
    return (
      <View style={styles.container}>
        <FilterHeader />
        <AddEventList />
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  listView: {
    flex: 1,
  },
  row: {
    flex: 1,
    marginLeft: 5,
    marginRight: 5,
    marginBottom: 20,
    // http://stackoverflow.com/questions/36605906/what-is-the-row-container-for-a-listview-component
    overflow: 'hidden',
  },
  leftEventImage: {},
  rightTextDescription: {
    flex: 1,
    marginLeft: normalize(5),
  },
  header: {
    backgroundColor: gradientTop,
  },
  headerRow: {
    alignItems: 'center',
    margin: 5,
  },
  headerText: {
    marginRight: 5,
  },
  title: {},
});
