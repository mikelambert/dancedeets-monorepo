/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import FormatText from 'react-format-text';
import moment from 'moment';
import ExecutionEnvironment from 'exenv';
import isEqual from 'lodash/isEqual';
import { injectIntl, intlShape } from 'react-intl';
import Slider from 'react-slick';
import Spinner from 'react-spinkit';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import Waypoint from 'react-waypoint';
import querystring from 'querystring';
import createBrowserHistory from 'history/createBrowserHistory';
import { performRequest as realPerformRequest } from 'dancedeets-common/js/api/dancedeets';
import { sortNumber } from 'dancedeets-common/js/util/sort';
import { intlWeb } from 'dancedeets-common/js/intl';
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
import { groupEventsByStartDate } from 'dancedeets-common/js/events/helpers';
import { formatStartDateOnly } from 'dancedeets-common/js/dates';
import { cdnBaseUrl } from 'dancedeets-common/js/util/url';
import { JsonSchema } from './schema';
import { getEventSchema } from './schema/event';
import { getBreadcrumbsForSearch } from './schema/breadcrumbs';
import { Card, ImagePrefix, wantsWindowSizes } from './ui';
import type { windowProps } from './ui';
import { SquareEventFlyer } from './eventCommon';
import GoogleAd from './googleAd';
import { canonicalizeQuery, SearchBox, CalendarRatio } from './resultsCommon';
import {
  MultiSelectList,
  generateUniformState,
  getSelected,
} from './MultiSelectList';
import type { MultiSelectState } from './MultiSelectList';

type FormSearchQuery = {
  location?: string, // eslint-disable-line react/no-unused-prop-types
  keywords?: string, // eslint-disable-line react/no-unused-prop-types
  start?: string, // eslint-disable-line react/no-unused-prop-types
  end?: string, // eslint-disable-line react/no-unused-prop-types
};

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

async function performRequest(
  path: string,
  args: Object,
  postArgs: ?Object | null
): Promise<Object> {
  return await realPerformRequest(window.fetch, path, args, postArgs, '2.0');
}

export class HorizontalEventFlyer extends React.Component {
  props: {
    event: BaseEvent,
  };

