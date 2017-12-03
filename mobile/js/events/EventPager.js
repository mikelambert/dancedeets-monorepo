/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { Dimensions, FlatList, InteractionManager, View } from 'react-native';
import { connect } from 'react-redux';
import { Event } from 'dancedeets-common/js/events/models';
import type { State } from '../reducers/search';
import { LoadingEventView, FullEventView } from './uicomponents';
import type { ThunkAction } from '../actions/types';
import { getPosition } from '../util/geo';
import { loadEvent } from '../actions/loadedEvents';

class EventPager extends React.Component<
  {
    onFlyerSelected: (x: Event) => ThunkAction,
    onEventNavigated: (x: SearchEvent) => void,
    selectedEvent: Event,

    // Self-managed props
    search: State,
  },
  {
    position: ?Object,
    loadInProgress: boolean,
  }
> {
  constructor(props) {
    super(props);
    this.state = {
      position: null,
      loadInProgress: true,
    };
    this.state = this.getNewState(this.props, null);
    (this: any).renderEvent = this.renderEvent.bind(this);
    (this: any).onScrollEnd = this.onScrollEnd.bind(this);
  }

  componentWillMount() {
    this.loadLocation();
  }

  componentDidMount() {
    InteractionManager.runAfterInteractions(() => {
      this.setState({ loadInProgress: false });
    });
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this.getNewState(nextProps, this.state.position));
  }

  // From https://stackoverflow.com/questions/43370807/react-native-get-current-page-in-flatlist-when-using-pagingenabled
  onScrollEnd(e) {
    const contentOffset = e.nativeEvent.contentOffset;
    const viewSize = e.nativeEvent.layoutMeasurement;

    const results = this.props.search.response.results;

    // Divide the horizontal offset by the width of the view to see which page is visible
    const pageIndex = Math.floor(contentOffset.x / viewSize.width);
    const event = results[pageIndex];
    if (event == null) {
      console.error('Found empty event for onEventNavigated.');
      console.error({
        pageIndex,
        contentOffsetX: contentOffset.x,
        viewSizeWidth: viewSize.width,
      });
      if (results) {
        console.error(`Response results has ${results.length} elements`);
      } else {
        const response = this.props.search.response;
        console.error(`Response is non-empty? ${String(response != null)}`);
        console.error(`Response error: ${response.error}`);
        console.error(`Response errorString: ${response.errorString}`);
      }
    }
    return this.props.onEventNavigated(event);
  }

  getNewState(props, oldPosition) {
    const position = oldPosition || this.state.position;
    const state = {
      ...this.state,
      position,
    };
    return state;
  }

  getSelectedPage() {
    const selectedEvent = this.props.selectedEvent;

    let initialPage = null;
    if (this.props.search.response && this.props.search.response.results) {
      initialPage = this.props.search.response.results.findIndex(
        x => x.id === selectedEvent.id
      );
    }
    return initialPage;
  }

  getItemLayout(itemData, index) {
    return {
      length: Dimensions.get('window').width,
      offset: Dimensions.get('window').width * index,
      index,
    };
  }

  async loadLocation() {
    const position = await getPosition();
    this.setState(this.getNewState(this.props, position));
  }

  renderEvent(info) {
    const eventData = info.item;
    // This can happen when we're animating in,
    // and have passed in some almost-entirely-empty dataSource.
    // We don't want to render anything for the hidden pages
    // until after the animation has completed
    // (and the user won't notice any jank)
    if (eventData == null) {
      // We don't return null, because we need an element which will
      // take up exactly the same amount of space as the full element.
      // This ensures the one *actually* rendered element in the ViewPager
      // gets allocated the correct sized layout (and not 2-3x larger).
      const width = Dimensions.get('window').width;
      return <View style={{ width }} />;
    }
    if (eventData.event) {
      return (
        <FullEventView
          onFlyerSelected={this.props.onFlyerSelected}
          event={eventData.event}
          currentPosition={eventData.position}
        />
      );
    } else if (eventData.searchEvent) {
      const loadedEventData = this.props.loadedEvents[eventData.searchEvent.id];
      if (!loadedEventData) {
        this.props.loadEvent(eventData.searchEvent.id);
      }
      return (
        <LoadingEventView
          onFlyerSelected={this.props.onFlyerSelected}
          event={eventData.searchEvent}
          currentPosition={eventData.position}
        />
      );
    }
  }

  render() {
    const position = this.state.position;
    if (!this.props.search.response) {
      if (this.props.selectedEvent) {
        // Navigation to a single event URL. Just render the singular event.
        return this.renderEvent({
          item: {
            event: this.props.selectedEvent,
            position: this.state.position,
          },
        });
      } else {
        console.log('No response!', this.props);
        return null;
      }
    }
    console.log(this.props.loadedEvents);
    const data = this.props.search.response.results.map(searchEvent => {
      const loadedEventState = this.props.loadedEvents[searchEvent.id];
      const event = loadedEventState ? loadedEventState.event : null;
      console.log(searchEvent.id, loadedEventState, event);
      return {
        key: searchEvent.id,
        event,
        searchEvent,
        position,
      };
    });
    console.log(data);
    return (
      <FlatList
        data={data}
        horizontal
        pagingEnabled
        renderItem={this.renderEvent}
        onMomentumScrollEnd={this.onScrollEnd}
        initialScrollIndex={this.getSelectedPage()}
        getItemLayout={this.getItemLayout}
        windowSize={5}
        initialNumToRender={1}
        maxToRenderPerBatch={2}
        removeClippedSubviews={false}
        showsHorizontalScrollIndicator={false}
      />
    );
  }
}
const mapStateToProps = state => ({
  search: state.search,
  loadedEvents: state.loadedEvents,
});
const mapDispatchToProps = dispatch => ({
  loadEvent: async eventId => {
    console.log('a');
    await dispatch(loadEvent(eventId));
    console.log('b');
  },
});

export default connect(mapStateToProps, mapDispatchToProps)(EventPager);
