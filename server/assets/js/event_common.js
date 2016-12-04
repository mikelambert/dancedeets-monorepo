
import React from 'react';

const choiceStrings = [
  {
    internal: 'attending',
    display: 'attending',
  },
  {
    internal: 'interested',
    display: 'interested',
  },
  {
    internal: 'declined',
    display: 'declined',
  },
];

type RsvpValue = 'attending' | 'interested' | 'declined' | 'none';


export class RsvpComponent extends React.Component {
  props: {
    event: Event;
    userRsvp: RsvpValue;
  }

  render() {
    const id = this.props.event.id;

    const choices = choiceStrings.map(({ internal, display }) => (
      <option
        key={internal}
        value={internal}
        selected={this.props.userRsvp === internal}
      >{display}</option>
    ));
    if (!this.props.userRsvp || this.props.userRsvp === 'none') {
      choices.push(<option key="none" value="" selected>none</option>);
    }

    return (
      <form style={{ margin: '0px', display: 'inline' }} className="form-inline">
        <select
          className="form-control"
          id={`rsvp_${id}`}
          name={`rsvp_${id}`}
          onChange={`
            console.log('hey', event.value);
            $.ajax({
              data: {rsvp: event.value, event_id: ${id}},
              type: 'POST',
              url: '/events/rsvp_ajax',
            });
          `}
        >
          {choices}
        </select>
      </form>
    );
  }
}
