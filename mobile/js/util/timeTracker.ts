/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { AppState, AppStateStatus, NativeEventSubscription } from 'react-native';
import { trackEnd, trackStart } from '../store/track';

interface TimeTrackerProps {
  eventName: string;
  eventValue: string;
  children: React.ReactNode;
}

export class TimeTracker extends React.Component<TimeTrackerProps> {
  private appStateSubscription: NativeEventSubscription | null = null;

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

  componentDidMount(): void {
    trackStart(this._formatEvent());
    // In RN 0.72+, addEventListener returns a subscription
    this.appStateSubscription = AppState.addEventListener('change', this._handleAppStateChange);
  }

  componentDidUpdate(prevProps: TimeTrackerProps): void {
    if (prevProps.eventValue !== this.props.eventValue) {
      trackEnd(this._formatEvent(prevProps.eventValue));
      trackStart(this._formatEvent());
    }
  }

  componentWillUnmount(): void {
    trackEnd(this._formatEvent()); // Track against old tab
    this.appStateSubscription?.remove();
  }

  render(): React.ReactNode {
    return this.props.children;
  }
}
