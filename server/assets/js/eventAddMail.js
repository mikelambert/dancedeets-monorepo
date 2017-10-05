/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { intlWeb } from 'dancedeets-common/js/intl';
import { Event } from 'dancedeets-common/js/events/models';
import { addUrlArgs } from 'dancedeets-common/js/util/url';
import { EmailWrapper } from './mailCommon';

class BodyWrapper extends React.Component {
  props: {
    event: Event,
  };

  render() {
    const event = this.props.event;
    const args = {
      utm_source: 'event_add',
      utm_medium: 'email',
      utm_campaign: 'event_add',
    };
    const url = event.getUrl(args);
    const shortUrl = `https://dd.events/e/${event.id}`;
    const address = event.venue.address;
    let city = 'your city';
    if (address && address.city) {
      city = `the ${address.city} area`;
    }
    // TODO: Handle 'intro email' different from 'second email'
    return (
      <mj-section background-color="#ffffff">
        <mj-column width="100%">
          <mj-text padding="10px 25px">
            <p>Hi there,</p>
            <p>
              I wanted to let you know we&#39;ve just added your event{' '}
              <a href={url}>{event.name}</a> to DanceDeets, where our worldwide
              dance community finds the dance events they care about.
            </p>
            <p>
              Thank you for organizing and hosting events like this one, that
              build and make up the essence of our dance scene. In return,
              we&#39;ll do our part to spread the word to dancers everywhere:
            </p>
            <ul>
              <li>
                Your event is now listed on {' '}
                <a href={addUrlArgs('https://www.dancedeets.com', args)}>
                  dancedeets.com
                </a>{' '}
                and our{' '}
                <a
                  href={addUrlArgs(
                    'https://www.dancedeets.com/mobile_apps',
                    args
                  )}
                >
                  mobile app
                </a>{' '}
                for the 40,000+ dancers that visit every month. Even if they
                done&#39;t have Facebook.
              </li>
              <li>
                Easily discoverable by dancers visiting {city}, as well as new
                dancers looking to join your scene.
              </li>
              <li>
                We&#39;ve published information about your event to Google and
                <a href="https://twitter.com/dancedeets">Twitter</a>, so dancers
                can find information about your event, no matter where they
                look.
              </li>
              <li>
                If you need a convenient URL to share with folks, you can use{' '}
                <a href={shortUrl}>shortUrl</a>, which can be viewed even by
                those friends who refuse to use Facebook.
              </li>
            </ul>
            <hr />
            <p>
              But we still want to make things better! Let us know which of the
              following will help you most!
            </p>
            <ul>
              <li>
                If you want us to tell you about common mistakes and ways to
                improve your event and event description, click here.
              </li>
              <li>
                If you want us to push and promote your event to an even larger
                audience outside of {city}, click here.
              </li>
              <li>
                If you want to be able to force-refresh the event information
                from Facebook anytime you make changes, click here.
              </li>
              <li>
                If you want to control the keywords we list your event as
                (currently {event.annotations.categories.join(', ')}), click
                here.
              </li>
              <li>
                If you want to set a special video trailer (or
                soundcloud/mixcloud link!) for your event, click here.
              </li>
              <li>
                If you want to set a specific contact email address for your
                events (other than {event.getContactEmails().join(', ')}), click
                here.
              </li>
            </ul>
          </mj-text>
        </mj-column>
      </mj-section>
    );
  }
}

class AddEventEmail extends React.Component {
  props: {
    event: Event,
  };

  render() {
    const title = this.props.event.name;
    return (
      <EmailWrapper
        header={`We've added your event: ${title}`}
        // TODO: Implement unsubscribe link
        footer={
          <div>
            You may also{' '}
            <a href="*|UNSUB:https://www.dancedeets.com/user/unsubscribe|*">
              unsubscribe
            </a>{' '}
            from these event notification emails.
          </div>
        }
      >
        <BodyWrapper />
      </EmailWrapper>
    );
  }
}

export default intlWeb(AddEventEmail);
