/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { injectIntl, intlShape } from 'react-intl';
import { intlWeb } from 'dancedeets-common/js/intl';
import { Event } from 'dancedeets-common/js/events/models';
import { EmailWrapper } from './mailCommon';

class BodyWrapper extends React.Component {
  props: {
    event: Event,
  };

  render() {
    const url = {
      utm_source: 'event_add',
      utm_medium: 'email',
      utm_campaign: 'event_add',
    };
    return (
      <mj-section background-color="#ffffff">
        <mj-column width="100%">
          <mj-text padding="10px 25px">
            <p>Hi there,</p>
            <p>
              I wanted to let you know we've just added your event{' '}
              <a href={url}>{this.props.event.name}</a> to DanceDeets, where our
              worldwide dance community can find the dance events they care
              about. Thanks for organizing and hosting events like this one,
              that build and make up the essence of our dance scene.
            </p>
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
        //TODO: Implement unsubscribe link
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
