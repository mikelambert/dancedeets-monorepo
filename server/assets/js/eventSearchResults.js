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
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import Collapse, { Panel } from 'rc-collapse';
import querystring from 'querystring';
import createBrowserHistory from 'history/createBrowserHistory';
import { performRequest } from 'dancedeets-common/js/api/dancedeets';
import { timeout } from 'dancedeets-common/js/api/timeouts';
import { sortString } from 'dancedeets-common/js/util/sort';
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
import { formatStartDateOnly } from 'dancedeets-common/js/dates';
import { getReactEventSchema } from './eventSchema';
import { Card, ImagePrefix } from './ui';
import { SquareEventFlyer } from './eventCommon';
import GoogleAd from './googleAd';
import { SearchBox } from './resultsCommon';

require('slick-carousel/slick/slick.css');
require('slick-carousel/slick/slick-theme.css');
require('../css/slick.scss');
require('../css/rc-collapse.scss');
require('react-tabs/style/react-tabs.scss');

type SearchQuery = Object;

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

class _EventDescription extends React.Component {
  props: {
    event: SearchEvent,
    indexingBot?: boolean,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    const event = this.props.event;
    const keywords = [...event.annotations.categories];
    if (this.props.indexingBot) {
      keywords.push(...event.annotations.keywords);
    }

    const startTime = moment(event.start_time).toDate();
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
          <ImagePrefix iconName="clock-o">
            {formatStartDateOnly(startTime, this.props.intl)}
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
const EventDescription = injectIntl(_EventDescription);

class HorizontalEvent extends React.Component {
  props: {
    event: SearchEvent,
    lazyLoad: boolean,
  };

  render() {
    const event = this.props.event;
    return (
      <div>
        <div className="grey-top-border">{' '}</div>
        <div
          style={{
            paddingTop: 10,
            paddingBottom: 10,
          }}
        >
          <table>
            <tbody>
              <tr>
                <td style={{ verticalAlign: 'top' }}>
                  <div className="event-image">
                    <SquareEventFlyer
                      event={this.props.event}
                      lazyLoad={this.props.lazyLoad}
                    />
                  </div>
                </td>
                <td style={{ verticalAlign: 'top' }}>
                  <div className="event-description">
                    <EventDescription event={this.props.event} />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
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
        <Sticky>
          <div className="bold" style={{ backgroundColor: 'white' }}>
            {header}
          </div>
        </Sticky>
      );
      resultItems.push(...renderedEvents);
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
        <Spinner name="circle" color="black" fadeIn="none" />
      </div>
    );
  }
}
const Loading = injectIntl(_Loading);

class ResultsList extends React.Component {
  props: {
    response: NewSearchResponse,
  };

