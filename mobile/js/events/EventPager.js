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
    search: State,

    navigation: NavigationScreenProp<NavigationRoute, NavigationAction>,
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
    (this: any).onEventNavigated = this.onEventNavigated.bind(this);
    (this: any).onFlyerSelected = this.onFlyerSelected.bind(this);
  }

  componentWillMount() {
    this.loadLocation();
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this.getNewState(nextProps, this.state.position));
  }

  onEventNavigated(event) {
    console.log(event);
    trackWithEvent('View Event', event);
    // TODO(navigation) : should this swap instead ofnavigate?
    this.props.navigation.setParams({ event });
  }

  onFlyerSelected() {
    const event = this.getEvent();
    trackWithEvent('View Flyer', event);
    // TODO(navigation): Should we pass in an i18n'ed title?
    this.props.navigation.navigate('FlyerView', { event });
  }

  getEvent(): any {
    return this.props.navigation.state.params.event;
  }

  getNewState(props, position) {
    const results = props.search.response;
    let finalResults = [];
    const newPosition = position || this.state.position;

    const selectedEvent = this.getEvent();

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
    const selectedEvent = this.getEvent();

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
        onFlyerSelected={this.onFlyerSelected}
        event={eventData.event}
        currentPosition={eventData.position}
      />
    );
  }

  componentDidMount() {
    InteractionManager.runAfterInteractions(() => {
      this.setState({ loadInProgress: false });
    });
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
          this.onEventNavigated(
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
