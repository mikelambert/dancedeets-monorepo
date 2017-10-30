/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { intlWeb } from 'dancedeets-common/js/intl';
import { Event, SearchEvent } from 'dancedeets-common/js/events/models';
// import { addUrlArgs } from 'dancedeets-common/js/util/url';
import {
  NewEmailWrapper,
  buttonBackgroundColor,
  buttonForegroundColor,
  columnPadding,
  outsideGutter,
} from './mailCommon';
import { EventDisplay } from './weeklyMail';

type User = {
  userName: string,
  city: string,
  countryName: string,
};

class NavHeader extends React.Component {
  render() {
    return (
      <mj-section mj-class="alternate">
        <mj-column
          width="30%"
          mj-class="alternate"
          background-color="transparent"
          vertical-align="middle"
        >
          <mj-image src="https://static.dancedeets.com/img/mail/header-dancedeets.png" />
        </mj-column>
        <mj-column width="70%" mj-class="alternate" vertical-align="middle">
          <mj-raw>
            <style
              // eslint-disable-next-line react/no-danger
              dangerouslySetInnerHTML={{
                __html: `
                  a.alternate-header-link:link,
                  a.alternate-header-link:visited,
                  a.alternate-header-link:hover,
                  a.alternate-header-link:active
                  {
                    color: #ffffff;
                    text-decoration: none;
                    margin-left: 10px;
                  }
                `,
              }}
            />
          </mj-raw>
          <mj-text
            mj-class="alternate"
            align="right"
            padding-right="20"
            height="100%"
          >
            <a
              href="https://www.dancedeets.com/"
              className="alternate-header-link"
            >
              HOME
            </a>&nbsp;
            <a
              href="https://medium.dancedeets.com/"
              className="alternate-header-link"
            >
              ARTICLES
            </a>&nbsp;
            <a
              href="https://www.dancedeets.com/tutorials"
              className="alternate-header-link"
            >
              TUTORIALS
            </a>&nbsp;
            <a
              href="https://www.dancedeets.com/about"
              className="alternate-header-link"
            >
              ABOUT
            </a>
          </mj-text>
        </mj-column>
      </mj-section>
    );
  }
}

class MainBody extends React.Component {
  props: {
    user: User,
    response: NewSearchResponse,
  };

  render() {
    const resultEvents = this.props.response.results.map(
      eventData => new SearchEvent(eventData)
    );
    return [
      <mj-section>
        <mj-column>
          <mj-text padding={`10px ${outsideGutter}`}>
            Hey {this.props.user.userName},
            <br />
            <br />
            We’ve found {resultEvents.length} events near {this.props.user.city}{' '}
            for you this week. Get ready to dance!
          </mj-text>
        </mj-column>
      </mj-section>,
      <EventDisplay events={resultEvents} />,
      <mj-section background-color="#ffffff">
        <mj-column width="100%">
          <mj-text padding={`10 ${outsideGutter}`}>
            Looking for more events? Be sure to check out{' '}
            <a href="https://www.dancedeets.com/">www.dancedeets.com</a> for the
            complete and up-to-date schedule!
            <br />
            <br />
            Not in {this.props.user.city}?{' '}
            <a href="https://www.dancedeets.com/user/edit">
              Change your preferred location
            </a>.
          </mj-text>
        </mj-column>
      </mj-section>,
    ];
  }
}

class HeaderFindYourDance extends React.Component {
  render() {
    return (
      <mj-section mj-class="alternate">
        <mj-column mj-class="alternate">
          <mj-image src="https://static.dancedeets.com/img/mail/header-find-your-dance.jpg" />
        </mj-column>
      </mj-section>
    );
  }
}

