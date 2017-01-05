/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import Masonry from 'react-masonry-component';
import {
  SearchEvent,
} from 'dancedeets-common/js/events/models';
import type {
  NewSearchResults,
} from 'dancedeets-common/js/events/search';
import {
  VerticalEvent,
} from './eventSearchResults';

class EventList extends React.Component {
  props: {
    results: NewSearchResults;
  }

  render() {
    const resultEvents = this.props.results.results.map(eventData => new SearchEvent(eventData));

    const resultItems = [];
    resultEvents.forEach((event, index) => {
      resultItems.push(<VerticalEvent key={event.id} event={event} />);
    });

    return (<div>
      <div style={{ width: '100%', padding: 10 }}>
        <Masonry>
          {resultItems}
        </Masonry>
      </div>
    </div>);
  }
}

export default EventList;
