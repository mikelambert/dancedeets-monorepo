
import $ from 'jquery';
import React from 'react';
import {
  injectIntl,
  intlShape,
  FormattedMessage,
} from 'react-intl';
import { messages } from 'dancedeets-common/js/events/messages';

const choiceStrings = [
  {
    internal: 'attending',
    messageName: 'attending',
  },
  {
    internal: 'maybe',
    messageName: 'maybe',
  },
  {
    internal: 'declined',
    messageName: 'declined',
  },
];

export type RsvpValue = 'attending' | 'maybe' | 'declined' | 'none';


class _RsvpComponent extends React.Component {
  props: {
    event: Event;
    userRsvp: RsvpValue;

    // Self-managed props
    intl: intlShape;
  }

  constructor(props) {
    super(props);
    (this: any).onChange = this.onChange.bind(this);
  }

  onChange(changeEvent) {
    $.ajax({
      type: 'POST',
      url: '/events/rsvp_ajax',
      data: {
        rsvp: changeEvent.target.value,
        event_id: this.props.event.id,
      },
    });
  }

  render() {
    const id = this.props.event.id;

    const choices = choiceStrings.map(({ internal, messageName }) => (
      <option
        key={internal}
        value={internal}
      >{this.props.intl.formatMessage(messages[messageName])}</option>
    ));

    const buttons = choiceStrings.map(({ internal, messageName }) => (
      <button
        key={`rsvp_${id}_${messageName}`}
        name={`rsvp_${id}`}
        type="button"
        className={`btn btn-default ${internal === this.props.userRsvp ? 'active' : ''}`}
        value={internal}
        onClick={this.onChange}
      ><FormattedMessage id={messages[messageName].id} /></button>
    ));
    return (
      <form style={{ margin: '0px', display: 'inline' }} className="form-inline">
        <div className="btn-group" role="group" aria-label="RSVPs">
          {buttons}
        </div>
      </form>
    );
  }
}
export const RsvpComponent = injectIntl(_RsvpComponent);
