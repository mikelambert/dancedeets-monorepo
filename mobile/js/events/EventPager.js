/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Dimensions,
  FlatList,
  InteractionManager,
  ScrollView,
  View,
} from 'react-native';
import ViewPager from 'react-native-viewpager';
import { connect } from 'react-redux';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { Event } from 'dancedeets-common/js/events/models';
import type { State } from '../reducers/search';
import { FullEventView } from './uicomponents';
import type { ThunkAction } from '../actions/types';
import { getPosition } from '../util/geo';
import { trackWithEvent } from '../store/track';

class EventPager extends React.Component {
  props: {
    onFlyerSelected: (x: Event) => ThunkAction,
    onEventNavigated: (x: Event) => void,
    selectedEvent: Event,

    // Self-managed props
    search: State,
  };

  state: {
    position: ?Object,
  };

  constructor(props) {
    super(props);
    this.state = {
      position: null,
    };
    this.state = this.getNewState(this.props, null);
    (this: any).renderEvent = this.renderEvent.bind(this);
  }

  componentWillMount() {
    this.loadLocation();
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this.getNewState(nextProps, this.state.position));
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
    return (
      <ScrollView>
        <FullEventView
          onFlyerSelected={this.props.onFlyerSelected}
          event={eventData.event}
          currentPosition={eventData.position}
        />
      </ScrollView>
    );
  }

  render() {
    const position = this.state.position;
    const selectedEvent = this.props.selectedEvent;
    if (!this.props.search.response) {
      console.log('No response!', this.props);
      return null;
    }
    const data = this.props.search.response.results.map(event => ({
      key: event.id,
      event,
      position,
    }));
    // We use react-native-viewpager instead of react-native-carousel,
    // because we only want to render a few pages in the big list
    // (as opposed to a fully rendered pageable/scrollable view, which will scale poorly)
    return (
      <FlatList
        debug
        data={data}
        horizontal
        pagingEnabled
        renderItem={this.renderEvent}
        onChangePage={i =>
          this.props.onEventNavigated(
            this.state.dataSource.getPageData(i).event
          )}
        initialScrollIndex={this.getSelectedPage()}
        getItemLayout={(itemData, index) => {
          /* console.log({
            itemData,
            index,
            length: Dimensions.get('window').width,
            offset: Dimensions.get('window').width * index,
          });*/
          return {
            length: Dimensions.get('window').width,
            offset: Dimensions.get('window').width * index,
            index,
          };
        }}
        windowSize={4}
        initialNumToRender={1}
        maxToRenderPerBatch={2}
        removeClippedSubviews={false}
      />
    );
  }
}
const mapStateToProps = state => ({
  search: state.search,
});
const mapDispatchToProps = dispatch => ({});

export default connect(mapStateToProps, mapDispatchToProps)(EventPager);