  render() {
    const fbDims = { width: 500, height: 262 };
    const event = this.props.event;
    const width = 700;
    const height = Math.round(width * fbDims.height / fbDims.width); // This dimension ratio come from what FB shows

    const scaledHeight = Math.round(fbDims.height / fbDims.width * 100);

    const croppedPicture = event.getCroppedCover(width, height);
    if (!croppedPicture) {
      return null;
    }
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
          className="full-width no-border"
        />
      </div>
    );
    return (
      <a className="link-event-flyer" href={event.getRelativeUrl()}>
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

    return (
      <div className="event-description">
        <h3 className="event-title">
          <a href={event.getRelativeUrl()}>{event.name}</a>
        </h3>
        <ImagePrefix iconUrl={`${cdnBaseUrl}/img/categories-black.png`}>
          {keywords.join(', ')}
        </ImagePrefix>
        <ImagePrefix iconName="clock-o">
          {formatStartDateOnly(
            event.getListDateMoment({ timezone: false }),
            this.props.intl
          )}
        </ImagePrefix>
        <ImagePrefix iconName="map-marker">
          <div>{event.venue.name}</div>
          <FormatText>{event.venue.cityStateCountry()}</FormatText>
        </ImagePrefix>
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
    return (
      <div className="grey-top-border horizontal-event">
        <div className="event-image">
          <SquareEventFlyer
            event={this.props.event}
            lazyLoad={this.props.lazyLoad}
          />
        </div>
        <EventDescription event={this.props.event} />
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
          <a href={event.getRelativeUrl()}>
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
    featuredInfo: FeaturedInfo,
  };

  render() {
    const event = this.props.featuredInfo.event;
    let promotionText = null;
    if (this.props.featuredInfo.promotionText) {
      promotionText = (
        <div style={{ fontStyle: 'italic' }}>
          {this.props.featuredInfo.promotionText}
        </div>
      );
    }
    return (
      <Card>
        <HorizontalEventFlyer event={event} />
        <h3 className="event-title" style={{ marginTop: 10, marginBottom: 0 }}>
          <a href={event.getRelativeUrl()}>{event.name}</a>
        </h3>
        {promotionText}
        <div>{event.venue.cityStateCountry()}</div>
      </Card>
    );
  }
}

class FeaturedEvents extends React.Component {
  props: {
    featuredInfos: Array<FeaturedInfo>,
  };

  render() {
    if (!this.props.featuredInfos.length) {
      return null;
    }

    const resultItems = [];
    const imageEvents = this.props.featuredInfos.filter(x => x.event.picture);
    imageEvents.forEach((featuredInfo, index) => {
      // Slider requires children to be actual HTML elements.
      resultItems.push(
        <div key={featuredInfo.event.id}>
          <FeaturedEvent featuredInfo={featuredInfo} />
        </div>
      );
    });

    const results =
      resultItems.length > 1 ? (
        <Slider autoplay dots>
          {resultItems}
        </Slider>
      ) : (
        resultItems
      );

    return (
      <div style={{ width: '100%', paddingLeft: 10, paddingRight: 10 }}>
        <div>
          <b>Featured Event:</b>
        </div>
        {results}
      </div>
    );
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

    // Masonry is too big and messy to use here
    // And float-left can get us pretty far as a layout strategy
    const resultItems = [];
    this.props.events.forEach((event, index) => {
      resultItems.push(
        <div style={{ float: 'left' }}>
          <VerticalEvent key={event.id} event={event} />
        </div>
      );
    });

    return (
      <div style={{ width: '100%', padding: 10 }} className="clearfix">
        {resultItems}
      </div>
    );
  }
}

class _EventsList extends React.Component {
  props: {
    events: Array<SearchEvent>,
    loadMoreContent: () => void,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    const resultItems = [];
    let overallEventIndex = 0;

    const hasMoreEventsToFetch = Boolean(this.props.loadMoreContent);
    const eventIndexThreshold = Math.round(this.props.events.length * 0.75);

    let waypoint = (
      <Waypoint key="waypoint" onEnter={this.props.loadMoreContent} />
    );
    groupEventsByStartDate(
      this.props.intl,
      this.props.events
    ).forEach(({ header, events }) => {
      const renderedEvents = events.map((event, index) => (
        <HorizontalEvent
          key={event.id}
          event={event}
          lazyLoad={overallEventIndex + index > 8}
        />
      ));

      resultItems.push(
        <div key={header} className="bold card-background">
          {header}
        </div>
      );

      if (
        hasMoreEventsToFetch &&
        eventIndexThreshold >= overallEventIndex &&
        eventIndexThreshold < overallEventIndex + events.length
      ) {
        renderedEvents.splice(
          eventIndexThreshold - overallEventIndex,
          0,
          waypoint
        );
        waypoint = null;
      }
      resultItems.push(...renderedEvents);
      overallEventIndex += events.length;
    });

    if (hasMoreEventsToFetch) {
      if (waypoint) {
        resultItems.push(waypoint);
      }
      resultItems.push(<Loading key="bottom_loading" style={{ margin: 80 }} />);
    }

    function adItem(origIndex) {
      // Google Ad: search-inline
      return (
        <GoogleAd
          key={`ad-${origIndex}`}
          id={`ad-${origIndex}-adType-inline`}
          style={{ display: 'block' }}
          data-ad-format="auto"
          data-ad-slot="8358307776"
        />
      );
    }
    // Set eveyr-other to 1000 to temporarily disable interspersed ads
    const monetizedResultItems = insertEvery(resultItems, adItem, 1000);

    return <div>{monetizedResultItems}</div>;
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
    const oneboxList = this.props.links.map(onebox => (
      <li key={onebox.url}>
        <a className="link-onebox" href={onebox.url}>
          {onebox.title}
        </a>
      </li>
    ));

    return (
      <div>
        <b>Featured Sites:</b>
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
          {categories.map(x => (
            <option key={x} value={x}>
              {x || 'Overall'}
            </option>
          ))}
        </select>
        <p>
          <i>{this.props.subtitle}:</i>
        </p>
      </form>
    );
    return (
      <div>
        {selector}
        <ul>
          {peopleList.map(x => (
            <li key={x.id}>
              <a href={`https://www.facebook.com/${x.id}`}>{x.name}</a>
            </li>
          ))}
        </ul>
      </div>
    );
  }
}

class EventFilters extends React.Component {
  props: {
    events: Array<SearchEvent>,
    onChange: (filters: Array<string>) => void,
  };

  state: {
    initialStyles: Array<string>,
    styles: MultiSelectState,
  };

  constructor(props) {
    super(props);
    const styles = this.getStyles();
    this.state = {
      styles: generateUniformState(styles, true),
      initialStyles: styles,
    };
  }

  getStyles() {
    const categoryLookup = this.props.events.reduce((acc, e) => {
      const newAcc = { ...acc };
      e.annotations.categories.forEach(cat => {
        newAcc[cat] = true;
      });
      return newAcc;
    }, {});
    return Object.keys(categoryLookup);
  }

  render() {
    return (
      <MultiSelectList
        list={this.state.initialStyles}
        selected={this.state.styles}
        onChange={state => {
          this.setState({ styles: state });
          this.props.onChange(getSelected(state));
        }}
      />
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

class Loading extends React.Component {
  props: {
    style?: Object,
  };

  render() {
    return (
      <div style={this.props.style}>
        <Spinner name="circle" color="black" fadeIn="none" />
      </div>
    );
  }
}

class ResultsList extends React.Component {
  props: {
    response: NewSearchResponse,
    showPast: boolean,
    loadMoreContent: () => void,
  };

  state: {
    filters: Array<String>,
  };

  constructor(props) {
    super(props);
    this.state = { filters: [] };
    (this: any).onChange = this.onChange.bind(this);
  }

  onChange(filters) {
    this.setState({ filters });
  }

  filterResults(events) {
    if (!this.state.filters.length) {
      return events;
    }
    const filterSet = new Set(this.state.filters);
    const foundEvents = events.filter(e => {
      const overlapCategories = e.annotations.categories.filter(cat =>
        filterSet.has(cat)
      );
      return overlapCategories.length;
    });
    return foundEvents;
  }

  render() {
    let resultEvents = this.props.response.results.map(
      eventData => new SearchEvent(eventData)
    );
    resultEvents = sortNumber(resultEvents, resultEvent =>
      resultEvent.getListDateMoment({ timezone: false }).valueOf()
    );
    const featuredInfos = (this.props.response.featuredInfos || [])
      .map(x => ({ ...x, event: new Event(x.event) }));

    resultEvents = this.filterResults(resultEvents);

    const now = moment(); // Timezone-aware 'now'
    const eventPanels = [];
    let currentEvents = null;
    let fullEvents = null;
    if (this.props.showPast) {
      currentEvents = [];
      fullEvents = resultEvents;
    } else {
      currentEvents = resultEvents.filter(event => {
        const end = event.getEndMoment({ timezone: true, estimate: true });
        return (
          event.getListDateMoment({ timezone: true }).isBefore(now) &&
          now.isBefore(end)
        );
      });
      fullEvents = resultEvents.filter(event =>
        event.getListDateMoment({ timezone: true }).isAfter(now)
      );
      // DEBUG CODE for current events:
      // currentEvents = resultEvents;
    }
    if (currentEvents.length) {
      eventPanels.push(
        <div key="current">
          <div className="bold">Events happening now:</div>
          <CurrentEvents events={currentEvents} />
        </div>
      );
    }
    eventPanels.push(
      <EventsList
        key="full"
        events={fullEvents}
        loadMoreContent={this.props.loadMoreContent}
      />
    );

    let featuredPanel = null;
    if (featuredInfos.length) {
      featuredPanel = (
        <FeaturedEvents featuredInfos={featuredInfos.map(x => x)} />
      );
    }

    let oneboxPanel = null;
    if (this.props.response.onebox_links.length) {
      oneboxPanel = <OneboxLinks links={this.props.response.onebox_links} />;
    }

    const eventFilters =
      global.window && global.window.location.hash.includes('filter') ? (
        <EventFilters events={resultEvents} onChange={this.onChange} />
      ) : null;

    const jsonSchema = !ExecutionEnvironment.canUseDOM
      ? resultEvents.map(x => (
          <JsonSchema key={x.id} json={getEventSchema(x)} />
        ))
      : null;

    return (
      <div style={{ backgroundColor: 'white', padding: 10 }}>
        {eventFilters}
        {featuredPanel}
        {oneboxPanel}
        {eventPanels}
        {jsonSchema}
      </div>
    );
  }
}

export async function search(
  location: ?string,
  keywords: ?string,
  start: ?string,
  end: ?string
) {
  const args = {};
  if (location) {
    args.location = location;
  }
  if (keywords) {
    args.keywords = keywords;
  }
  if (start) {
    args.start = start;
  }
  if (end) {
    args.end = end;
  }

  const response = await performRequest(
    'search',
    {
      ...args,
      skip_people: 1, // We don't need to auto-fetch people, since it is on a different tab
    },
    {}
  );
  response.featuredInfos = response.featuredInfos.map(x => ({
    ...x,
    event: new SearchEvent(x.event),
  }));
  response.results = response.results.map(x => new SearchEvent(x));
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

  componentWillReceiveProps(nextProps) {
    this.setState({ people: nextProps.response.people, failed: false });
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
      const args = {
        location: this.props.response.query.location,
        locale: this.props.response.query.locale,
      };
      const response = await performRequest('people', args, args);
      this.setState({ people: response.people });
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
            <Loading style={{ margin: 50 }} />
          </CallbackOnRender>
        );
      } else {
        adminContents =
          admins && Object.keys(admins).length ? (
            <PersonList
              title={this.props.intl.formatMessage(messages.nearbyPromoters)}
              subtitle={this.props.intl.formatMessage(
                messages.nearbyPromotersMessage
              )}
              people={admins}
              categoryOrder={this.props.categoryOrder}
            />
          ) : null;
        attendeeContents =
          attendees && Object.keys(attendees).length ? (
            <PersonList
              title={this.props.intl.formatMessage(messages.nearbyDancers)}
              subtitle={this.props.intl.formatMessage(
                messages.nearbyDancersMessage
              )}
              people={attendees}
              categoryOrder={this.props.categoryOrder}
            />
          ) : null;
      }
    } else if (this.state.failed) {
      adminContents = <span>Error Loading People</span>;
      attendeeContents = <span>Error Loading People</span>;
    } else {
      adminContents = null;
      attendeeContents = null;
    }

    const adminsDiv = adminContents ? (
      <div className="col-sm-6">{adminContents}</div>
    ) : null;
    const attendeesDiv = attendeeContents ? (
      <div className="col-sm-6">{attendeeContents}</div>
    ) : null;
    return (
      <div className="row">
        {adminsDiv}
        {attendeesDiv}
      </div>
    );
  }
}
const PeopleList = injectIntl(_PeopleList);

class _Calendar extends React.Component {
  props: {
    query: FormSearchQuery,

    // Self-managed props
    window: windowProps,
  };

  render() {
    const query = querystring.stringify(this.props.query);
    const calendarUrl = `/calendar/iframe?${query}`;
    const height = this.props.window
      ? this.props.window.width / CalendarRatio
      : 500;
    return (
      <iframe
        src={calendarUrl}
        style={{
          width: '100%',
          height,
          border: 0,
          borderBottom: '1px solid lightgrey',
        }}
      />
    );
  }
}
const Calendar = wantsWindowSizes(_Calendar);

class ResultTabs extends React.Component {
  props: {
    response: NewSearchResponse,
    query: FormSearchQuery,
    loading: boolean,
    categoryOrder: Array<string>,
    loadMoreContent: () => void,
  };

  render() {
    const overlayDiv = this.props.loading ? (
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(255, 255, 255, 0.7)',
        }}
      />
    ) : null;
    const tabPanelStyle = {
      position: 'relative',
    };
    let peopleTab = null;
    let peopleTabPanel = null;
    // Only show People tab if we have chosen a location
    if (this.props.query.location) {
      peopleTab = <Tab>People</Tab>;
      // It seems every time we re-render this tab...it is fully reconstructed,
      // and loses its state (and the associated downloaded People data).
      // TODO: We should do a better job of preserving Tab state (redux?).
      peopleTabPanel = (
        <TabPanel style={tabPanelStyle}>
          <PeopleList
            response={this.props.response}
            categoryOrder={this.props.categoryOrder}
          />
          {overlayDiv}
        </TabPanel>
      );
    }

    const queryStart = this.props.query.start
      ? moment(this.props.query.start)
      : null;
    const queryEnd = this.props.query.end ? moment(this.props.query.end) : null;
    const now = moment();
    const showPast = Boolean(
      (queryStart && queryStart.isBefore(now)) ||
        (queryEnd && queryEnd.isBefore(now))
    );

    return (
      <Tabs>
        <TabList>
          <Tab>Events List</Tab>
          <Tab>Calendar</Tab>
          {peopleTab}
        </TabList>

        <TabPanel style={tabPanelStyle}>
          <ResultsList
            response={this.props.response}
            showPast={showPast}
            loadMoreContent={this.props.loadMoreContent}
          />
          {overlayDiv}
        </TabPanel>
        <TabPanel style={tabPanelStyle}>
          <Calendar query={this.props.query} />
          {overlayDiv}
        </TabPanel>
        {peopleTabPanel}
      </Tabs>
    );
  }
}

