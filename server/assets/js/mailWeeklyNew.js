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
    user: any,
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
  render() {
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
              Start planning your next trip! Here are some ideas...
              <p />
              All events in:
              <ul>
                <li>
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
                  </a>
                </li>
              </ul>
              Search for dance styles across the country:
              <ul>
                <li>
                  <a
                    href="https://www.dancedeets.com/?location=Taiwan&keywords=locking"
                    class="alternate"
                  >
                    Locking in Taiwan
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.dancedeets.com/?location=France&keywords=popping"
                    class="alternate"
                  >
                    Popping in France
                  </a>
                </li>
              </ul>
              Follow dancers, crews, and event tours:
              <ul>
                <li>
                  <a
                    href="https://www.dancedeets.com/?keywords=icee"
                    class="alternate"
                  >
                    Icee
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.dancedeets.com/?keywords=%22lyle beniga%22"
                    class="alternate"
                  >
                    Lyle Beniga
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.dancedeets.com/?keywords=%22elite force%22"
                    class="alternate"
                  >
                    Elite Force
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.dancedeets.com/?keywords=%22wanted posse%22"
                    class="alternate"
                  >
                    Wanted Posse
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.dancedeets.com/?keywords=udef"
                    class="alternate"
                  >
                    the UDEF Tour
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.dancedeets.com/?keywords==%22red bull bc one%22"
                    class="alternate"
                  >
                    Red Bull BC One
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
              Got an event you would like to share with more dancers?<a
                href="https://www.dancedeets.com/events_add"
                class="alternate"
              >
                {' '}
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
              <p />
              Bboying/bgirling:
              <ul>
                <li>VincaniTV</li>
                <li>Storm's Footwork</li>
              </ul>
              Freestyle hiphop:
              <ul>
                <li>Elite Force 1990s</li>
                <li>Ill Kozby</li>
              </ul>
              House dance:
              <ul>
                <li>Elite Force 1990s</li>
                <li>Elite Force 2010s</li>
                <li>Jardy Santiago</li>
              </ul>
              Popping:
              <ul>
                <li>Popin Pete &amp; Skeeter Rabbit</li>
                <li>Oakland Boogaloo</li>
              </ul>
              Locking:
              <ul>
                <li>Skeeter Rabbit &amp; Flomaster</li>
                <li>Tony Gogo</li>
              </ul>
            </mj-text>
          </mj-column>
        </mj-section>
      </mj-wrapper>
    );
  }
}

class BodyWrapper extends React.Component {
  props: {
    user: any,
    response: NewSearchResponse,
  };

  render() {
    return [
      <NavHeader />,
      <HeaderFindYourDance />,
      <MainBody user={this.props.user} response={this.props.response} />,
      <FeaturePromo />,
    ];
  }
}

class AddEventEmail extends React.Component {
  props: {
    user: any,
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
