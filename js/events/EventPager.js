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

class EventPager extends React.Component {
  state: {
    dataSource: ViewPager.DataSource,
  };
  props: {
    onFlyerSelected: (x: Event) => ThunkAction,
    search: State,
  };


  constructor(props) {
    super(props);
    var dataSource = new ViewPager.DataSource({
      pageHasChanged: (row1, row2) => row1 !== row2,

    });
    this.state = {
      dataSource,
    };
    this.state = this._getNewState(this.props);
    (this: any).renderEvent = this.renderEvent.bind(this);
  }

  renderEvent(eventData: Object, pageID: number | string) {
    return <FullEventView
      onFlyerSelected={this.props.onFlyerSelected}
      event={new Event(eventData)}
    />;
  }

  _getNewState(props) {
    const results = props.search.results;
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithPages(results ? results.results : []),
    };
    return state;
  }

  componentWillReceiveProps(nextProps) {
    this.setState(this._getNewState(nextProps));
  }

  render() {
    return <ViewPager
      dataSource={this.state.dataSource}
      renderPage={this.renderEvent}
      renderPageIndicator={false}
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