async function performSearch(query: FormSearchQuery) {
  const response = await search(
    query.location,
    query.keywords,
    query.start,
    query.end
  );
  return response;
}

class ResultsPage extends React.Component {
  props: {
    response: NewSearchResponse,
    categoryOrder: Array<string>,
    query: Object,
    hasMoreResults: boolean,
  };

  state: {
    loading: boolean,
    query: FormSearchQuery,
    response: NewSearchResponse,
    loadingMore: boolean,
    hasMoreEventsToFetch: boolean,
  };

  constructor(props) {
    super(props);
    this.state = {
      response: this.props.response,
      query: canonicalizeQuery(this.props.query),
      loading: false,
      loadingMore: false,
      hasMoreEventsToFetch: this.props.hasMoreResults,
    };
    (this: any).onNewSearch = this.onNewSearch.bind(this);
    (this: any).loadMoreContent = this.loadMoreContent.bind(this);
  }

  async onNewSearch(query: Object) {
    const newQuery = canonicalizeQuery(query);
    // Only re-search when the query has changed
    if (isEqual(newQuery, this.state.query)) {
      return;
    }

    const newQueryString = querystring.stringify(newQuery);
    const oldQueryString = new URL(window.location.href).search;
    // Try to avoid calling history.replace if the query string is the same
    // Each new location change, triggers a reload of the page favicons
    if (newQueryString !== oldQueryString) {
      const history = createBrowserHistory();
      history.replace(`/?${newQueryString}`);
    }

    await this.setState({ query: newQuery, loading: true });
    const response = await performSearch(query);
    await this.setState({
      response,
      loading: false,
      hasMoreEventsToFetch: false,
    });
  }

