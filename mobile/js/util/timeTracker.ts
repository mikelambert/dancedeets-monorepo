/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { trackEnd, trackStart } from '../store/track';

interface TimeTrackerProps {
  eventName: string;
  eventValue: string;
  children: React.ReactNode;
}

export class TimeTracker extends React.Component<TimeTrackerProps> {
  _formatEvent(value: string | null = null): string {
    const trackValue = value || this.props.eventValue;
    return `${this.props.eventName}: ${trackValue}`;
  }

  _handleAppStateChange = (currentAppState: AppStateStatus): void => {
    if (currentAppState === 'active') {
      trackStart(this._formatEvent());
    }
    if (currentAppState === 'inactive') {
      trackEnd(this._formatEvent());
    }
  }

  componentWillMount(): void {
    trackStart(this._formatEvent());
    AppState.addEventListener('change', this._handleAppStateChange);
  }

  componentWillReceiveProps(nextProps: TimeTrackerProps): void {
    if (this.props.eventValue !== nextProps.eventValue) {
      trackEnd(this._formatEvent()); // Can't use track properties()
      trackStart(this._formatEvent(nextProps.eventValue));
    }
  }

  componentWillUnmount(): void {
    trackEnd(this._formatEvent()); // Track against old tab
    AppState.removeEventListener('change', this._handleAppStateChange);
  }

  render(): React.ReactNode {
    return this.props.children;
  }
}
