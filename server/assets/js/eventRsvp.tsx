/**
 * Copyright 2016 DanceDeets.
 */

/// <reference path="../../types/window.d.ts" />

import * as React from 'react';
import { MessageDescriptor } from 'react-intl';
import messages from 'dancedeets-common/js/events/messages';
import { Event } from 'dancedeets-common/js/events/models';
import { Message } from './intl';
import fetch from './fetch';
import { fbLoadEmitter } from './fb';

interface ChoiceString {
  internal: RsvpValue;
  messageName: string;
}

const choiceStrings: ChoiceString[] = [
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

interface RsvpComponentProps {
  event: Event;
  userRsvp: RsvpValue;
}

interface RsvpComponentState {
  rsvpValue: RsvpValue;
  updated: boolean;
  disableAll: boolean;
}

class _RsvpComponent extends React.Component<RsvpComponentProps, RsvpComponentState> {
  _choiceBinds: Array<() => Promise<void>>;

  constructor(props: RsvpComponentProps) {
    super(props);
    this.state = {
      rsvpValue: this.props.userRsvp,
      updated: false,
      disableAll: false,
    };
    this._choiceBinds = choiceStrings.map(({ internal }) =>
      this.onChange.bind(this, internal)
    );
    this.loadRsvpsFor = this.loadRsvpsFor.bind(this);
  }

  componentDidMount(): void {
    if (!window.hasCalledFbInit) {
      fbLoadEmitter.on('fb-load', () => {
        this.componentDidMount();
      });
      return;
    }
    console.log('RsvpComponent.componentDidMount Running', window.FB);
    window.FB?.getLoginStatus(response => {
      console.log('getLoginStatus returned ', response.status);
      if (response.status === 'connected' && response.authResponse) {
        this.loadRsvpsFor(response.authResponse.userID);
      }
    });
  }

  async onChange(rsvpValue: RsvpValue): Promise<void> {
    if (this.state.rsvpValue === rsvpValue) {
      return;
    }
    try {
      fetch('/events/rsvp_ajax', {
        rsvp: rsvpValue,
        event_id: this.props.event.id,
      });
      this.setState({
        rsvpValue,
        updated: true,
      });
    } catch (e) {
      const error = e as Error;
      console.error(e);
      console.error(`Error on rsvp_ajax: ${error.message}: ${error.stack}`);
    }
  }

  disableAll(): void {
    if (!this.state.disableAll) {
      this.setState({ disableAll: true });
    }
  }

  async loadRsvpsFor(userId: string): Promise<void> {
    choiceStrings.forEach(({ internal }) => {
      (window.FB as any)?.api(
        `/${this.props.event.id}/${internal}/${userId}`,
        'get',
        {},
        (response: { error?: unknown; data: unknown[] }) => {
          if (response.error) {
            // Disable all buttons since we don't have permission to RSVP
            this.disableAll();
            return;
          }
          if (response.data.length) {
            if (!this.state.updated) {
              this.setState({ rsvpValue: internal });
            }
          }
        }
      );
    });
  }

  render(): React.ReactNode {
    const { id } = this.props.event;

    const buttons = choiceStrings.map(({ internal, messageName }, index) => {
      const activeClass =
        this.state.rsvpValue === internal ? 'active btn-no-focus' : '';
      return (
        <button
          key={internal}
          type="button"
          className={`btn btn-default ${activeClass}`}
          id={`rsvp_${id}_${internal}`}
          value={internal}
          disabled={this.state.disableAll}
          onClick={this._choiceBinds[index]}
        >
          <Message message={(messages as Record<string, MessageDescriptor>)[messageName]} />
        </button>
      );
    });
    return (
      <form
        style={{ margin: '0px', display: 'inline' }}
        className="form-inline"
      >
        <div className="btn-group" role="group" aria-label="RSVPs">
          {buttons}
        </div>
      </form>
    );
  }
}
export const RsvpComponent = _RsvpComponent;
