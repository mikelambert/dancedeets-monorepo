/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { injectIntl, intlShape } from 'react-intl';
import { intlWeb } from 'dancedeets-common/js/intl';
import { SearchEvent } from 'dancedeets-common/js/events/models';
import type { NewSearchResponse } from 'dancedeets-common/js/events/search';
import {
  formatStartDateOnly,
  formatStartTime,
} from 'dancedeets-common/js/dates';
import { groupEventsByStartDate } from 'dancedeets-common/js/events/helpers';
import { addUrlArgs } from 'dancedeets-common/js/util/url';
import type { ExportedIconsEnum } from './exportedIcons';
import { EmailWrapper } from './mailCommon';

const outsideGutter = 20;
const verticalSpacing = 20;

function addTrackingTags(origUrl) {
  const tags = {
    utm_source: 'weekly_email',
    utm_medium: 'email',
    utm_campaign: 'weekly_email',
  };
  return addUrlArgs(origUrl, tags);
}

class SmallIcon extends React.Component {
  props: {
    url: string,
    alt: string,
  };

  render() {
    return (
      <img src={this.props.url} width="16" height="16" alt={this.props.alt} />
    );
  }
}

class FontAwesomeIcon extends React.Component {
  props: {
    name: ExportedIconsEnum,
    alt: string,
  };

  render() {
    return (
      <SmallIcon
        url={`https://static.dancedeets.com/img/font-awesome/black/png/16/${this
          .props.name}.png`}
        alt={this.props.alt}
      />
    );
  }
}

class _MailEvent extends React.Component {
  props: {
    event: SearchEvent,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    const event = this.props.event;
    const size = 180;
    const gutter = 10;
    let flyerImage = null;
    const eventUrl = addTrackingTags(this.props.event.getUrl());

    const coverUrl = event.getCroppedCover(size, size);
    if (coverUrl) {
      flyerImage = (
        <mj-image
          align="left"
          padding-right={gutter}
          src={coverUrl.source}
          alt=""
          width={size}
          href={eventUrl}
          border="1px solid black"
        />
      );
    }

    const verticalAlign = { verticalAlign: 'top' };
    const imageAlign = { ...verticalAlign, textAlign: 'center', width: 32 };

    let danceCategories = null;
    if (event.annotations.categories.length) {
      danceCategories = (
        <tr>
          <td style={imageAlign} padding-el>
            <SmallIcon
              url="https://static.dancedeets.com/img/categories-black.png"
              alt="Categories"
            />
          </td>
          <td style={verticalAlign}>
            {event.annotations.categories.join(', ')}
          </td>
        </tr>
      );
    }

    const start = event.getStartMoment({ timezone: false });
    return (
      <mj-section
        background-color="#ffffff"
        padding-left={outsideGutter * 2}
        padding-right={outsideGutter}
        padding-bottom={verticalSpacing}
      >
        <mj-column width="33%">{flyerImage}</mj-column>
        <mj-column width="66%">
          <mj-text mj-class="header">
            <a href={eventUrl}>{event.name}</a>
          </mj-text>
          <mj-table>
            {danceCategories}
            <tr>
              <td style={imageAlign}>
                <FontAwesomeIcon name="clock-o" alt="Time" />
              </td>
              <td style={verticalAlign}>
                {formatStartDateOnly(start, this.props.intl)},
                {formatStartTime(start, this.props.intl)}
              </td>
            </tr>
            <tr>
              <td style={imageAlign}>
                <FontAwesomeIcon name="map-marker" alt="Location" />
              </td>
              <td style={verticalAlign}>
                {event.venue.name}
                <br />
                {event.venue.cityStateCountry('\n')}
              </td>
            </tr>
          </mj-table>
        </mj-column>
      </mj-section>
    );
  }
}
const MailEvent = injectIntl(_MailEvent);

class DayHeader extends React.Component {
  props: {
    title: string,
  };

  render() {
    return (
      <mj-section
        background-color="#ffffff"
        padding-left={outsideGutter}
        padding-right={outsideGutter}
        padding-bottom={verticalSpacing}
      >
        <mj-column width="full-width">
          <mj-text mj-class="header">{this.props.title}</mj-text>
        </mj-column>
      </mj-section>
    );
  }
}

class _BodyWrapper extends React.Component {
  props: {
    user: any,
    response: NewSearchResponse,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    const resultEvents = this.props.response.results.map(
      eventData => new SearchEvent(eventData)
    );

    const eventDisplays = [];
    groupEventsByStartDate(
      this.props.intl,
      resultEvents
    ).forEach(({ header, events }) => {
      eventDisplays.push(<DayHeader key={header} title={header} />);
      eventDisplays.push(
        ...events.map(event => <MailEvent key={event.id} event={event} />)
      );
    });
    return [
      <mj-section background-color="#ffffff">
        <mj-column width="100%">
          <mj-text padding="10px 25px">
            <p>
              Hey {this.props.user.userName}
              , here’s what we’ve found for you this week!
            </p>
          </mj-text>
        </mj-column>
      </mj-section>,

      ...eventDisplays,

      <mj-section background-color="#ffffff">
        <mj-column width="100%">
          <mj-text padding="10px 25px">
            Looking for more events? Be sure to{' '}
            <a href="{{ search_url }}">check out website</a> for the complete
            and up-to-date schedule!
          </mj-text>
        </mj-column>
      </mj-section>,
      <mj-section
        background-color="#222337"
        padding-bottom="20px"
        padding-top="10px"
      >
        <mj-column width="full-width">
          <mj-text
            align="center"
            color="#FFFFFF"
            mj-class="header"
            padding="30px 0 0 0"
          >
            That’s all we’ve got for now...see you next week!
          </mj-text>
        </mj-column>
      </mj-section>,
    ];
  }
}
const BodyWrapper = injectIntl(_BodyWrapper);

class WeeklyEmail extends React.Component {
  props: {
    user: any,
    response: NewSearchResponse,
  };

  render() {
    return (
      <EmailWrapper
        header={`With ${this.props.response.results
          .length} events for Your Week in Dance!`}
        footer={
          <div>
            You may also{' '}
            <a href="*|UNSUB:https://www.dancedeets.com/user/unsubscribe|*">
              unsubscribe
            </a>{' '}
            or{' '}
            <a href="https://www.dancedeets.com/user/edit">
              change your preferred city
            </a>
            .
          </div>
        }
      >
        <BodyWrapper user={this.props.user} response={this.props.response} />
      </EmailWrapper>
    );
  }
}

export default intlWeb(WeeklyEmail);