  async loadMoreContent() {
    if (this.state.hasMoreEventsToFetch && !this.state.loadingMore) {
      // Mark that we're currently loading more,
      // so we don't perform two requests simultaneously (best-effort)
      await this.setState({ loadingMore: true });
      const response = await performSearch(this.state.query);
      // Mark that we no longer have events to fetch,
      // so that our children know not to show the Loading spinner.
      // Also, simultaneously update the respones with the full list of events.
      await this.setState({
        response,
        hasMoreEventsToFetch: false,
        loadingMore: false,
      });
    }
  }

  render() {
    const jsonSchema = !ExecutionEnvironment.canUseDOM ? (
      <JsonSchema
        json={getBreadcrumbsForSearch(
          this.state.response.address,
          this.state.response.query.keywords
        )}
      />
    ) : null;

    const resultsCard = (
      <Card style={{ margin: 0, padding: 0 }}>
        {jsonSchema}
        <ResultTabs
          query={this.state.query}
          loading={this.state.loading}
          response={this.state.response}
          categoryOrder={this.props.categoryOrder}
          loadMoreContent={
            this.state.hasMoreEventsToFetch ? this.loadMoreContent : null
          }
        />
      </Card>
    );
    // If we want better sticky performance, we should use
    // https://github.com/yahoo/react-stickynode
    // (And convert over the event headers as well)
    const sideAd = (
      <GoogleAd
        style={{
          display: 'inline-block',
          width: 300,
          height: 600,
          position: 'fixed',
          zIndex: 1,
        }}
        data-ad-slot="6881574572"
      />
    );
    const searchHeaderAd = (
      <GoogleAd
        key={`ad-searchHeader`}
        id={`ad-searchHeader`}
        style={{ display: 'inline-block', width: '100%', height: 100 }}
        data-ad-format="auto"
        data-ad-slot="3343723888"
      />
    );

    return (
      <div>
        <div className="container">
          <div className="row" style={{ marginTop: 20, marginBottom: 50 }}>
            <div className="col-xs-12">
              <SearchBox
                query={this.props.query}
                onNewSearch={this.onNewSearch}
              />
            </div>
          </div>
          <div className="row">
            <div className="col-md-8">
              {searchHeaderAd}
              {resultsCard}
            </div>
            <div className="col-md-4 hidden-xs hidden-sm">{sideAd}</div>
          </div>
        </div>
      </div>
    );
  }
}

export default intlWeb(ResultsPage);
