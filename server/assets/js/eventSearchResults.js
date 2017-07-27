/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import url from 'url';
import FormatText from 'react-format-text';
import moment from 'moment';
import ExecutionEnvironment from 'exenv';
import upperFirst from 'lodash/upperFirst';
import { injectIntl, intlShape } from 'react-intl';
import { StickyContainer, Sticky } from 'react-sticky';
import Masonry from 'react-masonry-component';
import Slider from 'react-slick';
import Spinner from 'react-spinkit';
import Collapse, { Panel } from 'rc-collapse';
import querystring from 'querystring';
import { intlWeb } from 'dancedeets-common/js/intl';
import type { Cover, JSONObject } from 'dancedeets-common/js/events/models';
import { messages } from 'dancedeets-common/js/events/people';
import {
  BaseEvent,
  Event,
  SearchEvent,
} from 'dancedeets-common/js/events/models';
import type {
  NewSearchResponse,
  Onebox,
  PeopleListing,
  StylePersonLookup,
} from 'dancedeets-common/js/events/search';
import {
  formatAttending,
  groupEventsByStartDate,
} from 'dancedeets-common/js/events/helpers';
import { getReactEventSchema } from './eventSchema';
import { Card, ImagePrefix, wantsWindowSizes } from './ui';
import type { windowProps } from './ui';
import { SquareEventFlyer } from './eventCommon';
import GoogleAd from './googleAd';
import { SearchBox } from './resultsCommon';

require('slick-carousel/slick/slick.css');
require('slick-carousel/slick/slick-theme.css');
require('../css/slick.scss');
require('../css/rc-collapse.scss');

function insertEvery<T>(
  array: Array<T>,
  insertion: (origIndex: number) => T,
  n: number
) {
  return array.reduce(
    (newArray, member, i) =>
      i % n === n - 1 // If it's our n'th element
        ? newArray.concat(member, insertion(i))
        : newArray.concat(member),
    []
  );
}

export class HorizontalEventFlyer extends React.Component {
  props: {
    event: BaseEvent,
  };

  generateCroppedCover(picture: Cover, width: number, height: number) {
    const parsedSource = url.parse(picture.source, true);
    parsedSource.query = { ...parsedSource.query, width, height };
    const newSourceUrl = url.format(parsedSource);

    return {
      source: newSourceUrl,
      width,
      height,
    };
  }

  render() {
    const event = this.props.event;
    const picture = event.picture;
    if (!picture) {
      return null;
    }
    const width = 800;
    const height = 400;

    const scaledHeight = '50'; // height == width * 50%

    const croppedPicture = this.generateCroppedCover(picture, width, height);
    const imageTag = (
      <div
        style={{
          height: 0,
          paddingBottom: `${scaledHeight}%`,
        }}
      >
        <img
          role="presentation"
          src={croppedPicture.source}
          style={{
            width: '100%',
          }}
          className="no-border"
        />
      </div>
    );
    return (
      <a className="link-event-flyer" href={event.getUrl()}>
        {imageTag}
      </a>
    );
  }
}

class EventDescription extends React.Component {
  props: {
    event: SearchEvent,
    indexingBot?: boolean,
  };

  render() {
    const event = this.props.event;
    const keywords = [...event.annotations.categories];
    if (this.props.indexingBot) {
      keywords.push(...event.annotations.keywords);
    }

    return (
      <div>
        <h3 className="event-title">
          <a href={event.getUrl()}>
            <span>{event.name}</span>
          </a>
        </h3>
        <div style={{ marginTop: 10 }}>
          <ImagePrefix
            icon={require('../img/categories-white.png')} // eslint-disable-line global-require
          >
            {keywords.join(', ')}
          </ImagePrefix>
        </div>
        <div>
          <ImagePrefix iconName="map-marker">
            <div>{event.venue.name}</div>
            <FormatText>{event.venue.cityStateCountry()}</FormatText>
          </ImagePrefix>
        </div>
      </div>
    );
  }
}

class HorizontalEvent extends React.Component {
  props: {
    event: SearchEvent,
    lazyLoad: boolean,
  };

  render() {
    const event = this.props.event;
    return (
      <div
        style={{
          float: 'left',
          borderColor: '#e9ebee',
          borderWidth: 1,
          borderStyle: 'solid',
          width: '50%', // TODO FIXME1
          margin: 10,
        }}
      >
        <table>
          <tbody>
            <tr>
              <td>
                <div className="event-image">
                  <SquareEventFlyer
                    event={this.props.event}
                    lazyLoad={this.props.lazyLoad}
                  />
                </div>
              </td>
              <td>
                <div className="event-description">
                  <EventDescription event={this.props.event} />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }
}

class VerticalEvent extends React.Component {
  props: {
    event: SearchEvent,
  };

