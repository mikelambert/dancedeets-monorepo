/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { intlWeb } from 'dancedeets-common/js/intl';
import { SearchEvent } from 'dancedeets-common/js/events/models';
import type { NewSearchResponse } from 'dancedeets-common/js/events/search';
// import { addUrlArgs } from 'dancedeets-common/js/util/url';
import {
  FeaturePromoBase,
  NewEmailWrapper,
  columnPadding,
  outsideGutter,
} from './mailCommon';
import { EventDisplay } from './weeklyMail';
import type { User } from './mailCommon';

export class NavHeader extends React.Component<{}> {
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

class MainBody extends React.Component<{
  user: User,
  response: NewSearchResponse,
}> {
  render() {
    const resultEvents = this.props.response.results.map(
      eventData => new SearchEvent(eventData)
    );
    return [
      <mj-section>
        <mj-column>
          <mj-text padding={`20px ${outsideGutter}`}>
            Hey {this.props.user.userName},
            <br />
            <br />
            We’ve found {resultEvents.length} events near {this.props.user.city}{' '}
            for you this week. Get ready to dance!
          </mj-text>
        </mj-column>
      </mj-section>,
      <EventDisplay events={resultEvents} />,
      <mj-section>
        <mj-column>
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

export class HeaderFindYourDance extends React.Component<{}> {
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

class AlternateFeaturePromo extends FeaturePromoBase {
  render() {
    const features = this.getFeatures();
    return (
      <mj-wrapper mj-class="alternate" padding={`30 ${outsideGutter}`}>
        <mj-section mj-class="alternate" padding="0 0 10">
          <mj-column mj-class="alternate">
            <mj-text mj-class="alternate" align="center" font-size="16px">
              Explore more on DanceDeets...
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <mj-image
              src={`https://static.dancedeets.com/img/mail/purple-icons/${features[0]
                .iconName}.png`}
              href={features[0].url}
              width="80px"
              height="80px"
              padding-bottom="20"
            />
            <mj-text mj-class="alternate" padding-right={columnPadding}>
              {features[0].element}
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <mj-image
              src={`https://static.dancedeets.com/img/mail/purple-icons/${features[1]
                .iconName}.png`}
              href={features[1].url}
              width="80px"
              height="80px"
              padding-bottom="20"
            />
            <mj-text
              mj-class="alternate"
              padding-left={columnPadding}
              padding-right={columnPadding}
            >
              {features[1].element}
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <mj-image
              src={`https://static.dancedeets.com/img/mail/purple-icons/${features[2]
                .iconName}.png`}
              href={features[2].url}
              width="80px"
              height="80px"
              padding-bottom="20"
            />
            <mj-text mj-class="alternate" padding-left={columnPadding}>
              {features[2].element}
            </mj-text>
          </mj-column>
        </mj-section>
      </mj-wrapper>
    );
  }
}

class BodyWrapper extends React.Component<{
  user: User,
  response: NewSearchResponse,
}> {
  render() {
    return [
      <NavHeader />,
      <HeaderFindYourDance />,
      <MainBody user={this.props.user} response={this.props.response} />,
      <AlternateFeaturePromo
        user={this.props.user}
        className="alternate"
        useNewlines
      />,
    ];
  }
}

class AddEventEmail extends React.Component<{
  user: User,
  response: NewSearchResponse,

  mobileIosUrl: string,
  mobileAndroidUrl: string,
  emailPreferencesUrl: string,
}> {
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
