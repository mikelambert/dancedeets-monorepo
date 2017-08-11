/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { injectIntl, intlShape } from 'react-intl';
import url from 'url';
import { intlWeb } from 'dancedeets-common/js/intl';
import type { Cover, JSONObject } from 'dancedeets-common/js/events/models';
import { SearchEvent } from 'dancedeets-common/js/events/models';
import type { NewSearchResponse } from 'dancedeets-common/js/events/search';
import {
  formatStartDateOnly,
  formatStartTime,
} from 'dancedeets-common/js/dates';
import { groupEventsByStartDate } from 'dancedeets-common/js/events/helpers';
import type { ExportedIconsEnum } from './exportedIcons';

const outsideGutter = 20;
const verticalSpacing = 20;

function addArgs(origUrl, args) {
  const parsedUrl = url.parse(origUrl, true);
  parsedUrl.query = { ...parsedUrl.query, ...args };
  const newUrl = url.format(parsedUrl);
  return newUrl;
}

function addTrackingTags(origUrl) {
  const tags = {
    utm_source: 'weekly_email',
    utm_medium: 'email',
    utm_campaign: 'weekly_email',
  };
  return addArgs(origUrl, tags);
}

function generateCroppedCover(picture: Cover, width: number, height: number) {
  return {
    source: addArgs(picture.source, { width, height }),
    width,
    height,
  };
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
        url={`https://www.dancedeets.com/dist/img/font-awesome/black/png/16/${this
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

    if (event.picture) {
      const coverUrl = generateCroppedCover(event.picture, size, size);
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
              url="https://www.dancedeets.com/dist/img/categories-black.png"
              alt="Categories"
            />
          </td>
          <td style={verticalAlign}>
            {event.annotations.categories.join(', ')}
          </td>
        </tr>
      );
    }

    const start = event.getStartMoment();
    return (
      <mj-section
        background-color="#ffffff"
        padding-left={outsideGutter * 2}
        padding-right={outsideGutter}
        padding-bottom={verticalSpacing}
      >
        <mj-column width="33%">
          {flyerImage}
        </mj-column>
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
    // TODO: flesh this out
    user?: any,
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
    return (
      <mj-container background-color="#D0D0F0">
        <mj-section full-width="full-width" padding="10px 25px">
          <mj-group>
            <mj-column>
              <mj-text>
                With
                {' '}
                {this.props.response.results.length}
                {' '}
                events for Your Week in Dance!
              </mj-text>
            </mj-column>
          </mj-group>
        </mj-section>
        <mj-section full-width="full-width">
          <mj-column>
            <mj-image
              src="https://www.dancedeets.com/images/mail-top.png"
              alt="top border"
            />
          </mj-column>
        </mj-section>
        <mj-section background-color="#222337" padding="0">
          <mj-column width="40%">
            <mj-image
              align="center"
              src="https://www.dancedeets.com/dist-400780539943311269/img/deets-head-and-title-on-black@2x.png"
              alt="logo"
              padding="0 0 30px 0"
            />
          </mj-column>
        </mj-section>
        <mj-section background-color="#ffffff">
          <mj-column width="100%">
            <mj-text padding="10px 25px">
              <p>
                Hey
                {' '}
                {this.props.user.userName}
                , here’s what we’ve found for you this week!
              </p>
            </mj-text>
          </mj-column>
        </mj-section>

        {eventDisplays}

        <mj-section background-color="#ffffff">
          <mj-column width="100%">
            <mj-text padding="10px 25px">
              Looking for more events? Be sure to
              {' '}
              <a href="{{ search_url }}">check out website</a>
              {' '}
              for the complete and up-to-date schedule!
            </mj-text>
          </mj-column>
        </mj-section>
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
        </mj-section>
        <mj-section>
          <mj-column>
            <mj-image
              src="https://www.dancedeets.com/images/mail-bottom.png"
              alt="bottom border"
              align="center"
              border="none"
              width="600"
              container-background-color="transparent"
            />
          </mj-column>
        </mj-section>
        <mj-section full-width="full-width" padding="20px">
          <mj-column>
            <mj-text align="center">
              You may also
              {' '}
              <a href="*|UNSUB:https://www.dancedeets.com/user/unsubscribe|*">
                unsubscribe
              </a>
              {' '}
              or
              {' '}
              <a href="https://www.dancedeets.com/user/edit">
                change your preferred city
              </a>
              .
            </mj-text>
          </mj-column>
        </mj-section>
      </mj-container>
    );
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
      <mjml>
        <mj-head>
          <mj-attributes>
            <mj-all
              padding="0"
              color="#000000"
              font-size="12px"
              line-height="20px"
              font-family="Ubuntu, Helvetica, Arial, sans-serif"
            />
            <mj-class name="header" font-size="18px" line-height="26px" />
          </mj-attributes>
        </mj-head>
        <mj-body>
          <BodyWrapper user={this.props.user} response={this.props.response} />
        </mj-body>
      </mjml>
    );
  }
}

export default intlWeb(WeeklyEmail);