  render() {
    const event = this.props.event;
    return (
      <Card
        style={{
          display: 'inline-block',
          width: 200,
          verticalAlign: 'top',
        }}
      >
        <SquareEventFlyer event={event} />
        <h3 className="event-title" style={{ marginTop: 10 }}>
          <a href={event.getUrl()}>
            <span>{event.name}</span>
          </a>
        </h3>
        <div className="event-city">
          <div>{event.venue.name}</div>
          <FormatText>{event.venue.cityStateCountry()}</FormatText>
        </div>
      </Card>
    );
  }
}

class FeaturedEvent extends React.Component {
  props: {
    event: BaseEvent,
  };

  render() {
    const event = this.props.event;
    return (
      <Card>
        <HorizontalEventFlyer event={event} />
        <h3 className="event-title" style={{ marginTop: 10 }}>
          <a href={event.getUrl()}>
            <span>{event.name}</span>
          </a>
        </h3>
      </Card>
    );
  }
}

class FeaturedEvents extends React.Component {
  props: {
    events: Array<BaseEvent>,
  };

  render() {
    if (!this.props.events.length) {
      return null;
    }

    const resultItems = [];
    const imageEvents = this.props.events.filter(x => x.picture);
    imageEvents.forEach((event, index) => {
      // Slider requires children to be actual HTML elements.
      resultItems.push(
        <div key={event.id}>
          <FeaturedEvent event={event} />
        </div>
      );
    });

    const results = resultItems.length > 1
      ? <Slider autoplay dots>{resultItems}</Slider>
      : resultItems;

    return <div style={{ width: '100%', padding: 10 }}>{results}</div>;
  }
}

class CurrentEvents extends React.Component {
  props: {
    events: Array<SearchEvent>,
  };

  render() {
    if (!this.props.events.length) {
      return null;
    }

    const resultItems = [];
    this.props.events.forEach((event, index) => {
      resultItems.push(<VerticalEvent key={event.id} event={event} />);
    });

    return (
      <div style={{ width: '100%', padding: 10 }}>
        <Masonry>
          {resultItems}
        </Masonry>
      </div>
    );
  }
}

class _EventsList extends React.Component {
  props: {
    events: Array<SearchEvent>,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    const resultItems = [];
    let overallEventIndex = 0;
    groupEventsByStartDate(
      this.props.intl,
      this.props.events,
      x => x.start_time
    ).forEach(({ header, events }) => {
      const renderedEvents = events.map((event, index) =>
        <HorizontalEvent
          key={event.id}
          event={event}
          lazyLoad={overallEventIndex + index > 8}
        />
      );

      resultItems.push(
        <Card key={header} className="clearfix" style={{ padding: 0 }}>
          <div className="card-header bold">{header}</div>
          {renderedEvents}
        </Card>
      );
      /* className="day-header"
          style={{
            marginTop: '30px',
            marginBottom: '10px',
            borderBottom: '1px solid white',
          }}
        >
*/
      overallEventIndex += events.length;
    });

    // Make some arbitrary determination on what kinds of ads to use.
    const lastEvent = this.props.events[0];
    const adType = lastEvent
      ? Number(lastEvent.id[lastEvent.id.length - 1]) % 3
      : null;
    function adItem(origIndex) {
      switch (adType) {
        case 0:
          return (
            <GoogleAd
              key={`ad-${origIndex}`}
              style={{ display: 'block' }}
              data-ad-format="fluid"
              data-ad-layout="image-side"
              data-ad-layout-key="-ef+o-2p-9x+sk"
              data-ad-slot="7215991777"
            />
          );
        case 1:
          return (
            <GoogleAd
              key={`ad-${origIndex}`}
              style={{ display: 'block' }}
              data-ad-format="auto"
              data-ad-slot="8358307776"
            />
          );
        case 2:
          return (
            <GoogleAd
              key={`ad-${origIndex}`}
              style={{ display: 'inline-block', width: '100%', height: 100 }}
              data-ad-format="auto"
              data-ad-slot="6502811377"
            />
          );
        default:
          return null;
      }
    }
    const monetizedResultItems = insertEvery(resultItems, adItem, 10);

    return (
      <StickyContainer>
        {monetizedResultItems}
      </StickyContainer>
    );
  }
}
const EventsList = injectIntl(_EventsList);

class _OneboxLinks extends React.Component {
  props: {
    links: Array<Onebox>,
  };

