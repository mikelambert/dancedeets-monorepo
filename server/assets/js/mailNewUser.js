/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { intlWeb } from 'dancedeets-common/js/intl';
// import { addUrlArgs } from 'dancedeets-common/js/util/url';
import { ImageThumbnail } from './mailAddEvent';
import { NavHeader, HeaderFindYourDance } from './mailWeeklyNew';
import type { User } from './mailWeeklyNew';
import {
  NewEmailWrapper,
  buttonBackgroundColor,
  buttonForegroundColor,
  columnPadding,
  outsideGutter,
} from './mailCommon';

class MainBody extends React.Component<{
  user: User,
}> {
  render() {
    return (
      <mj-section>
        <mj-column>
          <mj-text padding={`10px ${outsideGutter}`}>
            Hey {this.props.user.userName},
            <br />
            <br />
            Welcome to DanceDeets, the world’s biggest street dance event
            platform. You have found the gateway to over 250,000 street dance
            events around the world.
            <br />
            <br />
            DanceDeets was made by and for dancers. As dancers ourselves, we
            realized it was extremely difficult to jump into this dance scene,
            where the information was very much underground. What studios offer
            hiphop classes? What are the biggest battles next month? What party
            is popping this Friday night? DanceDeets wants to solving these
            problems by connecting dancers to the dance world.
            <br />
            <br />
            We appreciate your passion for dance. Now, let us help you take that
            passion to the dance floor…
          </mj-text>

          <mj-button
            href="https://www.dancedeets.com/"
            align="center"
            background-color={buttonBackgroundColor}
            color={buttonForegroundColor}
            height="25px"
            border-radius="30px"
            padding="20px 0px"
          >
            Find Your Dance Now
          </mj-button>
        </mj-column>
      </mj-section>
    );
  }
}

class UserTestimonials extends React.Component<{}> {
  render() {
    return (
      <mj-wrapper mj-class="alternate" padding={`10 ${outsideGutter}`}>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="testimonials/roxit.png" />
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding-right={columnPadding}
            >
              “I can’t imagine my life without DanceDeets. Five years ago, when
              I just started dancing, it was DanceDeets who led me into the
              scene!”
            </mj-text>
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding="10 0 0"
            >
              Keane Rox-it Rowley
              <br />
              Indianapolis, IL, USA
            </mj-text>
          </mj-column>

          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="testimonials/tomas.png" />
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding-left={columnPadding}
              padding-right={columnPadding}
            >
              “DanceDeets is <i>the</i> place to find dance events when you
              travel! More dancers need to be using this!”
            </mj-text>
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding="10 0 0"
            >
              Buddha Stretch<br />
              <a
                href="https://www.facebook.com/ELITEFORCECREW/"
                className="alternate"
              >
                Elite Force
              </a>
              <br />New York City, NY, USA
            </mj-text>
          </mj-column>

          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="testimonials/elena.png" />
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding-left={columnPadding}
            >
              “This has helped me countless times when travelling overseas, and
              helps me find out what’s going on in the local dance communities!”
            </mj-text>
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding="10 0 0"
            >
              Elanna Smith<br />
              <a
                href="https://www.facebook.com/ElectricFunketeers/"
                className="alternate"
              >
                Electric Funketeers
              </a>
              <br />
              Chicago, USA
            </mj-text>
          </mj-column>
        </mj-section>
      </mj-wrapper>
    );
  }
}

class BodyWrapper extends React.Component<{
  user: User,
}> {
  render() {
    return [
      <NavHeader />,
      <HeaderFindYourDance />,
      <MainBody user={this.props.user} />,
      <UserTestimonials />,
    ];
  }
}

class NewUserEmail extends React.Component<{
  user: User,

  mobileIosUrl: string,
  mobileAndroidUrl: string,
  emailPreferencesUrl: string,
}> {
  render() {
    return (
      <NewEmailWrapper
        previewText="Find your dance. Anywhere."
        mobileIosUrl={this.props.mobileIosUrl}
        mobileAndroidUrl={this.props.mobileAndroidUrl}
        emailPreferencesUrl={this.props.emailPreferencesUrl}
      >
        <BodyWrapper user={this.props.user} />
      </NewEmailWrapper>
    );
  }
}

export default intlWeb(NewUserEmail);
