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
            Looking for more events? Be sure to check out
            <a href="https://www.dancedeets.com/">www.dancedeets.com</a> for the
            complete and up-to-date schedule!
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
