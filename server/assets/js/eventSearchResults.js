/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import url from 'url';
import FormatText from 'react-format-text';
import moment from 'moment';
import upperFirst from 'lodash/upperFirst';
import { injectIntl, intlShape } from 'react-intl';
import { StickyContainer, Sticky } from 'react-sticky';
import Masonry from 'react-masonry-component';
import Slider from 'react-slick';
import Collapse, { Panel } from 'rc-collapse';
import { intlWeb } from 'dancedeets-common/js/intl';
import type { Cover, JSONObject } from 'dancedeets-common/js/events/models';
import {
  BaseEvent,
  Event,
  SearchEvent,
} from 'dancedeets-common/js/events/models';
import type {
  NewSearchResponse,
  Onebox,
  StylePersonLookup,
} from 'dancedeets-common/js/events/search';
import {
  formatStartTime,
  weekdayDate,
  weekdayTime,
} from 'dancedeets-common/js/dates';
import {
  formatAttending,
  groupEventsByStartDate,
} from 'dancedeets-common/js/events/helpers';
import { Card, ImagePrefix, wantsWindowSizes } from './ui';
import type { windowProps } from './ui';
import { SquareEventFlyer } from './eventCommon';

require('slick-carousel/slick/slick.css');
require('slick-carousel/slick/slick-theme.css');
require('../css/slick.scss');
require('../css/rc-collapse.scss');

/*
import {
  yellowColors,
} from '../ui/Colors';
*/
// TODO: Copies from mobile/js/ui/Colors.js
const yellowColors = ['#FFF3B0', '#FFEA73', '#FFD802', '#FFCA01', '#C0A000'];

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
    indexingBot: boolean,

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
      <div>
        <h3 className="event-title">
          <a href={event.getUrl()}>
            <span>{event.name}</span>
          </a>
        </h3>
        <ImagePrefix
          icon={require('../img/categories-white.png')} // eslint-disable-line global-require
        >
          {keywords.join(', ')}
        </ImagePrefix>
        <ImagePrefix iconName="clock-o">
          {formatStartTime(event.start_time, this.props.intl)}
        </ImagePrefix>
        <ImagePrefix iconName="map-marker">
          <div>{event.venue.name}</div>
          <FormatText>{event.venue.cityStateCountry('\n')}</FormatText>
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
    const event = this.props.event;
    return (
      <div className="wide-event clearfix">
        <div className="event-image">
          <SquareEventFlyer
            event={this.props.event}
            lazyLoad={this.props.lazyLoad}
          />
        </div>
        <div className="event-description">
          <EventDescription event={this.props.event} />
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
          <FormatText>{event.venue.cityStateCountry('\n')}</FormatText>
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
    groupEventsByStartDate(
      this.props.intl,
      this.props.events
    ).forEach(({ header, events }) => {
      resultItems.push(
        <li
          key={header}
          className="day-header"
          style={{
            marginTop: '30px',
            marginBottom: '10px',
            borderBottom: '1px solid white',
          }}
        >
          <Sticky className="opaque">{header}</Sticky>
        </li>
      );
      resultItems.push(
        ...events.map((event, index) => (
          <li key={event.id}>
            <HorizontalEvent
              key={event.id}
              event={event}
              lazyLoad={index > 8}
            />
          </li>
        ))
      );
    });

    return (
      <StickyContainer>
        <ol className="events-list">
          {resultItems}
        </ol>
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
    const oneboxList = this.props.links.map(onebox => (
      <li key={onebox.url}>
        <a className="link-onebox" href={onebox.url}>{onebox.title}</a>
      </li>
    ));

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
          {categories.map(x => (
            <option key={x} value={x}>{x || 'Overall'}</option>
          ))}
        </select>
        <p><i>{this.props.subtitle}:</i></p>
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

class _ResultsList extends React.Component {
  props: {
    response: NewSearchResponse,
    past: boolean,
    categoryOrder: Array<string>,

    // Self-managed props
    window: windowProps,
  };

  getPeoplePanel() {
    let peoplePanel = [];
    const admins = this.props.response.people.ADMIN;
    const attendees = this.props.response.people.ATTENDEE;
    if (admins || attendees) {
      const adminsList = (
        <PersonList
          title="Promoters"
          subtitle="If you want to organize an event, work with these folks"
          people={admins}
          categoryOrder={this.props.categoryOrder}
        />
      );
      const attendeesList = (
        <PersonList
          title="Dancers"
          subtitle="If you want to connect with the dance scene, hit these folks up"
          people={attendees}
          categoryOrder={this.props.categoryOrder}
        />
      );

      if (this.props.window && this.props.window.width < 768) {
        if (admins) {
          peoplePanel.push(
            <Panel key="people1" header="Nearby Promoters">{adminsList}</Panel>
          );
        }
        if (attendees) {
          peoplePanel.push(
            <Panel key="people2" header="Nearby Dancers">{attendeesList}</Panel>
          );
        }
      } else {
        const adminsDiv = admins
          ? <div className="col-sm-6">{adminsList}</div>
          : null;
        const attendeesDiv = attendees
          ? <div className="col-sm-6">{attendeesList}</div>
          : null;
        peoplePanel = (
          <Panel key="people" header="Nearby Promoters & Dancers">
            <div className="row">{adminsDiv}{attendeesDiv}</div>
          </Panel>
        );
      }
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
    const peoplePanel = this.getPeoplePanel();

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
    // Keep in sync with mobile?
    if (eventCount < 10) {
      defaultKeys.push('people', 'people1', 'people2');
    }

    return (
      <Collapse defaultActiveKey={defaultKeys}>
        {featuredPanel}
        {peoplePanel}
        {oneboxPanel}
        {eventPanels}
      </Collapse>
    );
  }
}
const ResultsList = wantsWindowSizes(_ResultsList);

export default intlWeb(ResultsList);
