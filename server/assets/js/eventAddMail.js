/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { intlWeb } from 'dancedeets-common/js/intl';
import { Event } from 'dancedeets-common/js/events/models';
// import { addUrlArgs } from 'dancedeets-common/js/util/url';
import { NewEmailWrapper, buttonColor } from './mailCommon';

class GenericCircle extends React.Component {
  render() {
    return (
      <mj-image
        src="https://static.dancedeets.com/img/mail/purple-circle.png"
        width="50px"
        height="50px"
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
      <mj-table>
        <tr>
          <td>
            <GenericCircle />
          </td>
          <td style={{ fontWeight: 'bold' }}>
            <mj-text>{this.props.title}</mj-text>
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
      <mj-section>
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
      <mj-section>
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
      <mj-section>
        <mj-column>
          <mj-button
            href="mailto:partnering@dancedeets.com"
            align="center"
            background-color={buttonColor}
          />
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
      <mj-wrapper class="alternate">
        <mj-section>
          <mj-column>
            <mj-text align="center">Events we have worked with:</mj-text>
          </mj-column>
        </mj-section>
        <mj-section>
          <mj-column>
            <ImageThumbnail imageName="events/sygu.jpg" />
            <mj-text>Step Ya Game Up</mj-text>
          </mj-column>
          <mj-column>
            <ImageThumbnail imageName="events/lohh.png" />
            <mj-text>Ladies of Hip-Hop</mj-text>
          </mj-column>
          <mj-column>
            <ImageThumbnail imageName="events/ssl.png" />
            <mj-text>Street Style Lab</mj-text>
          </mj-column>
        </mj-section>
        <mj-section>
          <mj-column>
            <mj-text align="center">Testimonials:</mj-text>
          </mj-column>
        </mj-section>
        <mj-section>
          <mj-column>
            <ImageThumbnail imageName="testimonials/nedric.jpg" />
            <mj-text>
              Looking forward to working with DanceDeets on my next event!
            </mj-text>
            <mj-text>Nedric Johnson (Juste Debout NYC)</mj-text>
          </mj-column>
          <mj-column>
            <ImageThumbnail imageName="testimonials/stretch.jpg" />
            <mj-text>
              I tell dancers to check DanceDeets for events in this scene...
            </mj-text>
            <mj-text>Buddha Stretch (Elite Force, MOPTOP)</mj-text>
          </mj-column>
          <mj-column>
            <ImageThumbnail imageName="testimonials/carlo.jpg" />
            <mj-text>
              More promoters need to start working with DanceDeets!
            </mj-text>
            <mj-text>Carlo C-Lo (Electro Soul, Top Status)</mj-text>
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
    const args = {
      utm_source: 'event_add',
      utm_medium: 'email',
      utm_campaign: 'event_add',
    };
    const shortUrl = `https://dd.events/e/${event.id}`;
    const address = event.venue.address;
    let city = 'your city';
    if (address && address.city) {
      city = `the ${address.city} area`;
    }
    // TODO: Handle 'intro email' different from 'second email'
    return [
      <mj-section class="alternate">
        <mj-column full-width="full-width">
          <mj-image src="https://static.dancedeets.com/img/mail/header-flyers.jpg" />
        </mj-column>
      </mj-section>,
      <mj-section>
        <mj-column full-width="full-width">
          <mj-text>
            <p>Hi there {this.props.organizerName},</p>
            <p>
              We want to help promote your new event and help grow our dance{' '}
              scene:
            </p>
            <p>“{event.name}”</p>
            <p>
              To start, we&#8217;ve added your event to DanceDeets, the{' '}
              world&#8217; s biggest street dance event platform:
            </p>
            <mj-button
              href={shortUrl}
              align="center"
              background-color={buttonColor}
            />

            <p>What does this mean for you?</p>
          </mj-text>

          <mj-table>
            <tr>
              <td>
                <GenericCircle />
              </td>
              <td>
                Your event is now accessible on dancedeets.com and our mobile{' '}
                app, for the 50,000+ dancers that visit us every month. Even if{' '}
                they don&#8217; t use Facebook.
              </td>
            </tr>
            <tr>
              <td>
                <GenericCircle />
              </td>
              <td>
                Easily discoverable by dancers living in {city} (or those just{' '}
                visiting!), as well as new dancers looking to get into the{' '}
                scene.
              </td>
              <td>
                <GenericCircle />
              </td>
              <td>
                We&#8217; ve published information about your event to Google{' '}
                and <a href="https://twitter.com/dancedeets">Twitter</a>, so{' '}
                dancers can find information about your event, no matter where{' '}
                they look.
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