  render() {
    if (!this.props.links.length) {
      return null;
    }
    const oneboxList = this.props.links.map(onebox =>
      <li key={onebox.url}>
        <a className="link-onebox" href={onebox.url}>{onebox.title}</a>
      </li>
    );

    return (
      <div>
        <ul>{oneboxList}</ul>
      </div>
    );
  }
}
const OneboxLinks = injectIntl(_OneboxLinks);

class PersonList extends React.Component {
  props: {
    title: string,
    subtitle: string,
    categoryOrder: Array<string>,
    people: StylePersonLookup,
  };

  state: {
    category: string,
  };

  constructor(props) {
    super(props);
    this.state = {
      category: '',
    };
  }

  render() {
    if (!this.props.people[this.state.category]) {
      console.error(
        'PersonList: Found empty people for category:',
        this.state.category,
        'in people object:',
        this.props.people
      );
      return null;
    }
    const peopleList = this.props.people[this.state.category].slice(0, 10);
    const categories = this.props.categoryOrder.filter(
      x => x === '' || this.props.people[x]
    );

    const selector = (
      <form className="form-inline" style={{ padding: 5 }}>
        <b>{this.props.title} by Style: </b>
        <select
          className="form-control form-inline"
          onChange={e => this.setState({ category: e.target.value })}
        >
          {categories.map(x =>
            <option key={x} value={x}>{x || 'Overall'}</option>
          )}
        </select>
        <p><i>{this.props.subtitle}:</i></p>
      </form>
    );
    return (
      <div>
        {selector}
        <ul>
          {peopleList.map(x =>
            <li key={x.id}>
              <a href={`https://www.facebook.com/${x.id}`}>{x.name}</a>
            </li>
          )}
        </ul>
      </div>
    );
  }
}

class CallbackOnRender extends React.Component {
  props: {
    callback: () => void | Promise<void>,
    children?: React.Element<*>,
  };

  render() {
    if (this.props.callback) {
      this.props.callback();
    }
    return this.props.children;
  }
}

class _Loading extends React.Component {
  props: {
    // Self-managed props
    intl: intlShape,
  };

  render() {
    return (
      <div>
        <Spinner name="circle" color="white" noFadeIn />
      </div>
    );
  }
}
const Loading = injectIntl(_Loading);

class _ResultsList extends React.Component {
  props: {
    response: NewSearchResponse,
    past: boolean,
    showPeople: boolean,
    categoryOrder: Array<string>,

    // Self-managed props
    window: windowProps,
    intl: intlShape,
  };

  state: {
    people: PeopleListing,
    failed: boolean,
  };

  _loadingPeople: boolean;

  constructor(props) {
    super(props);
    this.state = { people: props.response.people, failed: false };
    (this: any).loadPeopleIfNeeded = this.loadPeopleIfNeeded.bind(this);
  }

  async loadPeopleIfNeeded() {
    if (
      // If we're rendering on the server, ignore loading anything
      !ExecutionEnvironment.canUseDOM ||
      // This search area was too large, and we didn't want to do a people calculation
      !this.state.people ||
      // We already have some people loaded, no need to load them again
      Object.keys(this.state.people).length ||
      // We have an in-progress pending load
      this._loadingPeople
    ) {
      return;
    }
    try {
      this._loadingPeople = true;
      const formattedArgs = querystring.stringify({
        location: this.props.response.query.location,
        locale: this.props.response.query.locale,
      });

      const result = await fetch(`/api/v2.0/people?${formattedArgs}`);
      const resultJson = await result.json();
      this.setState({ people: resultJson.people });
    } catch (e) {
      console.error(e);
      this.setState({ failed: true });
    }
    this._loadingPeople = false;
  }

  renderPeoplePanel() {
    let peoplePanel = [];
    let adminContents = null;
    let attendeeContents = null;
    if (this.state.people) {
      const admins = this.state.people.ADMIN;
      const attendees = this.state.people.ATTENDEE;
      adminContents = admins
        ? <PersonList
            title={this.props.intl.formatMessage(messages.nearbyPromoters)}
            subtitle={this.props.intl.formatMessage(
              messages.nearbyPromotersMessage
            )}
            people={admins}
            categoryOrder={this.props.categoryOrder}
          />
        : <CallbackOnRender callback={this.loadPeopleIfNeeded}>
            <Loading />
          </CallbackOnRender>;
      attendeeContents = attendees
        ? <PersonList
            title={this.props.intl.formatMessage(messages.nearbyDancers)}
            subtitle={this.props.intl.formatMessage(
              messages.nearbyDancersMessage
            )}
            people={attendees}
            categoryOrder={this.props.categoryOrder}
          />
        : <CallbackOnRender callback={this.loadPeopleIfNeeded}>
            <Loading />
          </CallbackOnRender>;
    } else if (this.state.failed) {
      adminContents = <span>Error Loading People</span>;
      attendeeContents = <span>Error Loading People</span>;
    } else {
      adminContents = null;
      attendeeContents = null;
    }

    if (this.props.window && this.props.window.width < 768) {
      if (adminContents) {
        peoplePanel.push(
          <Panel
            key="people1"
            header={this.props.intl.formatMessage(messages.nearbyPromoters)}
            onItemClick={this.loadPeopleIfNeeded}
          >
            {adminContents}
          </Panel>
        );
      }
      if (attendeeContents) {
        peoplePanel.push(
          <Panel
            key="people2"
            header={this.props.intl.formatMessage(messages.nearbyDancers)}
            onItemClick={this.loadPeopleIfNeeded}
          >
            {attendeeContents}
          </Panel>
        );
      }
    } else {
      const adminsDiv = adminContents
        ? <div className="col-sm-6">{adminContents}</div>
        : null;
      const attendeesDiv = attendeeContents
        ? <div className="col-sm-6">{attendeeContents}</div>
        : null;
      peoplePanel = (
        <Panel
          key="people"
          header="Nearby Promoters & Dancers"
          onItemClick={this.loadPeopleIfNeeded}
        >
          <div className="row">{adminsDiv}{attendeesDiv}</div>
        </Panel>
      );
    }

    return peoplePanel;
  }