  render() {
    const resultEvents = this.props.response.results.map(
      eventData => new SearchEvent(eventData)
    );
    const featuredInfos = (this.props.response.featuredInfos || [])
      .map(x => ({ ...x, event: new Event(x.event) }));

    const now = moment();
    const eventPanels = [];
    let eventCount = null;
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

    let featuredPanel = null;
    if (featuredInfos.length) {
      featuredPanel = (
        <Panel key="featured" header="Featured Event">
          <FeaturedEvents events={featuredInfos.map(x => x.event)} />
        </Panel>
      );
    }

    let oneboxPanel = null;
    if (this.props.response.onebox_links.length) {
      oneboxPanel = (
        <Panel key="onebox" header="Related Links">
          <OneboxLinks links={this.props.response.onebox_links} />
        </Panel>
      );
    }
    const defaultKeys = ['featured', 'onebox', 'currentEvents', 'futureEvents'];

    return (
      <Collapse
        defaultActiveKey={defaultKeys}
        style={{ backgroundColor: 'white' }}
      >
        {featuredPanel}
        {oneboxPanel}
        {eventPanels}
        {ExecutionEnvironment.canUseDOM
          ? null
          : resultEvents.map(getReactEventSchema)}
      </Collapse>
    );
  }
}

export async function search(
  location: string,
  keywords: string,
  startDate: string,
  endDate: string
) {
  const response = await timeout(
    10000,
    performRequest(
      'search',
      {
        location,
        keywords,
        start: startDate,
        end: endDate,
        skip_people: 1, // We don't need to auto-fetch people, since it is on a different tab
      },
      {},
      '2.0'
    )
  );
  response.featuredInfos = response.featuredInfos.map(x => ({
    ...x,
    event: new SearchEvent(x.event),
  }));
  response.results = response.results.map(x => new SearchEvent(x));
  response.results = sortString(response.results, resultEvent =>
    moment(resultEvent.start_time).toISOString()
  );
  return response;
}

class _PeopleList extends React.Component {
  props: {
    response: NewSearchResponse,
    categoryOrder: Array<string>,

    // Self-managed props
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

  render() {
    let adminContents = null;
    let attendeeContents = null;
    if (this.state.people) {
      const admins = this.state.people.ADMIN;
      const attendees = this.state.people.ATTENDEE;
      if (!admins && !attendees) {
        return (
          <CallbackOnRender callback={this.loadPeopleIfNeeded}>
            <Loading />
          </CallbackOnRender>
        );
      } else {
        adminContents = admins
          ? <PersonList
              title={this.props.intl.formatMessage(messages.nearbyPromoters)}
              subtitle={this.props.intl.formatMessage(
                messages.nearbyPromotersMessage
              )}
              people={admins}
              categoryOrder={this.props.categoryOrder}
            />
          : null;
        attendeeContents = attendees
          ? <PersonList
              title={this.props.intl.formatMessage(messages.nearbyDancers)}
              subtitle={this.props.intl.formatMessage(
                messages.nearbyDancersMessage
              )}
              people={attendees}
              categoryOrder={this.props.categoryOrder}
            />
          : null;
      }
    } else if (this.state.failed) {
      adminContents = <span>Error Loading People</span>;
      attendeeContents = <span>Error Loading People</span>;
    } else {
      adminContents = null;
      attendeeContents = null;
    }

    const adminsDiv = adminContents
      ? <div className="col-sm-6">{adminContents}</div>
      : null;
    const attendeesDiv = attendeeContents
      ? <div className="col-sm-6">{attendeeContents}</div>
      : null;
    return <div className="row">{adminsDiv}{attendeesDiv}</div>;
  }
}
const PeopleList = injectIntl(_PeopleList);

class ResultTabs extends React.Component {
  props: {
    response: NewSearchResponse,
    query: SearchQuery,
    categoryOrder: Array<string>,
  };

  render() {
    const query = querystring.stringify(this.props.query);
    const calendarUrl = `/calendar/iframe/?${query}`;
    return (
      <Tabs>
        <TabList>
          <Tab>Events List</Tab>
          <Tab>Events Calendar</Tab>
          <Tab>People</Tab>
        </TabList>

        <TabPanel>
          <ResultsList response={this.props.response} />
        </TabPanel>
        <TabPanel>
          <iframe src={calendarUrl} />
        </TabPanel>
        <TabPanel>
          <PeopleList
            response={this.props.response}
            categoryOrder={this.props.categoryOrder}
          />
        </TabPanel>
      </Tabs>
    );
  }
}

class ResultsPage extends React.Component {
  props: {
    response: NewSearchResponse,
    categoryOrder: Array<string>,
    query: SearchQuery,
  };

  state: {
    response: NewSearchResponse,
  };

  constructor(props) {
    super(props);
    this.state = { response: this.props.response };
    (this: any).onNewSearch = this.onNewSearch.bind(this);
  }

  async onNewSearch(form) {
    const query = querystring.stringify(form);
    const history = createBrowserHistory();
    history.replace(`/?${query}`);

    const response = await search(
      form.location,
      form.keywords,
      form.start,
      form.end
    );
    this.setState({ response });
  }

  render() {
    const query = querystring.stringify(this.props.query);
    const calendarUrl = `/events/relevant?calendar=1&${query}`;
    return (
      <div className="col-xs-12">
        <SearchBox query={this.props.query} onNewSearch={this.onNewSearch} />

        <ResultTabs
          query={this.props.query}
          response={this.state.response}
          categoryOrder={this.props.categoryOrder}
        />
      </div>
    );
  }
}

export default intlWeb(ResultsPage);
