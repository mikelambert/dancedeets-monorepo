
import $ from 'jquery';
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

export type RsvpValue = 'attending' | 'maybe' | 'declined' | 'none';


export class RsvpComponent extends React.Component {
  props: {
    event: Event;
    userRsvp: RsvpValue;
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

    const choices = choiceStrings.map(({ internal, display }) => (
      <option
        key={internal}
        value={internal}
      >{display}</option>
    ));
    if (!this.props.userRsvp) {
      choices.push(<option key="none" value="">none</option>);
    }

    return (
      <form style={{ margin: '0px', display: 'inline' }} className="form-inline">
        <select
          className="form-control"
          id={`rsvp_${id}`}
          name={`rsvp_${id}`}
          onChange={this.onChange}
          defaultValue={this.props.userRsvp}
        >
          {choices}
        </select>
      </form>
    );
  }
}
