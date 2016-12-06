
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

  state: {
    rsvpValue: RsvpValue;
  }

  constructor(props) {
    super(props);
    this.state = { rsvpValue: this.props.userRsvp };
  }

  onChange(rsvpValue, changeEvent) {
    $.ajax({
      type: 'POST',
      url: '/events/rsvp_ajax',
      data: {
        rsvp: rsvpValue,
        event_id: this.props.event.id,
      },
    });
    this.setState({ rsvpValue });
  }

  render() {
    const id = this.props.event.id;

    const buttons = choiceStrings.map(({ internal, messageName }) => (
      <button
        type="button"
        className={`btn btn-default ${this.state.rsvpValue === internal ? 'active' : ''}`}
        id={`rsvp_${id}_${internal}`}
        value={internal}
        onClick={this.onChange.bind(this, internal)}
      >
        <FormattedMessage id={messages[messageName].id} />
      </button>
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