  render() {
    const resultEvents = this.props.response.results.map(
      eventData => new SearchEvent(eventData)
    );
    const featuredInfos = (this.props.response.featuredInfos || [])
      .map(x => ({ ...x, event: new Event(x.event) }));

    const now = moment();
    const eventPanels = [];
    let eventCount = null;
    if (this.props.past) {
      const pastEvents = resultEvents.filter(
        event => moment(event.start_time) < now
      );
      if (pastEvents.length) {
        eventPanels.push(
          <Panel key="pastEvents" header="Past Events">
            <EventsList events={pastEvents} />
          </Panel>
        );
      }
      eventCount = pastEvents.length;
    } else {
      // DEBUG CODE:
      // const currentEvents = resultEvents.filter(event => moment(event.start_time) > now);
      const currentEvents = resultEvents.filter(
        event => moment(event.start_time) < now && moment(event.end_time) > now
      );
      const futureEvents = resultEvents.filter(
        event => moment(event.start_time) > now
      );
      if (currentEvents.length) {
        eventPanels.push(
          <Panel key="currentEvents" header="Events Happening Now">
            <CurrentEvents events={currentEvents} />
          </Panel>
        );
      }
      if (futureEvents.length) {
        eventPanels.push(
          <Panel key="futureEvents" header="Upcoming Events">
            <EventsList events={futureEvents} />
          </Panel>
        );
      }
      eventCount = currentEvents.length + futureEvents.length;
    }

    let featuredPanel = null;
    if (featuredInfos.length) {
      featuredPanel = (
        <Panel key="featured" header="Featured Event">
          <FeaturedEvents events={featuredInfos.map(x => x.event)} />
        </Panel>
      );
    }
    const peoplePanel = this.renderPeoplePanel();

    let oneboxPanel = null;
    if (this.props.response.onebox_links.length) {
      oneboxPanel = (
        <Panel key="onebox" header="Related Links">
          <OneboxLinks links={this.props.response.onebox_links} />
        </Panel>
      );
    }
    const defaultKeys = [
      'featured',
      'onebox',
      'pastEvents',
      'currentEvents',
      'futureEvents',
    ];
    if (this.props.showPeople) {
      defaultKeys.push('people', 'people1', 'people2');
    }

    return (
      <Collapse defaultActiveKey={defaultKeys}>
        {featuredPanel}
        {peoplePanel}
        {oneboxPanel}
        {eventPanels}
        {ExecutionEnvironment.canUseDOM
          ? null
          : resultEvents.map(getReactEventSchema)}
      </Collapse>
    );
  }
}
const ResultsList = wantsWindowSizes(injectIntl(_ResultsList));

class ResultsPage extends React.Component {
  props: {
    response: NewSearchResponse,
    past: boolean,
    showPeople: boolean,
    categoryOrder: Array<string>,
    query: Object,
  };

  render() {
    const query = querystring.stringify(this.props.query);
    const calendarUrl = `/events/relevant?calendar=1&${query}`;
    return (
      <div className="col-md-9">
        <SearchBox query={this.props.query} />

        <div style={{ textAlign: 'right' }}>
          <a href={calendarUrl}>
            <ImagePrefix iconName="calendar">View on Calendar</ImagePrefix>
          </a>
        </div>
        <ResultsList
          response={this.props.response}
          past={this.props.past}
          showPeople={this.props.showPeople}
          categoryOrder={this.props.categoryOrder}
        />
      </div>
    );
  }
}

export default intlWeb(ResultsPage);
