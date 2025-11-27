/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';

const accentColor = '#DACCFF';
const primaryBackgroundColor = '#FFFFFF';
const secondaryBackgroundColor = '#4F5086';
const primaryForegroundColor = '#534F4F';
const secondaryForegroundColor = '#EEEEEE';
const footerForegroundColor = '#D5D5D5';
export const buttonBackgroundColor = '#A361CB';
export const buttonForegroundColor = '#FFFFFF';
export const outsideGutter = 30;
export const columnPadding = 15;

export function AltA(props: Object) {
  const { children, ...otherProps } = props;
  // eslint-disable-next-line jsx-a11y/anchor-has-context
  return (
    <a style={{ color: '#9999ff' }} className="alternate" {...otherProps}>
      {children}
    </a>
  );
}

export type User = {
  userName: string,
  city: string,
  countryName: string,
};

export class MobileAppPromo extends React.Component<{
  mobileIosUrl: string,
  mobileAndroidUrl: string,
}> {
  render() {
    return (
      <mj-section padding={`40 ${outsideGutter} 0`}>
        <mj-column>
          <mj-text mj-class="header" padding-bottom="10">
            Find Your Dance on the go
          </mj-text>
          <mj-text padding="10 0">
            Discover over 250,000 battles, parties, workshops, sessions,
            everywhere you go. Find dance events near you by location, time,
            style, and keywords.
          </mj-text>
          <mj-table>
            <tr>
              <td>
                <a href={this.props.mobileIosUrl}>
                  <img
                    alt="Download iPhone/iPad App"
                    src="https://storage.googleapis.com/dancedeets-static/img/mail/mobile-ios-download.png"
                    width="122"
                    style={{ padding: 10 }}
                    border="0"
                  />
                </a>
              </td>
              <td>
                <a href={this.props.mobileAndroidUrl}>
                  <img
                    alt="Download Android App"
                    src="https://storage.googleapis.com/dancedeets-static/img/mail/mobile-android-download.png"
                    width="122"
                    style={{ padding: 10 }}
                    border="0"
                  />
                </a>
              </td>
            </tr>
          </mj-table>
        </mj-column>
        <mj-column>
          <mj-image
            src="https://storage.googleapis.com/dancedeets-static/img/mail/mobile-phones-top.jpg"
            alt=""
            align="center"
            border="none"
            container-background-color="transparent"
            padding-left="30"
          />
        </mj-column>
      </mj-section>
    );
  }
}

type Feature = {
  iconName: string,
  element: React.Element<*>,
};

export class FeaturePromoBase extends React.Component<{
  user: User,
  LinkComponent: React.Component<*>,
  useNewlines: boolean,
}> {
  getFeatures() {
    const features: Array<Feature> = [
      {
        iconName: 'search',
        url: `https://www.dancedeets.com/?location=${this.props.user.city}`,
        element: this.renderSearchElement(),
      },
      {
        iconName: 'calendar-add',
        url: 'https://www.dancedeets.com/events_add',
        element: this.renderAddEventFeature(),
      },
      {
        iconName: 'movie',
        url: 'https://www.dancedeets.com/tutorials',
        element: this.renderMovieFeature(),
      },
    ];
    return features;
  }

  renderSeparator() {
    return this.props.useNewlines ? [<br />, <br />] : [<br />];
  }

  renderSearchElement() {
    const { user, LinkComponent } = this.props;
    const { countryName } = user;
    return (
      <div>
        Planning your next trip?
        {this.renderSeparator()}
        Check all events in{' '}
        <LinkComponent href="https://www.dancedeets.com/?location=NYC">
          NYC
        </LinkComponent>,{' '}
        <LinkComponent href="https://www.dancedeets.com/?location=Paris">
          Paris
        </LinkComponent>, and{' '}
        <LinkComponent href="https://www.dancedeets.com/?location=Los Angeles">
          LA
        </LinkComponent>.
        {this.renderSeparator()}
        Or all events in {countryName} for{' '}
        <LinkComponent
          href={`https://www.dancedeets.com/?location=${countryName}&keywords=breaking`}
        >
          Bboying/Bgirling
        </LinkComponent>
        , {' '}
        <LinkComponent
          href={`https://www.dancedeets.com/?location=${countryName}&keywords=popping`}
        >
          Popping
        </LinkComponent>
        , and {' '}
        <LinkComponent
          href={`https://www.dancedeets.com/?location=${countryName}&keywords=hiphop`}
        >
          Hip-Hop
        </LinkComponent>
      </div>
    );
  }

  renderAddEventFeature() {
    const { LinkComponent } = this.props;
    return (
      <div>
        Got an event you would like to share with more dancers?
        {this.renderSeparator()}
        <LinkComponent href="https://www.dancedeets.com/events_add">
          Add an event
        </LinkComponent>{' '}
        with just a few clicks!
      </div>
    );
  }

  renderMovieFeature() {
    const { LinkComponent } = this.props;
    return (
      <div>
        Check out the{' '}
        <LinkComponent href="https://www.dancedeets.com/tutorials">
          best dance tutorials
        </LinkComponent>{' '}
        we found around the world to help you level up.
        {this.renderSeparator()}
        Whether it’s{' '}
        <LinkComponent href="https://www.dancedeets.com/tutorials/break">
          bboying
        </LinkComponent>,{' '}
        <LinkComponent href="https://www.dancedeets.com/tutorials/pop">
          popping
        </LinkComponent>{' '}
        or{' '}
        <LinkComponent href="https://www.dancedeets.com/tutorials/lock">
          locking
        </LinkComponent>,{' '}
        <LinkComponent href="https://www.dancedeets.com/tutorials/hiphop">
          freestyle hiphop
        </LinkComponent>{' '}
        or{' '}
        <LinkComponent href="https://www.dancedeets.com/tutorials/house">
          house
        </LinkComponent>, we’ve got you covered!
      </div>
    );
  }
}

