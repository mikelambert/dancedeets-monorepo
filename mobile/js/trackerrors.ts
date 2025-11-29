/**
 * Copyright 2016 DanceDeets.
 *
 * Error tracking initialization - @sentry/react-native v5
 */

import trackjs from 'react-native-trackjs';
import crashlyticsReporter from 'react-native-fabric-crashlytics';
import * as Sentry from '@sentry/react-native';

export default function init(): void {
  if (__DEV__) {
    // Don't send exceptions from __DEV__, it's way too noisy!
    // Live reloading and hot reloading in particular lead to tons of noise...
    return;
  }

  // Initialize Sentry with the new v5 API
  Sentry.init({
    dsn: 'https://56b58e9bc5c44335ab7ef39a1f85d1aa:5d0631b36af0489fab9eae00b9953e4f@sentry.io/106536',
    // Enable automatic performance monitoring
    tracesSampleRate: 1.0,
    // Enable native crash reporting
    enableNativeCrashHandling: true,
  });

  trackjs.init({
    token: '77a8a7079d734df7a94150f8f0d7e16f',
    application: 'react-native',
  });
  crashlyticsReporter.init();
}
