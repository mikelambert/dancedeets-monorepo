/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import FormatText from 'react-format-text';
import moment from 'moment';
import ExecutionEnvironment from 'exenv';
import isEqual from 'lodash/isEqual';
import { useIntl } from 'react-intl';
import Slider from 'react-slick';
import Spinner from 'react-spinkit';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import Waypoint from 'react-waypoint';
import querystring from 'querystring';
import { createBrowserHistory } from 'history';
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
  FeaturedInfo,
  NewSearchResponse,
  Onebox,
  PeopleListing,
  StylePersonLookup,
} from 'dancedeets-common/js/events/search';
import {
  expandResults,
  groupEventsByStartDate,
} from 'dancedeets-common/js/events/helpers';
import { formatStartDateOnly } from 'dancedeets-common/js/dates';
import { cdnBaseUrl } from 'dancedeets-common/js/util/url';
import { JsonSchema } from './schema';
import { getEventSchema } from './schema/event';
import { getBreadcrumbsForSearch } from './schema/breadcrumbs';
import { Card, ImagePrefix, wantsWindowSizes } from './ui';
import type { WindowProps } from './ui';
import { SquareEventFlyer } from './eventCommon';
import GoogleAd from './googleAd';
import { canonicalizeQuery, SearchBox, CalendarRatio } from './resultsCommon';
import {
  MultiSelectList,
  generateUniformState,
  getSelected,
} from './MultiSelectList';
import type { MultiSelectState } from './MultiSelectList';

interface FormSearchQuery {
  location?: string;
  keywords?: string;
  start?: string;
  end?: string;
  min_worth?: number;
}

function insertEvery<T>(
  array: Array<T>,
  insertion: (origIndex: number) => T,
  n: number
): Array<T> {
  return array.reduce<Array<T>>(
    (newArray, member, i) =>
      i % n === n - 1
        ? newArray.concat(member, insertion(i))
        : newArray.concat(member),
    []
  );
}

async function performRequest(
  path: string,
  args: Record<string, string | number | boolean>,
  postArgs: Record<string, string | number | boolean> | null
): Promise<Record<string, unknown>> {
  return await realPerformRequest(window.fetch, path, args, postArgs, '2.0');
}

interface HorizontalEventFlyerProps {
  event: BaseEvent;
}

export class HorizontalEventFlyer extends React.Component<HorizontalEventFlyerProps> {
  render(): React.ReactElement | null {
    const fbDims = { width: 500, height: 262 };
    const { event } = this.props;
    const width = 700;
    const height = Math.round(width * fbDims.height / fbDims.width);

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
        <img alt="" src={croppedPicture.uri} className="full-width no-border" />
      </div>
    );
    return (
      <a className="link-event-flyer" href={event.getRelativeUrl()}>
        {imageTag}
      </a>
    );
  }
}

interface EventDescriptionProps {
  event: SearchEvent;
  indexingBot?: boolean;
}

function EventDescription({ event, indexingBot }: EventDescriptionProps): React.ReactElement {
  const intl = useIntl();
  const keywords = [...event.annotations.categories];
  if (indexingBot) {
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
          intl
        )}
      </ImagePrefix>
      <ImagePrefix iconName="map-marker">
        <div>{event.venue.name}</div>
        <FormatText>{event.venue.cityStateCountry()}</FormatText>
      </ImagePrefix>
    </div>
  );
}

interface HorizontalEventProps {
  event: SearchEvent;
  lazyLoad?: boolean;
}

