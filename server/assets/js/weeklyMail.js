/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  injectIntl,
  intlShape,
} from 'react-intl';
import url from 'url';
import {
  intlWeb,
} from 'dancedeets-common/js/intl';
import type {
  Cover,
  JSONObject,
} from 'dancedeets-common/js/events/models';
import {
  BaseEvent,
  SearchEvent,
} from 'dancedeets-common/js/events/models';
import type {
  NewSearchResponse,
} from 'dancedeets-common/js/events/search';
import {
  formatStartTime,
  weekdayDate,
  weekdayTime,
} from 'dancedeets-common/js/dates';
import {
  groupEventsByStartDate,
} from 'dancedeets-common/js/events/helpers';


const outsideGutter = 20;
const verticalSpacing = 20;

function generateCroppedCover(picture: Cover, width: number, height: number) {
  const parsedSource = url.parse(picture.source, true);
  parsedSource.query = { ...parsedSource.query, width, height };
  const newSourceUrl = url.format(parsedSource);

  return {
    source: newSourceUrl,
    width,
    height,
  };
}

class _MailEvent extends React.Component {
  props: {
    event: BaseEvent;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const event = this.props.event;
    const fullWidth = 600;
    const size = 180;
    const gutter = 10;
    const coverUrl = generateCroppedCover(event.picture, size, size);
    const eventUrl = this.props.event.getUrl();
    return (
      <mj-section
        background-color="#ffffff"
        padding-left={outsideGutter * 2}
        padding-right={outsideGutter}
        padding-bottom={verticalSpacing}
      >
        <mj-column width={size + gutter}>
          <mj-image
            padding-right={gutter}
            src={coverUrl.source}
            alt=""
            width={size}
            href={eventUrl}
          />
        </mj-column>
        <mj-column width={fullWidth - size - gutter - outsideGutter * 3}>
          <mj-text mj-class="header">
            <a href={eventUrl}>{event.name}</a>
          </mj-text>
          <mj-text>
            Time: {formatStartTime(event.start_time, this.props.intl)}
            <br />
            Location: {event.venue.name}
            <br />
            {event.venue.cityStateCountry('\n')}
          </mj-text>
          <mj-button align="left" href={eventUrl}>
            See Event Details
          </mj-button>
        </mj-column>
      </mj-section>
    );
  }
}
const MailEvent = injectIntl(_MailEvent);

function shouldReactivateUser(user) {
  return true;
  // return this.props.user.expired_oauth_token && this.props.user.num_auto_added_events > 10;
}

class IntroText extends React.Component {
  props: {
    // TODO: flesh this out
    user: any;
  }

  render() {
    return (<mj-text padding="10px 25px">
      <p>Hey {this.props.user.userName}, here&rsquo;s what we&rsquo;ve got for you this week!</p>
      <p>Or check <a href="{{ search_url }}">the most up-to-date listings</a>.</p>
    </mj-text>);
  }
}

class DayHeader extends React.Component {
  props: {
    title: string;
  }

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
    user?: any;
    response: NewSearchResponse;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const resultEvents = this.props.response.results.map(eventData => new SearchEvent(eventData));

    const eventDisplays = [];
    groupEventsByStartDate(this.props.intl, resultEvents).forEach(({ header, events }) => {
      eventDisplays.push(<DayHeader key={header} title={header} />);
      eventDisplays.push(...events.map(event => <MailEvent key={event.id} event={event} />));
    });
    return (
      <mj-container background-color="#e0f2ff">
        <mj-section full-width="full-width" padding="10px 25px">
          <mj-group>
            <mj-column>
              <mj-text>
                DanceDeets Weekly, with {this.props.response.results.length} this week for you!
              </mj-text>
            </mj-column>
          </mj-group>
        </mj-section>
        <mj-section full-width="full-width" >
          <mj-column>
            <mj-image src="http://www.dancedeets.com/images/mail-top.png" alt="top border" />
          </mj-column>
        </mj-section>
        <mj-section background-color="#222337" padding="0">
          <mj-column width="40%">
            <mj-image align="center" src="http://www.dancedeets.com/dist-400780539943311269/img/deets-head-and-title-on-black@2x.png" alt="logo" padding="0 0 30px 0" />
          </mj-column>
        </mj-section>
        <mj-section background-color="#ffffff">
          <mj-column width="100%">
            <IntroText user={this.props.user} />
          </mj-column>
        </mj-section>

        {eventDisplays}

        <mj-section background-color="#222337" padding-bottom="20px" padding-top="10px">
          <mj-column width="full-width">
            <mj-text align="center" color="#FFFFFF" mj-class="header" padding="30px 0 0 0">That&rsquo;s all we&rsquo;ve got for now...see you next week!
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section>
          <mj-column>
            <mj-image src="http://www.dancedeets.com/images/mail-bottom.png" alt="bottom border" align="center" border="none" width="600" container-background-color="transparent" />
          </mj-column>
        </mj-section>
        <mj-section full-width="full-width" padding="20px">
          <mj-column>
            <mj-text align="center">
              You may also <a href="*|UNSUB:http://www.dancedeets.com|*">unsubscribe</a> or <a href="http://www.dancedeets.com/user/edit">change your preferred city</a>
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
    user: any;
    response: NewSearchResponse;
  }

  render() {
    return (
      <mjml>
        <mj-head>
          <mj-attributes>
            <mj-all padding="0" color="#000000" font-size="12px" line-height="18px" font-family="Ubuntu, Helvetica, Arial, sans-serif" />
            <mj-class name="header" font-size="18px" line-height="23px" />
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
