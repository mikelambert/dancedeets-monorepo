/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { useIntl, IntlShape } from 'react-intl';
import { intlWeb } from 'dancedeets-common/js/intl';
import { BaseEvent, SearchEvent } from 'dancedeets-common/js/events/models';
import type { NewSearchResponse } from 'dancedeets-common/js/events/search';
import {
  formatStartDateOnly,
  formatStartTime,
} from 'dancedeets-common/js/dates';
import { groupEventsByStartDate } from 'dancedeets-common/js/events/helpers';
import type { ExportedIconsEnum } from './exportedIcons';
import { EmailWrapper, outsideGutter } from './mailCommon';

const verticalSpacing = 20;

interface SmallIconProps {
  url: string;
  alt: string;
}

function SmallIcon({ url, alt }: SmallIconProps): React.ReactElement {
  return <img src={url} width="16" height="16" alt={alt} />;
}

interface FontAwesomeIconProps {
  name: ExportedIconsEnum;
  alt: string;
}

function FontAwesomeIcon({ name, alt }: FontAwesomeIconProps): React.ReactElement {
  return (
    <SmallIcon
      url={`https://storage.googleapis.com/dancedeets-static/img/font-awesome/black/png/16/${name}.png`}
      alt={alt}
    />
  );
}

interface MailEventProps {
  event: SearchEvent;
}

function MailEvent({ event }: MailEventProps): React.ReactElement {
  const intl = useIntl();
  const size = 180;
  const gutter = 10;
  let flyerImage: React.ReactElement | null = null;
  const eventUrl = event.getUrl({
    utm_source: 'weekly_email',
    utm_medium: 'email',
    utm_campaign: 'weekly_email',
  });

  const coverUrl = event.getCroppedCover(size, size);
  if (coverUrl) {
    flyerImage = (
      <mj-image
        align="left"
        padding-right={gutter}
        src={coverUrl.uri}
        alt=""
        width={`${size}`}
        href={eventUrl}
        border="1px solid black"
      />
    );
  }

  const verticalAlign: React.CSSProperties = { verticalAlign: 'top' };
  const imageAlign: React.CSSProperties = { ...verticalAlign, textAlign: 'center', width: 32 };

  let danceCategories: React.ReactElement | null = null;
  if (event.annotations.categories.length) {
    danceCategories = (
      <tr>
        <td style={imageAlign}>
          <SmallIcon
            url="https://storage.googleapis.com/dancedeets-static/img/categories-black.png"
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
      padding-left={outsideGutter + 20}
      padding-right={outsideGutter}
      padding-bottom={verticalSpacing}
    >
      <mj-column width="33%">{flyerImage as React.ReactNode}</mj-column>
      <mj-column width="66%">
        <mj-text mj-class="header">
          <a href={eventUrl}>{event.name}</a>
        </mj-text>
        <mj-table>
          {danceCategories as React.ReactNode}
          <tr>
            <td style={imageAlign}>
              <FontAwesomeIcon name="clock-o" alt="Time" />
            </td>
            <td style={verticalAlign}>
              {formatStartDateOnly(start, intl)},
              {formatStartTime(start, intl)}
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

interface DayHeaderProps {
  title: string;
}

function DayHeader({ title }: DayHeaderProps): React.ReactElement {
  return (
    <mj-section
      background-color="#ffffff"
      padding-left={outsideGutter}
      padding-right={outsideGutter}
      padding-bottom={verticalSpacing}
    >
      <mj-column width="full-width">
        <mj-text mj-class="header">{title}</mj-text>
      </mj-column>
    </mj-section>
  );
}

interface EventDisplayProps {
  events: Array<BaseEvent>;
}

export function EventDisplay({ events }: EventDisplayProps): React.ReactElement {
  const intl = useIntl();
  const eventDisplays: React.ReactElement[] = [];
  groupEventsByStartDate(
    intl,
    events
  ).forEach(({ header, events: groupedEvents }) => {
    eventDisplays.push(<DayHeader key={header} title={header} />);
    eventDisplays.push(
      ...groupedEvents.map(event => (
        <MailEvent key={event.id} event={event as SearchEvent} />
      ))
    );
  });
  return <>{eventDisplays}</>;
}

interface BodyWrapperProps {
  user: { userName: string };
  response: NewSearchResponse;
}

function BodyWrapper({ user, response }: BodyWrapperProps): React.ReactElement {
  // response.results is already SearchEvent[] from NewSearchResponse
  const resultEvents = response.results;

  return (
    <>
      <mj-section key="intro" background-color="#ffffff">
        <mj-column width="100%">
          <mj-text padding="10px 25px">
            <p>
              Hey {user.userName}
              , here's what we've found for you this week!
            </p>
          </mj-text>
        </mj-column>
      </mj-section>
      <EventDisplay key="events" events={resultEvents} />
      <mj-section key="more" background-color="#ffffff">
        <mj-column width="100%">
          <mj-text padding="10px 25px">
            Looking for more events? Be sure to{' '}
            <a href="{{ search_url }}">check out website</a> for the complete
            and up-to-date schedule!
          </mj-text>
        </mj-column>
      </mj-section>
      <mj-section
        key="footer"
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
            That's all we've got for now...see you next week!
          </mj-text>
        </mj-column>
      </mj-section>
    </>
  );
}

interface WeeklyEmailProps {
  user: { userName: string };
  response: NewSearchResponse;
  currentLocale: string;
}

function WeeklyEmail({ user, response }: WeeklyEmailProps): React.ReactElement {
  return (
    <EmailWrapper
      header={`With ${response.results.length} events for Your Week in Dance!`}
      footer={
        <div>
          You may also{' '}
          <a href="https://www.dancedeets.com/user/unsubscribe">
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
      <BodyWrapper user={user} response={response} />
    </EmailWrapper>
  );
}

export default intlWeb(WeeklyEmail);