class HorizontalEvent extends React.Component<HorizontalEventProps> {
  render(): React.ReactElement {
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

interface VerticalEventProps {
  event: SearchEvent;
}

class VerticalEvent extends React.Component<VerticalEventProps> {
  render(): React.ReactElement {
    const { event } = this.props;
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

interface FeaturedEventProps {
  featuredInfo: FeaturedInfo;
}

class FeaturedEvent extends React.Component<FeaturedEventProps> {
  render(): React.ReactElement {
    const { event } = this.props.featuredInfo;
    let promotionText: React.ReactElement | null = null;
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

interface FeaturedEventsProps {
  featuredInfos: Array<FeaturedInfo>;
}

class FeaturedEvents extends React.Component<FeaturedEventsProps> {
  render(): React.ReactElement | null {
    if (!this.props.featuredInfos.length) {
      return null;
    }

    const resultItems: React.ReactElement[] = [];
    const imageEvents = this.props.featuredInfos.filter(x => x.event.picture);
    imageEvents.forEach((featuredInfo) => {
      resultItems.push(
        <div key={`${featuredInfo.event.id}-${featuredInfo.event.start_time}`}>
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

interface CurrentEventsProps {
  events: Array<SearchEvent>;
}

class CurrentEvents extends React.Component<CurrentEventsProps> {
  render(): React.ReactElement | null {
    if (!this.props.events.length) {
      return null;
    }

    const resultItems: React.ReactElement[] = [];
    this.props.events.forEach((event) => {
      resultItems.push(
        <div key={`${event.id}-${event.start_time}`} style={{ float: 'left' }}>
          <VerticalEvent event={event} />
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

interface EventsListProps {
  events: Array<SearchEvent>;
  loadMoreContent: (() => void | Promise<void>) | null;
}

function EventsList({ events, loadMoreContent }: EventsListProps): React.ReactElement {
  const intl = useIntl();
  const resultItems: React.ReactNode[] = [];
  let overallEventIndex = 0;

  const hasMoreEventsToFetch = Boolean(loadMoreContent);
  const eventIndexThreshold = Math.round(events.length * 0.75);

  let waypoint: React.ReactElement | null = (
    <Waypoint key="waypoint" onEnter={loadMoreContent || undefined} />
  );
  groupEventsByStartDate(
    intl,
    events
  ).forEach(({ header, events: groupedEvents }) => {
    const renderedEvents: React.ReactNode[] = groupedEvents.map((event, index) => (
      <HorizontalEvent
        key={`${event.id}-${event.start_time}`}
        event={event as SearchEvent}
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
      eventIndexThreshold < overallEventIndex + groupedEvents.length
    ) {
      renderedEvents.splice(
        eventIndexThreshold - overallEventIndex,
        0,
        waypoint
      );
      waypoint = null;
    }
    resultItems.push(...renderedEvents);
    overallEventIndex += groupedEvents.length;
  });

  if (hasMoreEventsToFetch) {
    if (waypoint) {
      resultItems.push(waypoint);
    }
    resultItems.push(<Loading key="bottom_loading" style={{ margin: 80 }} />);
  }

  function adItem(origIndex: number): React.ReactElement {
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
  const monetizedResultItems = insertEvery(resultItems, adItem, 1000);

  return <div>{monetizedResultItems}</div>;
}

interface OneboxLinksProps {
  links: Array<Onebox>;
}

class _OneboxLinks extends React.Component<OneboxLinksProps> {
  render(): React.ReactElement | null {
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
const OneboxLinks = _OneboxLinks;

interface PersonListProps {
  title: string;
  subtitle: string;
  categoryOrder: Array<string>;
  people: StylePersonLookup;
}

interface PersonListState {
  category: string;
}

class PersonList extends React.Component<PersonListProps, PersonListState> {
  constructor(props: PersonListProps) {
    super(props);
    this.state = {
      category: 'Street Dance',
    };
  }

  render(): React.ReactElement | null {
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
      x => this.props.people[x]
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

interface EventFiltersProps {
  events: Array<SearchEvent>;
  onChange: (filters: Array<string>) => void;
}

interface EventFiltersState {
  initialStyles: Array<string>;
  styles: MultiSelectState;
}

class EventFilters extends React.Component<EventFiltersProps, EventFiltersState> {
  constructor(props: EventFiltersProps) {
    super(props);
    const styles = this.getStyles();
    this.state = {
      styles: generateUniformState(styles, true),
      initialStyles: styles,
    };
  }

  getStyles(): Array<string> {
    const categoryLookup = this.props.events.reduce<Record<string, boolean>>((acc, e) => {
      const newAcc = { ...acc };
      e.annotations.categories.forEach(cat => {
        newAcc[cat] = true;
      });
      return newAcc;
    }, {});
    return Object.keys(categoryLookup);
  }

  render(): React.ReactElement {
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

interface CallbackOnRenderProps {
  callback: () => void | Promise<void>;
  children: React.ReactNode;
}

class CallbackOnRender extends React.Component<CallbackOnRenderProps> {
  render(): React.ReactNode {
    if (this.props.callback) {
      this.props.callback();
    }
    return this.props.children;
  }
}

interface LoadingProps {
  style?: React.CSSProperties;
}

class Loading extends React.Component<LoadingProps> {
  render(): React.ReactElement {
    return (
      <div style={this.props.style}>
        <Spinner name="circle" color="black" fadeIn="none" />
      </div>
    );
  }
}

interface ResultsListProps {
  response: NewSearchResponse;
  showPast: boolean;
  loadMoreContent: (() => void | Promise<void>) | null;
}

interface ResultsListState {
  filters: Array<string>;
}

class ResultsList extends React.Component<ResultsListProps, ResultsListState> {
  constructor(props: ResultsListProps) {
    super(props);
    this.state = { filters: [] };
    this.onChange = this.onChange.bind(this);
  }

  onChange(filters: Array<string>): void {
    this.setState({ filters });
  }

  filterResults(events: Array<SearchEvent>): Array<SearchEvent> {
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

  render(): React.ReactElement {
    let resultEvents = this.props.response.results.map(
      eventData => new SearchEvent(eventData as unknown as Record<string, unknown>)
    );
    resultEvents = expandResults(resultEvents, SearchEvent) as SearchEvent[];
    resultEvents = sortNumber(resultEvents, resultEvent =>
      resultEvent.getListDateMoment({ timezone: false }).valueOf()
    );
    const featuredInfos = (this.props.response.featuredInfos || [])
      .map(x => ({ ...x, event: new Event(x.event as unknown as Record<string, unknown>) }));

    resultEvents = this.filterResults(resultEvents);

    const now = moment();
    const eventPanels: React.ReactElement[] = [];
    let currentEvents: Array<SearchEvent>;
    let fullEvents: Array<SearchEvent>;
    if (this.props.showPast) {
      currentEvents = [];
      fullEvents = resultEvents;
    } else {
      currentEvents = resultEvents.filter(event => {
        const end = event.getEndMomentWithFallback({ timezone: true });
        return (
          event.getListDateMoment({ timezone: true }).isBefore(now) &&
          now.isBefore(end)
        );
      });
      fullEvents = resultEvents.filter(event =>
        event.getListDateMoment({ timezone: true }).isAfter(now)
      );
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

    let featuredPanel: React.ReactElement | null = null;
    if (featuredInfos.length) {
      featuredPanel = (
        <FeaturedEvents featuredInfos={featuredInfos as FeaturedInfo[]} />
      );
    }

    let oneboxPanel: React.ReactElement | null = null;
    if (this.props.response.onebox_links.length) {
      oneboxPanel = <OneboxLinks links={this.props.response.onebox_links} />;
    }

    const eventFilters =
      (global as unknown as { window: Window }).window && (global as unknown as { window: Window }).window.location.hash.includes('filter') ? (
        <EventFilters events={resultEvents} onChange={this.onChange} />
      ) : null;

    const jsonSchema = !ExecutionEnvironment.canUseDOM
      ? resultEvents.map(x => (
          <JsonSchema
            key={`${x.id}-${x.start_time}`}
            json={getEventSchema(x)}
          />
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
  location: string | null | undefined,
  keywords: string | null | undefined,
  start: string | null | undefined,
  end: string | null | undefined,
  min_worth: number | null | undefined
): Promise<NewSearchResponse> {
  const args: Record<string, unknown> = {};
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
  if (min_worth) {
    args.min_worth = min_worth;
  }

  const response = await performRequest(
    'search',
    {
      ...args,
      skip_people: 1,
    },
    {}
  );
  const searchResponse = response as unknown as NewSearchResponse;
  searchResponse.featuredInfos = (searchResponse.featuredInfos || []).map(x => ({
    ...x,
    event: new Event(x.event as unknown as Record<string, unknown>),
  }));
  searchResponse.results = searchResponse.results.map(x => new SearchEvent(x as unknown as Record<string, unknown>));
  return searchResponse;
}

interface PeopleListProps {
  response: NewSearchResponse;
  categoryOrder: Array<string>;
}

function PeopleList({ response, categoryOrder }: PeopleListProps): React.ReactElement {
  const intl = useIntl();
  const [people, setPeople] = React.useState<PeopleListing | null>(response.people);
  const [failed, setFailed] = React.useState(false);
  const loadingPeopleRef = React.useRef(false);

  React.useEffect(() => {
    setPeople(response.people);
    setFailed(false);
  }, [response.people]);

  const loadPeopleIfNeeded = React.useCallback(async (): Promise<void> => {
    if (
      !ExecutionEnvironment.canUseDOM ||
      !people ||
      Object.keys(people).length ||
      loadingPeopleRef.current
    ) {
      return;
    }
    try {
      loadingPeopleRef.current = true;
      const args = {
        location: response.query.location,
        locale: response.query.locale,
      };
      const fetchedResponse = await performRequest('people', args, args);
      setPeople((fetchedResponse as { people: PeopleListing }).people);
    } catch (e) {
      console.error(e);
      setFailed(true);
    }
    loadingPeopleRef.current = false;
  }, [people, response.query.location, response.query.locale]);

  let adminContents: React.ReactElement | null = null;
  let attendeeContents: React.ReactElement | null = null;
  if (people) {
    const admins = people.ADMIN;
    const attendees = people.ATTENDEE;
    if (!admins && !attendees) {
      return (
        <CallbackOnRender callback={loadPeopleIfNeeded}>
          <Loading style={{ margin: 50 }} />
        </CallbackOnRender>
      );
    } else {
      adminContents =
        admins && Object.keys(admins).length ? (
          <PersonList
            title={intl.formatMessage(messages.nearbyPromoters)}
            subtitle={intl.formatMessage(
              messages.nearbyPromotersMessage
            )}
            people={admins}
            categoryOrder={categoryOrder}
          />
        ) : null;
      attendeeContents =
        attendees && Object.keys(attendees).length ? (
          <PersonList
            title={intl.formatMessage(messages.nearbyDancers)}
            subtitle={intl.formatMessage(
              messages.nearbyDancersMessage
            )}
            people={attendees}
            categoryOrder={categoryOrder}
          />
        ) : null;
    }
  } else if (failed) {
    adminContents = <span>Error Loading People</span>;
    attendeeContents = <span>Error Loading People</span>;
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

interface CalendarProps {
  query: FormSearchQuery;
  window: WindowProps;
}

class _Calendar extends React.Component<CalendarProps> {
  render(): React.ReactElement {
    const query = querystring.stringify(this.props.query as Record<string, string>);
    const calendarUrl = `/calendar/iframe?${query}`;
    const height = this.props.window
      ? this.props.window.width / CalendarRatio
      : 500;
    return (
      <iframe
        title="Event Calendar"
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

interface ResultTabsProps {
  response: NewSearchResponse;
  query: FormSearchQuery;
  loading: boolean;
  categoryOrder: Array<string>;
  loadMoreContent: (() => void | Promise<void>) | null;
}

class ResultTabs extends React.Component<ResultTabsProps> {
  render(): React.ReactElement {
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
    const tabPanelStyle: React.CSSProperties = {
      position: 'relative',
    };
    let peopleTab: React.ReactElement | null = null;
    let peopleTabPanel: React.ReactElement | null = null;
    if (this.props.query.location) {
      peopleTab = <Tab>People</Tab>;
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

async function performSearch(query: FormSearchQuery): Promise<NewSearchResponse> {
  const response = await search(
    query.location,
    query.keywords,
    query.start,
    query.end,
    query.min_worth
  );
  return response;
}

interface ResultsPageProps {
  response: NewSearchResponse;
  categoryOrder: Array<string>;
  query: Record<string, unknown>;
  hasMoreResults: boolean;
  currentLocale: string;
}

interface ResultsPageState {
  loading: boolean;
  query: FormSearchQuery;
  response: NewSearchResponse;
  loadingMore: boolean;
  hasMoreEventsToFetch: boolean;
}

class ResultsPage extends React.Component<ResultsPageProps, ResultsPageState> {
  constructor(props: ResultsPageProps) {
    super(props);
    this.state = {
      response: this.props.response,
      query: canonicalizeQuery(this.props.query as { location: string; keywords: string; start: string; end: string }) as FormSearchQuery,
      loading: false,
      loadingMore: false,
      hasMoreEventsToFetch: this.props.hasMoreResults,
    };
    this.onNewSearch = this.onNewSearch.bind(this);
    this.loadMoreContent = this.loadMoreContent.bind(this);
  }

  async onNewSearch(query: Record<string, unknown>): Promise<void> {
    const newQuery = canonicalizeQuery(query as { location: string; keywords: string; start: string; end: string }) as FormSearchQuery;
    if (isEqual(newQuery, this.state.query)) {
      return;
    }

    const newQueryString = querystring.stringify(newQuery as Record<string, string>);
    const oldQueryString = new URL(window.location.href).search;
    if (newQueryString !== oldQueryString) {
      const history = createBrowserHistory();
      history.replace(`/?${newQueryString}`);
    }

    await this.setState({ query: newQuery, loading: true });
    const response = await performSearch(query as FormSearchQuery);
    await this.setState({
      response,
      loading: false,
      hasMoreEventsToFetch: false,
    });
  }

  async loadMoreContent(): Promise<void> {
    if (this.state.hasMoreEventsToFetch && !this.state.loadingMore) {
      await this.setState({ loadingMore: true });
      const response = await performSearch(this.state.query);
      await this.setState({
        response,
        hasMoreEventsToFetch: false,
        loadingMore: false,
      });
    }
  }

  render(): React.ReactElement {
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
        key="ad-searchHeader"
        id="ad-searchHeader"
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