export class Footer extends React.Component<{
  emailPreferencesUrl: string,
}> {
  render() {
    return [
      <mj-section>
        <mj-column>
          <mj-divider border-color={accentColor} />
        </mj-column>
      </mj-section>,

      <mj-section mj-class="alternate" padding="20 0 0">
        <mj-column mj-class="alternate">
          <mj-table width="100px" align="center">
            <tr>
              <td>
                <a href="https://www.facebook.com/dancedeets">
                  <img
                    src="https://storage.googleapis.com/dancedeets-static/img/mail/social-facebook.png"
                    alt="Facebook"
                    width="30"
                    style={{ margin: '0px 10px' }}
                  />
                </a>
              </td>
              <td>
                <a href="https://www.twitter.com/dancedeets">
                  <img
                    src="https://storage.googleapis.com/dancedeets-static/img/mail/social-twitter.png"
                    alt="Facebook"
                    width="30"
                    style={{ margin: '0px 10px' }}
                  />
                </a>
              </td>
              <td>
                <a href="https://www.instagram.com/dancedeets">
                  <img
                    src="https://storage.googleapis.com/dancedeets-static/img/mail/social-instagram.png"
                    alt="Facebook"
                    width="30"
                    style={{ margin: '0px 10px' }}
                  />
                </a>
              </td>
            </tr>
          </mj-table>
          <mj-text
            align="center"
            mj-class="alternate"
            color={footerForegroundColor}
          >
            <p>Built for and by dancers.</p>
            <p>Sent with ❤ from DanceDeets</p>
            <p>
              <AltA href={this.props.emailPreferencesUrl}>
                Unsubscribe / email preferences
              </AltA>
            </p>
          </mj-text>
        </mj-column>
      </mj-section>,
    ];
  }
}

export class NewEmailWrapper extends React.Component<{
  previewText: string,
  mobileIosUrl: string,
  mobileAndroidUrl: string,
  emailPreferencesUrl: string,
  children: React.Node,
}> {
  render() {
    /*
    I would love to do this...but unfortunately mj-style grabs web-resource-inliner->datauri,
    as well as imagesize (dependent require) and mimer (has a data load),
    all of which don't work well in a precompiled environment.
    So instead, we try to force our alternate-a tags to use a separate component that sets the color directly.
      <mj-style
        // un-inlined link colors don't seem to take sufficient precedence over pseudo-classes
        // pseudo-classes don't seem to render properly on gmail (or others)
        inline="inline"
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{
          __html: `
              a.alternate {
                color: #9999ff;
              }
            `,
        }}
      />
    */
    return (
      <mjml>
        <mj-head>
          <mj-attributes>
            <mj-all
              padding="0px"
              color={primaryForegroundColor}
              background-color={primaryBackgroundColor}
              font-size="13px"
              line-height="20px"
              font-family="Helvetica Nueue, Helvetica, Arial, sans-serif"
            />
            <mj-class name="header" font-size="18px" line-height="26px" />
            <mj-class
              name="alternate"
              background-color={secondaryBackgroundColor}
              color={secondaryForegroundColor}
            />
            <mj-preview>{this.props.previewText}</mj-preview>
          </mj-attributes>
        </mj-head>
        <mj-body>
          <mj-container background-color="#EAEAEA">
            {this.props.children}
            <MobileAppPromo
              mobileAndroidUrl={this.props.mobileAndroidUrl}
              mobileIosUrl={this.props.mobileIosUrl}
            />
            <Footer emailPreferencesUrl={this.props.emailPreferencesUrl} />
          </mj-container>
        </mj-body>
      </mjml>
    );
  }
}

export class EmailWrapper extends React.Component<{
  header: React.Node,
  footer: React.Node,
  children: React.Node,
}> {
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
          <mj-container background-color="#D0D0F0">
            <mj-section full-width="full-width" padding="10px 25px">
              <mj-group>
                <mj-column>
                  <mj-text>{this.props.header}</mj-text>
                </mj-column>
              </mj-group>
            </mj-section>
            <mj-section full-width="full-width">
              <mj-column>
                <mj-image
                  src="https://storage.googleapis.com/dancedeets-static/img/mail-top.png"
                  alt=""
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

            {this.props.children}

            <mj-section>
              <mj-column>
                <mj-image
                  src="https://storage.googleapis.com/dancedeets-static/img/mail-bottom.png"
                  alt=""
                  align="center"
                  border="none"
                  width="600"
                  container-background-color="transparent"
                />
              </mj-column>
            </mj-section>
            <mj-section full-width="full-width" padding="20px">
              <mj-column>
                <mj-text align="center">{this.props.footer}</mj-text>
              </mj-column>
            </mj-section>
          </mj-container>
        </mj-body>
      </mjml>
    );
  }
}
