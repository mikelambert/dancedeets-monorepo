/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { intlWeb } from 'dancedeets-common/js/intl';
import { Event } from 'dancedeets-common/js/events/models';
// import { addUrlArgs } from 'dancedeets-common/js/util/url';
import {
  NewEmailWrapper,
  buttonBackgroundColor,
  buttonForegroundColor,
} from './mailCommon';

class GenericCircle extends React.Component {
  render() {
    return (
      <img
        alt="•"
        src="https://static.dancedeets.com/img/mail/purple-circle.png"
        width="36px"
        height="36px"
      />
    );
  }
}

class SellingPoint extends React.Component {
  props: {
    title: string,
    contents: string,
  };

  render() {
    return [
      <mj-table container-background-color="transparent">
        <tr>
          <td style={{ width: 36 }}>
            <GenericCircle />
          </td>
          <td style={{ fontWeight: 'bold', paddingLeft: 20 }}>
            {this.props.title}
          </td>
        </tr>
      </mj-table>,
      <mj-text>{this.props.contents}</mj-text>,
    ];
  }
}

class Upsell extends React.Component {
  render() {
    return [
      <mj-section
        mj-class="alternate"
        padding="0 30"
        background-url="https://static.dancedeets.com/img/mail/white-background-height.png"
        background-repeat="repeat-x"
      >
        <mj-group mj-class="alternate" background-color="transparent">
          <mj-column mj-class="alternate" background-color="transparent">
            <mj-spacer height="120px" />
            <mj-text
              mj-class="alternate"
              background-color="transparent"
              align="center"
            >
              Want to be a featured event?
            </mj-text>
            <mj-text
              mj-class="alternate"
              background-color="transparent"
              align="center"
              font-style="italic"
              font-size="20px"
              padding-top="20px"
            >
              Collaborate with us!
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate" background-color="transparent">
            <mj-image
              src="https://static.dancedeets.com/img/mail/mobile-phone-featured-event.png"
              width="200px"
            />
          </mj-column>
        </mj-group>
      </mj-section>,

      <mj-section padding="20 30">
        <mj-column>
          <SellingPoint
            title="THE most influencial dance event platform"
            contents="Over 250,000 events around the world, visited by over 50,000 dancers every month."
          />
        </mj-column>
        <mj-column>
          <SellingPoint
            title="Maximum exposure on multiple channels"
            contents="Website, mobile apps, Facebook, Instagram, Twitter… We will push your event to everywhere dancers look."
          />
        </mj-column>
      </mj-section>,
      <mj-section padding="0 30">
        <mj-column>
          <SellingPoint
            title="Ongoing event promotion support"
            contents="We will post/share footage and event recap after the event, to our 8,000 global followers on Facebook."
          />
        </mj-column>
        <mj-column>
          <SellingPoint
            title="Completely free!"
            contents="No fee! All you need to do is to help spread DanceDeets’ name to your local dancers.."
          />
        </mj-column>
      </mj-section>,
      <mj-section padding="0 20 30">
        <mj-column>
          <mj-button
            href="mailto:partnering@dancedeets.com"
            align="center"
            background-color={buttonBackgroundColor}
            color={buttonForegroundColor}
            height="25px"
            border-radius="30px"
          >
            Get in Touch
          </mj-button>
        </mj-column>
      </mj-section>,
    ];
  }
}

class ImageThumbnail extends React.Component {
  props: {
    imageName: string,
  };

  render() {
    const imageUrl = `https://static.dancedeets.com/img/mail/${this.props
      .imageName}`;
    return <mj-image src={imageUrl} width="100px" height="100px" />;
  }
}

class EventTestimonials extends React.Component {
  render() {
    return (
      <mj-wrapper mj-class="alternate" padding="10 30">
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <mj-text mj-class="alternate" align="center">
              Events we have worked with:
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="events/sygu.jpg" />
            <mj-text mj-class="alternate" align="center">
              Step Ya Game Up
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="events/lohh.png" />
            <mj-text mj-class="alternate" align="center">
              Ladies of Hip-Hop
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="events/ssl.png" />
            <mj-text mj-class="alternate" align="center">
              Street Style Lab
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <mj-text mj-class="alternate" align="center">
              Testimonials:
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="testimonials/nedric.jpg" />
            <mj-text mj-class="alternate">
              Looking forward to working with DanceDeets on my next event!
            </mj-text>
            <mj-text mj-class="alternate">
              Nedric Johnson<br />Juste Debout NYC
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="testimonials/stretch.jpg" />
            <mj-text mj-class="alternate">
              I tell dancers to check DanceDeets for events in this scene...
            </mj-text>
            <mj-text mj-class="alternate">
              Buddha Stretch<br />Elite Force, MOPTOP
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="testimonials/carlo.jpg" />
            <mj-text mj-class="alternate">
              More promoters need to start working with DanceDeets!
            </mj-text>
            <mj-text mj-class="alternate">
              Carlo C-Lo<br />Electro Soul, Top Status
            </mj-text>
          </mj-column>
        </mj-section>
      </mj-wrapper>
    );
  }
}

