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
} from './mailCommon';
import { EventDisplay } from './weeklyMail';

class NavHeader extends React.Component {
  render() {
    return (
      <mj-navbar mj-class="alternate">
        <mj-column
          width="20%"
          mj-class="alternate"
          background-color="transparent"
        >
          <mj-image src="https://static.dancedeets.com/img/mail/header-dancedeets.png" />
        </mj-column>
        <mj-column width="80%" mj-class="alternate">
          <mj-inline-links base-url="https://www.dancedeets.com">
            <mj-link href="/" mj-class="alternate">
              HOME
            </mj-link>
            <mj-link href="https://medium.dancedeets.com" mj-class="alternate">
              BLOG
            </mj-link>
            <mj-link href="/tutorials" mj-class="alternate">
              TUTORIALS
            </mj-link>
            <mj-link href="/about" mj-class="alternate">
              ABOUT US
            </mj-link>
          </mj-inline-links>
        </mj-column>
      </mj-navbar>
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
          <mj-text padding="10px 25px">
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
          <mj-text padding="10px 25px">
            Looking for more events? Be sure to check out
            <a href="https://www.dancedeets.com/">www.dancedeets.com</a> for the
            complete and up-to-date schedule!
          </mj-text>
        </mj-column>
      </mj-section>,
    ];
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
