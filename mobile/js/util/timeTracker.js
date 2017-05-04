/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { AppState } from 'react-native';
import { trackEnd, trackStart } from '../store/track';

type TimeTrackerProps = {
  eventName: string,
  eventValue: string,
};

export class TimeTracker extends React.Component {
  props: TimeTrackerProps & {
    children?: React.Element<*>,
  };

  constructor(props: TimeTrackerProps) {
    super(props);
    (this: any)._handleAppStateChange = this._handleAppStateChange.bind(this);
  }

  componentWillMount() {
    trackStart(this._formatEvent());
    AppState.addEventListener('change', this._handleAppStateChange);
  }

  componentWillReceiveProps(nextProps: TimeTrackerProps) {
    if (this.props.eventValue != nextProps.eventValue) {
      trackEnd(this._formatEvent()); // Can't use track properties()
      trackStart(this._formatEvent(nextProps.eventValue));
    }
  }

  componentWillUnmount() {
    trackEnd(this._formatEvent()); // Track against old tab
    AppState.removeEventListener('change', this._handleAppStateChange);
  }

  _formatEvent(value: ?string = null) {
    const trackValue = value || this.props.eventValue;
    return `${this.props.eventName}: ${trackValue}`;
  }

  _handleAppStateChange(currentAppState) {
    if (currentAppState === 'active') {
      trackStart(this._formatEvent());
    }
    if (currentAppState === 'inactive') {
      trackEnd(this._formatEvent());
    }
  }

  render() {
    return this.props.children;
  }
}