class BodyWrapper extends React.Component {
  props: {
    event: Event,
    // organizerEmail: string,
    organizerName: string,
  };

  render() {
    const event = this.props.event;
    /*
    const args = {
      utm_source: 'event_add',
      utm_medium: 'email',
      utm_campaign: 'event_add',
    };
    */
    const shortUrl = `https://dd.events/e/${event.id}`;
    const address = event.venue.address;
    let city = 'your city';
    if (address && address.city) {
      city = `the ${address.city} area`;
    }
    // TODO: Handle 'intro email' different from 'second email'
    return [
      <mj-section mj-class="alternate">
        <mj-column mj-class="alternate" full-width="full-width">
          <mj-image src="https://static.dancedeets.com/img/mail/header-flyers.jpg" />
        </mj-column>
      </mj-section>,
      <mj-section padding="10 30 0">
        <mj-column full-width="full-width">
          <mj-text>
            <p>Hi there {this.props.organizerName},</p>
            <p>
              We want to help promote your new event and help grow our dance
              scene:
            </p>
            <p>“{event.name}”</p>
            <p>
              To start, we&#8217;ve added your event to DanceDeets, the
              world&#8217;s biggest street dance event platform:
            </p>
          </mj-text>
          <mj-button
            href={shortUrl}
            align="center"
            background-color={buttonBackgroundColor}
            color={buttonForegroundColor}
            height="25px"
            border-radius="30px"
          >
            View Your Event
          </mj-button>
          <mj-text>
            <p>What does this mean for you?</p>
          </mj-text>

          <mj-table>
            <tr>
              <td style={{ verticalAlign: 'top' }}>
                <GenericCircle />
              </td>
              <td style={{ paddingLeft: 20, paddingBottom: 20 }}>
                Your event is now accessible on dancedeets.com and our mobile
                app, for the 50,000+ dancers that visit us every month. Even if
                they don&#8217;t use Facebook.
              </td>
            </tr>
            <tr>
              <td style={{ verticalAlign: 'top' }}>
                <GenericCircle />
              </td>
              <td style={{ paddingLeft: 20, paddingBottom: 20 }}>
                Easily discoverable by dancers living in {city} (or those just
                visiting!), as well as new dancers looking to get into the
                scene.
              </td>
            </tr>
            <tr>
              <td style={{ verticalAlign: 'top' }}>
                <GenericCircle />
              </td>
              <td style={{ paddingLeft: 20, paddingBottom: 20 }}>
                We&#8217;ve published information about your event to Google and{' '}
                <a href="https://twitter.com/dancedeets">Twitter</a>, so dancers
                can find information about your event, no matter where they
                look.
              </td>
            </tr>
          </mj-table>

          <mj-text font-weight="bold">Want more promotion? Read on…</mj-text>
        </mj-column>
      </mj-section>,
      <Upsell />,
      <EventTestimonials />,
    ];
  }
}

class AddEventEmail extends React.Component {
  props: {
    event: Event,
    organizerEmail: string,
    organizerName: string,

    mobileIosUrl: string,
    mobileAndroidUrl: string,
    emailPreferencesUrl: string,
  };

  render() {
    const event = new Event(this.props.event);
    return (
      <NewEmailWrapper
        previewText={`We want to help promote your event!`}
        mobileIosUrl={this.props.mobileIosUrl}
        mobileAndroidUrl={this.props.mobileAndroidUrl}
        emailPreferencesUrl={this.props.emailPreferencesUrl}
      >
        <BodyWrapper
          event={event}
          organizerEmail={this.props.organizerEmail}
          organizerName={this.props.organizerName}
        />
      </NewEmailWrapper>
    );
  }
}

export default intlWeb(AddEventEmail);
