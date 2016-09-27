/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { State } from '../reducers/search';

import React from 'react';
import ViewPager from 'react-native-viewpager';
import { connect } from 'react-redux';
import { Event } from './models';
import { FullEventView } from './uicomponents';
import type { ThunkAction } from '../actions/types';
import {
  getPosition,
} from '../util/geo';

class EventPager extends React.Component {
  state: {
    dataSource: ViewPager.DataSource,
    position: ?Object,
  };
  props: {
    onFlyerSelected: (x: Event) => ThunkAction,
    onEventNavigated: (x: Event) => void,
    search: State,
    selectedEvent: Event,
  };


  constructor(props) {
    super(props);
    var dataSource = new ViewPager.DataSource({
      pageHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = {
      position: null,
      dataSource,
    };
    this.state = this._getNewState(this.props, null);
    (this: any).renderEvent = this.renderEvent.bind(this);
  }

  renderEvent(eventData: Object, pageID: number | string) {
    return <FullEventView
      onFlyerSelected={this.props.onFlyerSelected}
      event={eventData.event}
      currentPosition={eventData.position}
    />;
  }

  _getNewState(props, position) {
    const results = props.search.results;
    let finalResults = [];
    position = position || this.state.position;

    if (results && results.results) {
      const pageIndex = results.results.findIndex((x) => x.id === this.props.selectedEvent.id);
      // If we have an event that's not in the list, it's because we're just displaying this event.
      if (pageIndex === -1) {
        finalResults = [this.props.selectedEvent].map((event) => ({event, position}));
      } else {
        finalResults = results.results.map((event) => ({event, position}));
      }
    }
    const state = {
      ...this.state,
      position: position,
      dataSource: this.state.dataSource.cloneWithPages(finalResults),
    };
    return state;
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this._getNewState(nextProps, this.state.position));
  }

  async loadLocation() {
    const position = await getPosition();
    this.setState(this._getNewState(this.props, position));
  }

  componentWillMount() {
    this.loadLocation();
  }

  getSelectedPage() {
    let initialPage = null;
    if (this.props.search.results && this.props.search.results.results) {
      initialPage = this.props.search.results.results.findIndex((x) => x.id === this.props.selectedEvent.id);
    }
    return initialPage;
  }

  render() {
    // We use react-native-viewpager instead of react-native-carousel,
    // because we only want to render a few pages in the big list
    // (as opposed to a fully rendered pageable/scrollable view, which will scale poorly)
    return <ViewPager
      ref="view_pager"
      dataSource={this.state.dataSource}
      renderPage={this.renderEvent}
      renderPageIndicator={false}
      onChangePage={ (i) => this.props.onEventNavigated(this.state.dataSource.getPageData(i).event) }
      initialPage={this.getSelectedPage()}
    />;
  }
}
const mapStateToProps = (state) => {
  return {
    search: state.search,
  };
};
const mapDispatchToProps = (dispatch) => {
  return {
  };
};
export default EventPager = connect(
  mapStateToProps,
  mapDispatchToProps
)(EventPager);
