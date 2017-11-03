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
  columnPadding,
  outsideGutter,
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
    placement: 'left' | 'right',
  };

  render() {
    const paddings = {
      'padding-left': this.props.placement === 'right' ? 10 : 0,
      'padding-right': this.props.placement === 'left' ? 10 : 0,
    };
    return [
      <mj-table container-background-color="transparent" {...paddings}>
        <tr>
          <td style={{ width: 36 }}>
            <GenericCircle />
          </td>
          <td style={{ fontSize: 15, paddingLeft: 20 }}>{this.props.title}</td>
        </tr>
      </mj-table>,
      <mj-spacer height="20px" />,
      <mj-text {...paddings}>{this.props.contents}</mj-text>,
    ];
  }
}

class Upsell extends React.Component {
  render() {
    return [
      <mj-section
        mj-class="alternate"
        padding={`0 ${outsideGutter}`}
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

      <mj-section padding={`40 ${outsideGutter}`}>
        <mj-column>
          <SellingPoint
            title="THE most influencial dance event platform"
            contents="Over 250,000 events around the world, visited by over 50,000 dancers every month."
            placement="left"
          />
        </mj-column>
        <mj-column>
          <SellingPoint
            title="Maximum exposure on multiple channels"
            contents="Website, mobile apps, Facebook, Instagram, Twitter… We will push your event to everywhere dancers look."
            placement="right"
          />
        </mj-column>
      </mj-section>,
      <mj-section padding={`0 ${outsideGutter}`}>
        <mj-column>
          <SellingPoint
            title="Ongoing event promotion support"
            contents="We will post/share footage and event recap after the event, to our 8,000 global followers on Facebook."
            placement="left"
          />
        </mj-column>
        <mj-column>
          <SellingPoint
            title="Completely free!"
            contents="No fee! All you need to do is to help spread DanceDeets’ name to your local dancers.."
            placement="right"
          />
        </mj-column>
      </mj-section>,
      <mj-section padding={`0 ${outsideGutter} 30`}>
        <mj-column>
          <mj-button
            href="mailto:partnering@dancedeets.com"
            align="center"
            background-color={buttonBackgroundColor}
            color={buttonForegroundColor}
            height="25px"
            border-radius="30px"
            padding="20px 0px"
          >
            Get in Touch
          </mj-button>
        </mj-column>
      </mj-section>,
    ];
  }
}

export class ImageThumbnail extends React.Component {
  props: {
    imageName: string,
  };

  render() {
    const imageUrl = `https://static.dancedeets.com/img/mail/${this.props
      .imageName}`;
    return (
      <mj-image src={imageUrl} width="80px" height="80px" padding-bottom="20" />
    );
  }
}

class EventTestimonials extends React.Component {
  render() {
    return (
      <mj-wrapper mj-class="alternate" padding={`10 ${outsideGutter}`}>
        <mj-section mj-class="alternate" padding="20 0">
          <mj-column mj-class="alternate">
            <mj-text mj-class="alternate" align="center" font-size="16px">
              Events we have worked with:
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="events/event1.png" />
            <mj-text mj-class="alternate" align="center">
              Step Ya Game Up
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="events/event2.png" />
            <mj-text mj-class="alternate" align="center">
              Street Style Lab
            </mj-text>
          </mj-column>
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="events/event3.png" />
            <mj-text mj-class="alternate" align="center">
              Ladies of Hip-Hop
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section mj-class="alternate" padding="40 0 20">
          <mj-column mj-class="alternate">
            <mj-text mj-class="alternate" align="center" font-size="16px">
              Testimonials:
            </mj-text>
          </mj-column>
        </mj-section>
        <mj-section mj-class="alternate">
          <mj-column mj-class="alternate">
            <ImageThumbnail imageName="testimonials/terry.png" />
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding-right={columnPadding}
            >
              “Promoting is all about increasing your reach, being seen by more
              regular everyday people, dancers, potential sponsors, etc.
              Everyone who matters in this scene is on DanceDeets, that&#8217;s
              why I put my events there!”
            </mj-text>
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding="10 0 0"
            >
              Brooklyn Terry<br />
              <a
                href="https://www.facebook.com/ELITEFORCECREW/"
                className="alternate"
              >
                Elite Force
              </a>
              <br />
              <a
                href="https://www.facebook.com/SpeakeasyTYO"
                className="alternate"
              >
                Speakeasy TYO
              </a>
              <br />
              Tokyo, Japan
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
              “We had dancers from Russia coming to our jam in Norway because
              they found it on DanceDeets!”
            </mj-text>
            <mj-text
              mj-class="alternate"
              font-size="11px"
              align="center"
              padding="10 0 0"
            >
              Tomas Vikeland<br />
              <a
                href="https://www.facebook.com/midtnorsk.urban.dans"
                className="alternate"
              >
                Midtnorsk Urban Dans
              </a>
              <br />Trondheim, Norway
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
              “Promoting on DanceDeets was really easy and smooth, only took a
              few minutes!”
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

class HeaderFlyers extends React.Component {
  render() {
    return (
      <mj-section mj-class="alternate">
        <mj-column mj-class="alternate" full-width="full-width">
          <mj-image src="https://static.dancedeets.com/img/mail/header-flyers.jpg" />
        </mj-column>
      </mj-section>
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
    let hiThere = 'Hi there,';
    if (this.props.organizerName) {
      hiThere = `Hi there ${this.props.organizerName},`;
    }
    // TODO: Handle 'intro email' different from 'second email'
    return [
      <HeaderFlyers />,
      <mj-section padding={`10 ${outsideGutter} 0`}>
        <mj-column full-width="full-width">
          <mj-text>
            <p>{hiThere}</p>
            <p>
              We want to help promote your new event, and grow our dance scene:
            </p>
            <p style={{ paddingLeft: 20 }}>“{event.name}”</p>
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
            padding="20px 0px"
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
                Your event is now accessible on{' '}
                <a href="https://www.dancedeets.com">dancedeets.com</a> and our
                mobile app, for the 50,000+ dancers that visit us every month.
                Even if they don&#8217;t use Facebook.
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
    organizer: {
      email: string,
      name: string,
    },

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
          organizerEmail={this.props.organizer.email}
          organizerName={this.props.organizer.name}
        />
      </NewEmailWrapper>
    );
  }
}

export default intlWeb(AddEventEmail);