class FeaturePromo extends React.Component {
  props: {
    user: User,
  };
  render() {
    const countryName = this.props.user.countryName;
    return (
      <mj-wrapper mj-class="alternate" padding={`10 ${outsideGutter}`}>
        <mj-section mj-class="alternate" padding="20 0">
          <mj-column mj-class="alternate">
            <mj-text mj-class="alternate" align="center" font-size="16px">
              Explore more on DanceDeets...
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <mj-image
              src="https://static.dancedeets.com/img/mail/purple-icons/search.png"
              width="80"
              height="80"
              padding-bottom="20"
            />
            <mj-text mj-class="alternate" padding-right={columnPadding}>
              Planning your next trip?
              <p />
              Check all events in{' '}
              <a
                href="https://www.dancedeets.com/?location=NYC"
                class="alternate"
              >
                NYC
              </a>,{' '}
              <a
                href="https://www.dancedeets.com/?location=Paris"
                class="alternate"
              >
                Paris
              </a>, and{' '}
              <a
                href="https://www.dancedeets.com/?location=Los Angeles"
                class="alternate"
              >
                LA
              </a>.<br />
              <br />Or all events in {countryName} for:<br />
              <ul>
                <li>
                  <a
                    href={`https://www.dancedeets.com/?location=${countryName}&keywords=breaking`}
                    class="alternate"
                  >
                    Bboying/Bgirling
                  </a>
                </li>
                <li>
                  <a
                    href={`https://www.dancedeets.com/?location=${countryName}&keywords=popping`}
                    class="alternate"
                  >
                    Popping
                  </a>
                </li>
                <li>
                  <a
                    href={`https://www.dancedeets.com/?location=${countryName}&keywords=hiphop`}
                    class="alternate"
                  >
                    Hip-Hop
                  </a>
                </li>
              </ul>
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <mj-image
              src="https://static.dancedeets.com/img/mail/purple-icons/calendar-add.png"
              width="80"
              height="80"
              padding-bottom="20"
            />
            <mj-text
              mj-class="alternate"
              padding-left={columnPadding}
              padding-right={columnPadding}
            >
              Got an event you would like to share with more dancers?<br />
              <br />
              <a href="https://www.dancedeets.com/events_add" class="alternate">
                Add an event
              </a>{' '}
              with just a few clicks!
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <mj-image
              src="https://static.dancedeets.com/img/mail/purple-icons/movie.png"
              width="80"
              height="80"
              padding-bottom="20"
            />
            <mj-text mj-class="alternate" padding-left={columnPadding}>
              Check out the{' '}
              <a href="https://www.dancedeets.com/tutorials" class="alternate">
                best dance tutorials
              </a>{' '}
              we found around the world to help you level up.
              <br />
              <br />
              Whether it's{' '}
              <a
                href="https://www.dancedeets.com/tutorials/break"
                class="alternate"
              >
                bboying
              </a>,{' '}
              <a
                href="https://www.dancedeets.com/tutorials/pop"
                class="alternate"
              >
                popping
              </a>{' '}
              or{' '}
              <a
                href="https://www.dancedeets.com/tutorials/lock"
                class="alternate"
              >
                locking
              </a>,{' '}
              <a
                href="https://www.dancedeets.com/tutorials/hiphop"
                class="alternate"
              >
                freestyle hiphop
              </a>{' '}
              or{' '}
              <a
                href="https://www.dancedeets.com/tutorials/house"
                class="alternate"
              >
                house
              </a>, we've got you covered!
            </mj-text>
          </mj-column>
        </mj-section>
      </mj-wrapper>
    );
  }
}

class BodyWrapper extends React.Component {
  props: {
    user: User,
    response: NewSearchResponse,
  };

  render() {
    return [
      <NavHeader />,
      <HeaderFindYourDance />,
      <MainBody user={this.props.user} response={this.props.response} />,
      <FeaturePromo user={this.props.user} />,
    ];
  }
}

class AddEventEmail extends React.Component {
  props: {
    user: User,
    response: NewSearchResponse,

    mobileIosUrl: string,
    mobileAndroidUrl: string,
    emailPreferencesUrl: string,
  };

  render() {
    return (
      <NewEmailWrapper
        previewText={`With ${this.props.response.results
          .length} events for Your Week in Dance!`}
        mobileIosUrl={this.props.mobileIosUrl}
        mobileAndroidUrl={this.props.mobileAndroidUrl}
        emailPreferencesUrl={this.props.emailPreferencesUrl}
      >
        <BodyWrapper user={this.props.user} response={this.props.response} />
      </NewEmailWrapper>
    );
  }
}

export default intlWeb(AddEventEmail);
