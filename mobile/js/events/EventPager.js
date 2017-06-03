/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Dimensions, InteractionManager, View } from 'react-native';
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
    dataSource: ViewPager.DataSource,
    position: ?Object,
    loadInProgress: boolean,
  };

  constructor(props) {
    super(props);
    const dataSource = new ViewPager.DataSource({
      pageHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = {
      position: null,
      dataSource,
      loadInProgress: true,
    };
    this.state = this.getNewState(this.props, null);
    (this: any).renderEvent = this.renderEvent.bind(this);
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

  getNewState(props, position) {
    const results = props.search.response;
    let finalResults = [];
    const newPosition = position || this.state.position;

    const selectedEvent = this.props.selectedEvent;

    if (results && results.results) {
      const pageIndex = results.results.findIndex(
        x => x.id === selectedEvent.id
      );
      if (pageIndex !== -1) {
        finalResults = results.results.map(event => ({ event, newPosition }));
      }
    }
    // If we have an event that's not in the list, it's because we're just displaying this event.
    if (!finalResults.length) {
      finalResults = [selectedEvent].map(event => ({
        event,
        newPosition,
      }));
    }
    const state = {
      ...this.state,
      position: newPosition,
      dataSource: this.state.dataSource.cloneWithPages(finalResults),
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

  renderEvent(eventData: Object, pageID: number | string) {
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
      <FullEventView
        onFlyerSelected={this.props.onFlyerSelected}
        event={eventData.event}
        currentPosition={eventData.position}
      />
    );
  }

  render() {
    // We only show the "first" element in the dataSource, until we've finished our animation in
    // This should help speed up the event-view transition.
    let dataSource = this.state.dataSource;
    if (this.state.loadInProgress) {
      const selectedIndex = this.getSelectedPage();
      if (selectedIndex == null) {
        return null;
      }
      const selectedPage = dataSource.getPageData(selectedIndex);
      const tempData = Array.from(new Array(dataSource.getPageCount()));
      tempData[selectedIndex] = selectedPage;
      dataSource = this.state.dataSource.cloneWithPages(tempData);
    }

    // We use react-native-viewpager instead of react-native-carousel,
    // because we only want to render a few pages in the big list
    // (as opposed to a fully rendered pageable/scrollable view, which will scale poorly)
    return (
      <ViewPager
        dataSource={dataSource}
        renderPage={this.renderEvent}
        renderPageIndicator={false}
        onChangePage={i =>
          this.props.onEventNavigated(
            this.state.dataSource.getPageData(i).event
          )}
        initialPage={this.getSelectedPage()}
      />
    );
  }
}
const mapStateToProps = state => ({
  search: state.search,
});
const mapDispatchToProps = dispatch => ({});

export default connect(mapStateToProps, mapDispatchToProps)(EventPager);
