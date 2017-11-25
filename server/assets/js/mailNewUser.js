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
import type { User } from './mailCommon';
import {
  FeaturePromoBase,
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
          <mj-text padding={`20px ${outsideGutter}`}>
            Hey {this.props.user.userName},
            <br />
            <br />
            Welcome to DanceDeets, the world’s biggest street dance event
            platform. The gateway to over 250,000 street dance events worldwide.
            <br />
            <br />
            DanceDeets was made for and by dancers. As dancers ourselves, we
            realized how difficult it is to find the dance scene when traveling,
            and how hard it was to jump into the scene when we first started.
            <ul>
              <li>Who’s teaching workshops nearby?</li>
              <li>What are the biggest battles next month?</li>
              <li>Where are the dance parties this weekend?</li>
            </ul>
            DanceDeets wants to solving these problems by connecting dancers
            with the dance communities worldwide.
            <br />
            <br />
            We love and share your passion for dance. Now, let us help you bring
            that passion to the dance floor…
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
      <mj-wrapper mj-class="alternate" padding={`20 ${outsideGutter}`}>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="testimonials/stretch.png" />
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding-right={columnPadding}
            >
              “DanceDeets is <i>the</i> place to find street dance events, at
              home and when traveling! More dancers need to be using this!”
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
            <ImageThumbnail imageName="testimonials/roxit.png" />
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding-left={columnPadding}
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
            <ImageThumbnail imageName="testimonials/jasey.png" />
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
              Jasey<br />
              <br />Sydney, Australia
            </mj-text>
          </mj-column>
        </mj-section>
      </mj-wrapper>
    );
  }
}

class FeaturePromo extends FeaturePromoBase {
  render() {
    const features = this.getFeatures();
    return (
      <mj-section>
        <mj-column>
          <mj-table padding-left="40" padding-right="40">
            {features.map(feature => (
              <tr>
                <td style={{ verticalAlign: 'top' }}>
                  <a href={feature.url}>
                    <img
                      src={`https://static.dancedeets.com/img/mail/purple-icons/${feature.iconName}.png`}
                      alt=""
                      width="80"
                      height="80"
                      style={{ paddingBottom: 20 }}
                    />
                  </a>
                </td>
                <td style={{ paddingLeft: 20, paddingBottom: 20 }}>
                  {feature.element}
                </td>
              </tr>
            ))}
          </mj-table>
        </mj-column>
      </mj-section>
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
      <FeaturePromo
        user={this.props.user}
        LinkComponent="a"
        useNewlines={false}
      />,
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
